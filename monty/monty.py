#!/usr/bin/env python3
"""Python project generator."""
import os
import posixpath
import re
import shutil
import sys
from functools import (partial,
                       reduce)
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
                    Tuple)

import click
import requests
from strictyaml import (Map,
                        Str,
                        load)
from strictyaml.yamllocation import YAMLChunk

__version__ = '0.2.1'

TRANSLATION_TABLE = bytes({7, 8, 9, 10, 12, 13, 27}
                          | set(range(0x20, 0x100))
                          - {0x7f})

urljoin = posixpath.join


def api_method_url(method: str,
                   *,
                   base_url: str,
                   version: str) -> str:
    return urljoin(base_url, version, method)


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
              **params: Any) -> requests.Response:
    users_url = users_method_url(base_url=base_url,
                                 version=version)
    user_url = urljoin(users_url, login)

    with requests.Session() as session:
        return session.get(user_url,
                           params=params)


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


def load_github_user(login: str,
                     *,
                     base_url='https://api.github.com',
                     access_token: str = None) -> Dict[str, Any]:
    users_method_url = partial(api_method_url,
                               'users')
    params = {}
    if access_token is not None:
        params['access_token'] = access_token
    response = load_user(login=login,
                         base_url=base_url,
                         version='',
                         users_method_url=users_method_url,
                         **params)
    user = response.json()
    try:
        error_message = user['message']
    except KeyError:
        return user
    else:
        raise ValueError(error_message)


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


settings_schema = Map({
    'azure_login': Str(),
    'description': NonEmptySingleLineStr(),
    'dockerhub_login': Str(),
    'email': Str(),
    'github_login': Str(),
    'license_classifier': LicenseClassifier(),
    'project': Str(),
    'version': Str(),
})


@click.command()
@click.option('--version', '-v',
              is_flag=True,
              help='Displays script version information and exits.')
@click.option('--settings-path', '-s',
              default='settings.yml',
              help='Path (absolute or relative) to settings '
                   '(defaults to "settings.yml").')
@click.option('--template-dir', '-t',
              default='template',
              help='Path (absolute or relative) to template project '
                   '(defaults to "template").')
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
         output_dir: str,
         overwrite: bool,
         github_access_token: Optional[str]) -> None:
    """Generates project from template."""
    if version:
        sys.stdout.write(__version__)
        return

    template_dir = os.path.normpath(template_dir)
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
    replacements = {'_{}_'.format(key): value
                    for key, value in settings.items()}
    non_binary_files_paths = filterfalse(is_binary_file,
                                         files_paths(template_dir))
    paths_pairs = replace_files_paths(non_binary_files_paths,
                                      src=template_dir,
                                      dst=output_dir,
                                      replacements=replacements)
    for file_path, new_file_path in paths_pairs:
        if not overwrite and os.path.exists(new_file_path):
            error_message = ('Trying to overwrite '
                             'existing file "{path}", '
                             'but no "--overwrite" flag was set.'
                             .format(path=new_file_path))
            raise click.BadOptionUsage('overwrite', error_message)
        replacers = [partial(re.compile(r'\b{}\b'.format(origin)).sub,
                             replacement)
                     for origin, replacement in replacements.items()]
        rewrite_file(file_path, new_file_path,
                     replacers=replacers)


def rewrite_file(src_file_path: str,
                 dst_file_path: str,
                 *,
                 replacers: List[Callable[[str], str]]) -> None:
    with open(src_file_path,
              encoding='utf-8') as file:
        new_lines = list(replace_lines(file,
                                       replacers=replacers))
    directory_path = os.path.dirname(dst_file_path)
    os.makedirs(directory_path,
                exist_ok=True)
    with open(dst_file_path,
              mode='w',
              encoding='utf-8') as new_file:
        new_file.writelines(new_lines)
    shutil.copymode(src_file_path, dst_file_path)


def is_binary_file(path: str) -> bool:
    with open(path, mode='rb') as file:
        return is_binary_string(file.read(1024))


def is_binary_string(bytes_string: bytes,
                     *,
                     translation_table: bytes = TRANSLATION_TABLE) -> bool:
    return bool(bytes_string.translate(None, translation_table))


def files_paths(path: str) -> Iterator[str]:
    for root, _, files_names in os.walk(path):
        for file_name in files_names:
            yield os.path.join(root, file_name)


def replace_files_paths(paths: Iterable[str],
                        *,
                        src: str,
                        dst: str,
                        replacements: Dict[str, str]
                        ) -> Iterator[Tuple[str, str]]:
    def replace_file_path(file_path: str) -> str:
        root, file_name = os.path.split(file_path)
        new_file_name, = replace_path_parts(file_name,
                                            replacements=replacements)
        new_root_parts = Path(root.replace(src, dst)).parts
        new_root_parts = replace_path_parts(*new_root_parts,
                                            replacements=replacements)
        new_root = str(Path(*new_root_parts))
        return os.path.join(new_root, new_file_name)

    first_paths, second_paths = tee(paths)
    yield from zip(first_paths, map(replace_file_path, second_paths))


def replace_path_parts(*path_parts: str,
                       replacements: Dict[str, str]) -> Iterator[str]:
    yield from map(replacements.get, path_parts, path_parts)


def replace_lines(lines: Iterable[str],
                  *,
                  replacers: List[Callable[[str], str]]) -> Iterator[str]:
    def replace(string: str, replacer: Callable[[str], str]) -> str:
        return replacer(string)

    replace_items = partial(reduce, replace, replacers)
    yield from map(replace_items, lines)


if __name__ == '__main__':
    main()
