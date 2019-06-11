import os
import tempfile

from hypothesis import strategies

from .common import ascii_alphanumeric
from .services import (azure_logins,
                       dockerhub_logins,
                       github_logins)

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
settings = strategies.fixed_dictionaries({
    'azure_login': azure_logins,
    'dockerhub_login': dockerhub_logins,
    'email': strategies.emails(),
    'github_login': github_logins,
    'project': projects_names,
})
template_directories_paths = strategies.just(os.path.abspath('template'))
temporary_directories = strategies.builds(tempfile.TemporaryDirectory)
