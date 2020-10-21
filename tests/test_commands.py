import os
import tempfile
from contextlib import (ExitStack,
                        contextmanager)
from functools import partial
from typing import (Any,
                    Dict,
                    Iterable,
                    Optional)

import click
import pytest
import strictyaml
from hypothesis import given

from monty import monty
from tests import strategies
from tests.utils import Secured


@given(strategies.settings,
       strategies.templates_directories_paths,
       strategies.template_repositories_names,
       strategies.temporary_directories,
       strategies.github_access_tokens)
def test_main(settings: Dict[str, str],
              templates_directory_path: str,
              template_repository_name: Optional[str],
              temporary_directory: tempfile.TemporaryDirectory,
              github_access_token: Secured) -> None:
    with ExitStack() as stack:
        output_dir = stack.enter_context(temporary_directory)
        settings_path = stack.enter_context(write_settings(settings))

        command = partial(monty.main.callback,
                          version=False,
                          settings_path=settings_path,
                          templates_dir=templates_directory_path,
                          output_dir=output_dir,
                          github_access_token=github_access_token.value,
                          template_repo=template_repository_name)

        files_count_before = capacity(monty.files_paths(output_dir))

        command(overwrite=False)

        template_directory_files_count = capacity(monty.files_paths(
                templates_directory_path))

        files_count_after = capacity(monty.files_paths(output_dir))

        command(overwrite=True)

        files_count_after_overwrite = capacity(monty.files_paths(output_dir))

        assert files_count_after == (files_count_before
                                     + template_directory_files_count)
        assert files_count_after_overwrite == files_count_after

        if template_directory_files_count:
            with pytest.raises(click.BadOptionUsage):
                command(overwrite=False)


@contextmanager
def write_settings(settings: Dict[str, str]) -> Any:
    file = tempfile.NamedTemporaryFile(mode='w',
                                       encoding='utf8',
                                       delete=False)
    file.write(strictyaml.as_document(settings).as_yaml())
    file.close()
    result = file.name
    try:
        yield result
    finally:
        os.unlink(result)


def capacity(elements: Iterable[Any]) -> int:
    return sum(1 for _ in elements)
