import os
import tempfile
from functools import partial

from hypothesis import strategies

from monty import monty
from .common import ascii_alphanumeric
from .services import (azure_logins,
                       dockerhub_logins,
                       github_logins)

descriptions = strategies.text(
        strategies.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=1)
licenses_classifiers = monty.load_licenses_classifiers()
licenses = strategies.sampled_from(
        [classifier.rsplit(' :: ', 1)[-1]
         for classifier in licenses_classifiers
         if len([sub_classifier
                 for sub_classifier in licenses_classifiers
                 if sub_classifier.startswith(classifier)]) == 1])
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
    'license': licenses,
    'project': projects_names,
    'version': versions,
})
template_directories_paths = strategies.just(os.path.abspath('template'))
temporary_directories = strategies.builds(tempfile.TemporaryDirectory)
