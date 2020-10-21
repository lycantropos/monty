#!/usr/bin/env python3
"""Python project generator."""
import calendar
import io
import os
import posixpath
import shutil
import sys
from datetime import datetime
from functools import partial
from itertools import (filterfalse,
                       tee)
from pathlib import Path
from typing import (Any,
                    Callable,
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
from jinja2 import Template
from strictyaml import (Map,
                        Regex,
                        Str,
                        load)
from strictyaml.yamllocation import YAMLChunk

__version__ = '1.0.1'


class NonEmptySingleLineStr(Str):
    def validate_scalar(self, chunk: YAMLChunk) -> str:
        contents = chunk.contents
        if not contents:
            chunk.expecting_but_found('when expecting non-empty string',
                                      contents)
        elif len(contents.splitlines()) > 1:
            chunk.expecting_but_found('when expecting single-line string',
                                      contents)
        return contents


class LicenseClassifier(Str):
    def validate_scalar(self, chunk: YAMLChunk) -> str:
        contents = chunk.contents
        if contents not in load_licenses_classifiers():
            chunk.expecting_but_found('when expecting '
                                      'license Trove classifier',
                                      contents)
        return contents


version_pattern = r'\d+\.\d+(\.\d+)?'
settings_schema = Map({
    'azure_login': Str(),
    'description': NonEmptySingleLineStr(),
    'dockerhub_login': Str(),
    'email': Str(),
    'github_login': Str(),
    'license_classifier': LicenseClassifier(),
    'project': Regex(r'\w+([\.-]\w+)*'),
    'version': Regex(version_pattern),
    'min_python_version': Regex(version_pattern),
    'max_python_version': Regex(version_pattern),
})


@click.command()
@click.option('--version', '-v',
              is_flag=True,
              help='Displays script version information and exits.')
@click.option('--settings-path', '-s',
              default='settings.yml',
              help='Path (absolute or relative) to settings '
                   '(defaults to "settings.yml").')
@click.option('--template-dir',
              default='template',
              help='Path (absolute or relative) to template project.')
@click.option('--template-repo',
              default=None,
              help='Github repository in format `owner name/repository name` '
                   'with template.')
@click.option('--output-dir', '-o',
              default='.',
              help='Path (absolute or relative) to output directory '
                   '(defaults to current working directory).')
@click.option('--overwrite',
              is_flag=True,
              help='Overwrites files if output directory exists.')
@click.option('--github-access-token', '-g',
              default=None,
              help='Personal access token '
                   'that can be used to access the GitHub API.')
def main(version: bool,
         settings_path: str,
         template_dir: str,
         template_repo: Optional[str],
         output_dir: str,
         overwrite: bool,
         github_access_token: Optional[str]) -> None:
    """Generates project from template."""
    if version:
        sys.stdout.write(__version__)
        return
    template_dir = os.path.normpath(template_dir)
    if template_repo is not None:
        template_dir = os.path.join(template_dir, template_repo)
        latest_commit_info, = (requests.get('https://api.github.com/repos/{}'
                                            '/commits?per_page=1'
                                            .format(template_repo)).json())
        latest_commit_datetime_string = (
            latest_commit_info['commit']['committer']['date'])
        latest_commit_timestamp = calendar.timegm(
                datetime.strptime(latest_commit_datetime_string,
                                  '%Y-%m-%dT%H:%M:%SZ').utctimetuple())
        os.makedirs(template_dir,
                    exist_ok=True)
        previous_versions_paths = os.listdir(template_dir)
        template_dir = os.path.join(template_dir, str(latest_commit_timestamp))
        if previous_versions_paths:
            previous_version_path, = previous_versions_paths
            previous_version_timestamp = int(
                    os.path.basename(previous_version_path))
            if previous_version_timestamp < latest_commit_timestamp:
                shutil.rmtree(previous_version_path)
                load_github_repository(template_repo, template_dir)
        else:
            load_github_repository(template_repo, template_dir)
    output_dir = os.path.normpath(output_dir)
    os.makedirs(output_dir,
                exist_ok=True)
    settings = (load(Path(settings_path).read_text(encoding='utf-8'),
                     schema=settings_schema)
                .data)
    license_classifier = settings['license_classifier']
    _, settings['license'] = license_classifier.rsplit(' :: ', 1)
    dockerhub_login = settings['dockerhub_login']
    github_login = settings['github_login']
    dockerhub_user = load_dockerhub_user(dockerhub_login)
    github_user = load_github_user(github_login,
                                   access_token=github_access_token)
    settings.setdefault('full_name',
                        github_user['name'] or dockerhub_user['full_name'])
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
                     base_url='https://api.github.com',
                     access_token: Optional[str] = None) -> Dict[str, Any]:
    users_method_url = partial(api_method_url,
                               'users')
    headers = (None
               if access_token is None
               else {'Authorization': 'token {}'.format(access_token)})
    response = load_user(login=login,
                         base_url=base_url,
                         version='',
                         users_method_url=users_method_url,
                         headers=headers)
    user = response.json()
    try:
        error_message = user['message']
    except KeyError:
        return user
    else:
        raise ValueError(error_message)


def load_licenses_classifiers(*,
                              url: str = 'https://pypi.org/pypi?%3A'
                                         'action=list_classifiers',
                              license_classifier_prefix: str = 'License :: '
                              ) -> List[str]:
    with requests.get(url,
                      stream=True) as response:
        return [line
                for line in response.iter_lines(decode_unicode=True)
                if line.startswith(license_classifier_prefix)]


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
    return Template(source,
                    keep_trailing_newline=True,
                    trim_blocks=True).render(**settings)


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
