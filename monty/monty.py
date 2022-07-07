#!/usr/bin/env python3
"""Python project generator."""
import calendar
import io
import os
import posixpath
import shutil
import sys
import warnings
from datetime import datetime
from functools import partial
from itertools import (filterfalse,
                       tee)
from pathlib import Path
from typing import (Any,
                    Callable,
                    Container,
                    Dict,
                    Iterable,
                    Iterator,
                    List,
                    Optional,
                    Tuple,
                    cast)
from zipfile import ZipFile

import click
import requests
from jinja2 import (StrictUndefined,
                    Template)
from strictyaml import (Map,
                        MapPattern,
                        Optional as OptionalKey,
                        Regex,
                        Str,
                        load)
from strictyaml.yamllocation import YAMLChunk

__version__ = '3.0.0'
FULL_NAME_KEY = 'full_name'
GITHUB_API_ENDPOINT = 'https://api.github.com'
TROVE_LICENSE_CLASSIFIER_KEY = 'trove_license_classifier'
TROVE_CLASSIFIER_SEPARATOR = ' :: '
VERSION_PATTERN = r'\d+\.\d+(\.\d+)?(-(alpha|beta))?'


class NonEmptySingleLineStr(Str):
    def validate_scalar(self, chunk: YAMLChunk) -> str:
        contents = (chunk.contents
                    if isinstance(chunk.contents, str)
                    else chunk.contents.value)
        if not contents:
            chunk.expecting_but_found('when expecting non-empty string',
                                      contents)
        elif len(contents.splitlines()) > 1:
            chunk.expecting_but_found('when expecting single-line string',
                                      contents)
        return contents


class SpdxLicenseIdentifier(Str):
    def __init__(self, identifiers: Container[str]) -> None:
        self.identifiers = identifiers

    def validate_scalar(self, chunk: YAMLChunk) -> Dict[str, Any]:
        contents = chunk.contents
        if contents not in self.identifiers:
            chunk.expecting_but_found('when expecting SPDX license identifier',
                                      contents)
        return contents


class TroveLicenseClassifier(Str):
    def __init__(self, identifiers: Container[str]) -> None:
        self.classifiers = identifiers

    def validate_scalar(self, chunk: YAMLChunk) -> str:
        contents = chunk.contents
        if contents not in self.classifiers:
            chunk.expecting_but_found('when expecting '
                                      'license Trove classifier',
                                      contents)
        return contents


@click.command()
@click.option('--version', '-v',
              is_flag=True,
              help='Displays script version information and exits.')
@click.option('--settings-path', '-s',
              default='settings.yml',
              help='Path (absolute or relative) to settings '
                   '(defaults to "settings.yml").')
@click.option('--templates-dir',
              default='.templates',
              help='Path (absolute or relative) to templates.')
@click.option('--output-dir', '-o',
              default='.',
              help='Path (absolute or relative) to output directory '
                   '(defaults to current working directory).')
@click.option('--overwrite',
              is_flag=True,
              help='Overwrites files if output directory exists.')
@click.option('--github-access-token', '-g',
              envvar='GITHUB_ACCESS_TOKEN',
              default=None,
              help='Personal access token '
                   'that can be used to access the GitHub API.')
@click.argument('template-repo')
def main(version: bool,
         settings_path: str,
         templates_dir: str,
         output_dir: str,
         overwrite: bool,
         github_access_token: Optional[str],
         template_repo: str) -> None:
    """Generates project from template."""
    if version:
        sys.stdout.write(__version__)
        return
    templates_dir = os.path.normpath(templates_dir)
    template_dir = sync_template(templates_dir, template_repo,
                                 github_access_token)
    output_dir = os.path.normpath(output_dir)
    os.makedirs(output_dir,
                exist_ok=True)
    settings = load_settings(settings_path, github_access_token)
    non_binary_files_paths = filterfalse(is_binary_file,
                                         files_paths(template_dir))
    renderer = cast(Callable[[str], str], partial(render,
                                                  settings=settings))
    paths_pairs = replace_files_paths(non_binary_files_paths,
                                      source_path=template_dir,
                                      destination=output_dir,
                                      renderer=renderer)
    for file_path, new_file_path in paths_pairs:
        if not overwrite and os.path.exists(new_file_path):
            raise click.BadOptionUsage('overwrite',
                                       'Trying to overwrite "{path}", '
                                       'but no "--overwrite" flag was set.'
                                       .format(path=new_file_path))
        render_file(file_path, new_file_path,
                    renderer=renderer)


def sync_template(templates_path: str, repository_path: str,
                  github_access_token: Optional[str]) -> str:
    base_template_dir = os.path.join(templates_path, repository_path)
    latest_commits_info = requests.get(
            GITHUB_API_ENDPOINT
            + '/repos/{}/commits?per_page=1'.format(repository_path),
            headers=_to_github_headers(github_access_token)).json()
    _validate_github_response(latest_commits_info)
    latest_commit_info, = latest_commits_info
    latest_commit_datetime_string = (
        latest_commit_info['commit']['committer']['date'])
    latest_commit_timestamp = calendar.timegm(
            datetime.strptime(latest_commit_datetime_string,
                              '%Y-%m-%dT%H:%M:%SZ').utctimetuple())
    os.makedirs(base_template_dir,
                exist_ok=True)
    template_dir = os.path.join(base_template_dir,
                                str(latest_commit_timestamp))
    try:
        previous_timestamp_string, = os.listdir(base_template_dir)
    except ValueError:
        load_github_repository(repository_path, template_dir)
    else:
        previous_timestamp = int(previous_timestamp_string)
        if previous_timestamp < latest_commit_timestamp:
            shutil.rmtree(os.path.join(base_template_dir,
                                       previous_timestamp_string))
            load_github_repository(repository_path, template_dir)
    return template_dir


def load_settings(settings_path: str,
                  github_access_token: Optional[str]) -> Dict[str, str]:
    spdx_licenses_info = load_spdx_licenses_info()
    trove_licenses_classifiers = load_trove_licenses_classifiers()
    settings_schema = Map({
        'description': NonEmptySingleLineStr(),
        'dockerhub_login': NonEmptySingleLineStr(),
        'email': NonEmptySingleLineStr(),
        'github_login': NonEmptySingleLineStr(),
        'project': Regex(r'\w+([\.-]\w+)*'),
        'spdx_license_identifier': SpdxLicenseIdentifier(
                spdx_licenses_info.keys()
        ),
        'version': Regex(VERSION_PATTERN),
        OptionalKey(FULL_NAME_KEY): NonEmptySingleLineStr(),
        OptionalKey('max_version_of'): MapPattern(NonEmptySingleLineStr(),
                                                  Regex(VERSION_PATTERN)),
        OptionalKey('min_version_of'): MapPattern(NonEmptySingleLineStr(),
                                                  Regex(VERSION_PATTERN)),
        OptionalKey(TROVE_LICENSE_CLASSIFIER_KEY): TroveLicenseClassifier(
                trove_licenses_classifiers
        ),
    })
    settings = (load(Path(settings_path).read_text(encoding='utf-8'),
                     schema=settings_schema)
                .data)
    spdx_license_info = spdx_licenses_info[settings['spdx_license_identifier']]
    spdx_license_name = spdx_license_info['name']
    if spdx_license_info['is_deprecated']:
        warnings.warn('License "{name}" is marked as deprecated by SPDX.'
                      .format(name=spdx_license_name),
                      DeprecationWarning)
    settings['spdx_license_name'] = spdx_license_name
    if TROVE_LICENSE_CLASSIFIER_KEY not in settings:
        osi_approved = spdx_license_info['osi_approved']
        candidates = [classifier
                      for classifier in trove_licenses_classifiers
                      if ((spdx_license_name
                           in classifier.rsplit(TROVE_CLASSIFIER_SEPARATOR,
                                                maxsplit=1)[1])
                          and (('OSI Approved'
                                == classifier.split(TROVE_CLASSIFIER_SEPARATOR,
                                                    maxsplit=2)[1])
                               if osi_approved
                               else
                               ('OSI Approved'
                                != classifier.split(TROVE_CLASSIFIER_SEPARATOR,
                                                    maxsplit=2)[1])))]
        try:
            trove_license_classifier, = candidates
        except ValueError:
            if not candidates:
                warnings.warn('No Trove classifier found '
                              'for license "{name}", '
                              'in case of need specify it explicitly '
                              'with "{key}" key in settings.'
                              .format(name=spdx_license_name,
                                      key=TROVE_LICENSE_CLASSIFIER_KEY),
                              UserWarning)
            else:
                warnings.warn('Found {count} conflicting Trove classifiers '
                              'for license "{name}", '
                              'in case of need specify it explicitly '
                              'with "{key}" key in settings.'
                              .format(count=len(candidates),
                                      name=spdx_license_name,
                                      key=TROVE_LICENSE_CLASSIFIER_KEY),
                              UserWarning)
        else:
            settings[TROVE_LICENSE_CLASSIFIER_KEY] = trove_license_classifier
    dockerhub_login = settings['dockerhub_login']
    github_login = settings['github_login']
    if FULL_NAME_KEY not in settings:
        settings[FULL_NAME_KEY] = (
                load_github_user(github_login,
                                 access_token=github_access_token)['name']
                or load_dockerhub_user(dockerhub_login)['full_name']
        )
    return settings


def api_method_url(method: str,
                   *,
                   base_url: str,
                   version: str) -> str:
    return urljoin(base_url, version, method)


def files_paths(path: str) -> Iterator[str]:
    for root, _, files_names in os.walk(path):
        for file_name in files_names:
            yield os.path.join(root, file_name)


def is_binary_file(path: str) -> bool:
    with open(path, mode='rb') as file:
        return is_binary_string(file.read(1024))


def is_binary_string(bytes_string: bytes,
                     *,
                     translation_table: bytes = bytes({7, 8, 9, 10, 12, 13, 27}
                                                      | set(range(0x20, 0x100))
                                                      - {0x7f})) -> bool:
    return bool(bytes_string.translate(None, translation_table))


def load_dockerhub_user(login: str,
                        *,
                        base_url: str = 'https://hub.docker.com',
                        version: str = 'v2') -> Dict[str, Any]:
    users_method_url = partial(api_method_url,
                               'users')
    response = load_user(login=login,
                         base_url=base_url,
                         version=version,
                         users_method_url=users_method_url)
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        error_message = ('Invalid login: "{login}". '
                         'Not found via API request to "{url}".'
                         .format(login=login,
                                 url=response.url))
        raise ValueError(error_message) from error
    else:
        return response.json()


def load_github_repository(name: str, destination_path: str) -> None:
    archive_url = 'https://github.com/{}/archive/master.zip'.format(name)
    archive_bytes_stream = io.BytesIO(requests.get(archive_url).content)
    with ZipFile(archive_bytes_stream) as zip_file:
        for resource_info in zip_file.infolist():
            is_directory = resource_info.filename[-1] == '/'
            if is_directory:
                continue
            top_level_directory_name = Path(resource_info.filename).parts[0]
            resource_info.filename = os.path.relpath(resource_info.filename,
                                                     top_level_directory_name)
            zip_file.extract(resource_info, destination_path)


def load_github_user(login: str,
                     *,
                     base_url: str = GITHUB_API_ENDPOINT,
                     access_token: Optional[str] = None) -> Dict[str, Any]:
    users_method_url = partial(api_method_url,
                               'users')
    response = load_user(login=login,
                         base_url=base_url,
                         version='',
                         users_method_url=users_method_url,
                         headers=_to_github_headers(access_token))
    user = response.json()
    _validate_github_response(user)
    return user


def load_spdx_licenses_info(json_url: str = 'https://raw.githubusercontent.com'
                                            '/spdx/license-list-data/master'
                                            '/json/licenses.json'
                            ) -> Dict[str, Any]:
    response = requests.get(json_url)
    response.raise_for_status()
    raw_licenses = response.json()['licenses']
    result = {
        raw_license['licenseId']: {
            'name': raw_license['name'],
            'is_deprecated': raw_license['isDeprecatedLicenseId'],
            'osi_approved': raw_license['isOsiApproved'],
        }
        for raw_license in raw_licenses
    }
    assert len(result) == len(raw_licenses), (
        'License identifiers should be unique'
    )
    return result


def load_trove_licenses_classifiers(
        *,
        url: str = 'https://pypi.org/pypi?%3Aaction=list_classifiers',
) -> List[str]:
    with requests.get(url,
                      stream=True) as response:
        return [line
                for line in response.iter_lines(decode_unicode=True)
                if (line.split(TROVE_CLASSIFIER_SEPARATOR,
                               maxsplit=1)[0]
                    == 'License')]


def _to_github_headers(access_token: Optional[str]
                       ) -> Optional[Dict[str, str]]:
    return (None
            if access_token is None
            else {'Authorization': 'token {}'.format(access_token)})


def _validate_github_response(response: Any) -> None:
    if isinstance(response, dict) and 'message' in response:
        raise ValueError(response['message'])


def load_user(login: str,
              *,
              base_url: str,
              version: str,
              users_method_url: Callable[..., str],
              headers: Optional[Dict[str, str]] = None) -> requests.Response:
    users_url = users_method_url(base_url=base_url,
                                 version=version)
    user_url = urljoin(users_url, login)
    session = requests.Session()
    if headers is not None:
        session.headers.update(headers)
    with session as session:
        return session.get(user_url)


def render(source: str, settings: Dict[str, str]) -> str:
    return (Template(source,
                     keep_trailing_newline=True,
                     trim_blocks=True,
                     undefined=StrictUndefined)
            .render(**settings))


def render_file(source_path: str,
                destination_path: str,
                *,
                encoding: str = 'utf-8',
                renderer: Callable[[str], str]) -> None:
    os.makedirs(os.path.dirname(destination_path),
                exist_ok=True)
    Path(destination_path).write_text(renderer(Path(source_path)
                                               .read_text(encoding=encoding)),
                                      encoding=encoding)
    shutil.copymode(source_path, destination_path)


def render_path_parts(*path_parts: str,
                      renderer: Callable[[str], str]) -> Iterator[str]:
    for path in path_parts:
        yield renderer(path)


def replace_files_paths(paths: Iterable[str],
                        *,
                        source_path: str,
                        destination: str,
                        renderer: Callable[[str], str]
                        ) -> Iterator[Tuple[str, str]]:
    def replace_file_path(file_path: str) -> str:
        root, file_name = os.path.split(file_path)
        new_file_name = renderer(file_name)
        new_root_parts = Path(root.replace(source_path, destination)).parts
        new_root = str(Path(*map(renderer, new_root_parts)))
        return os.path.join(new_root, new_file_name)

    original_paths, source_paths = tee(paths)
    yield from zip(original_paths, map(replace_file_path, source_paths))


urljoin = posixpath.join

if __name__ == '__main__':
    main()
