import tempfile
from functools import partial

from hypothesis import strategies

from monty import monty
from .common import ascii_alphanumeric
from .services import (dockerhub_logins,
                       github_logins)


def is_utf_8_string(string: str) -> bool:
    try:
        string.encode('utf-8').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False
    else:
        return True


descriptions = (
    (strategies.text(strategies.characters(blacklist_categories=('Cs', 'Cc')),
                     min_size=1)
     .filter(is_utf_8_string))
)
trove_licenses_classifiers = strategies.sampled_from(
        monty.load_trove_licenses_classifiers()
)
spdx_licenses_identifiers = strategies.sampled_from(
        list(monty.load_spdx_licenses_info())
)
projects_names_delimiters = '.-_'
projects_names_alphabet = strategies.sampled_from(ascii_alphanumeric
                                                  + projects_names_delimiters)


def project_name_valid(project_name: str) -> bool:
    return not any(project_name.startswith(delimiter)
                   or project_name.endswith(delimiter)
                   for delimiter in projects_names_delimiters)


projects_names = (strategies.text(alphabet=projects_names_alphabet,
                                  min_size=2,
                                  max_size=100)
                  .filter(project_name_valid))
versions_parts = strategies.integers(0, 100)
versions = (strategies.tuples(versions_parts, versions_parts, versions_parts)
            .map(partial(map, str))
            .map('.'.join))
optional_settings = {
    monty.TROVE_LICENSE_CLASSIFIER_KEY: trove_licenses_classifiers,
    'min_python_version': versions,
    'max_python_version': versions,
}
required_settings = {
    'description': descriptions,
    'dockerhub_login': dockerhub_logins,
    'email': strategies.emails(),
    'github_login': github_logins,
    'spdx_licenses_identifier': spdx_licenses_identifiers,
    'project': projects_names,
    'version': versions,
}
settings = strategies.fixed_dictionaries({**required_settings,
                                          **optional_settings})
templates_directories_paths = strategies.builds(tempfile.mkdtemp)
template_repositories_names = strategies.sampled_from(
        ['lycantropos/monty-cpp-bind-port-template',
         'lycantropos/monty-cpython-pypy-template',
         'lycantropos/monty-python-c-api-template',
         'lycantropos/monty-rust-python-template',
         'lycantropos/monty-rust-template']
)
temporary_directories = strategies.builds(tempfile.TemporaryDirectory)
