import tempfile
from functools import partial

from hypothesis import strategies

from monty import monty
from .common import ascii_alphanumeric
from .services import (azure_logins,
                       dockerhub_logins,
                       github_logins)


def is_utf_8_string(string: str) -> bool:
    try:
        string.encode('utf-8').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False
    else:
        return True


descriptions = (strategies.text(
        strategies.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=1)
                .filter(is_utf_8_string))
licenses_classifiers = strategies.sampled_from(
        monty.load_licenses_classifiers())
projects_names_delimiters = '.-_'
projects_names_alphabet = strategies.sampled_from(ascii_alphanumeric
                                                  + projects_names_delimiters)


def project_name_valid(project_name: str) -> bool:
    for delimiter in projects_names_delimiters:
        surrounded_by_delimiter = (project_name.startswith(delimiter) or
                                   project_name.endswith(delimiter))
        if surrounded_by_delimiter:
            return False
    return True


projects_names = (strategies.text(alphabet=projects_names_alphabet,
                                  min_size=2,
                                  max_size=100)
                  .filter(project_name_valid))
versions_parts = strategies.integers(0, 100)
versions = (strategies.tuples(versions_parts, versions_parts, versions_parts)
            .map(partial(map, str))
            .map('.'.join))
settings = strategies.fixed_dictionaries({
    'azure_login': azure_logins,
    'description': descriptions,
    'dockerhub_login': dockerhub_logins,
    'email': strategies.emails(),
    'github_login': github_logins,
    'license_classifier': licenses_classifiers,
    'project': projects_names,
    'version': versions,
    'min_python_version': versions,
    'max_python_version': versions,
})
template_directories_paths = strategies.builds(tempfile.mkdtemp)
template_repositories_names = strategies.just(
        'lycantropos/monty-cpython-pypy-template')
temporary_directories = strategies.builds(tempfile.TemporaryDirectory)
