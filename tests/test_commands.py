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


@given(strategies.settings,
       strategies.template_dirs,
       strategies.temporary_dirs,
       strategies.github_access_tokens)
def test_main(settings: Dict[str, str],
              template_dir: str,
              temporary_dir: tempfile.TemporaryDirectory,
              github_access_token: Optional[str]) -> None:
    with ExitStack() as stack:
        output_dir = stack.enter_context(temporary_dir)
        settings_path = stack.enter_context(write_settings(settings))

        command = partial(monty.main.callback,
                          version=False,
                          settings_path=settings_path,
                          template_dir=template_dir,
                          output_dir=output_dir,
                          github_access_token=github_access_token)

        template_dir_files_count = capacity(monty.files_paths(template_dir))
        files_count_before = capacity(monty.files_paths(output_dir))

        command(overwrite=False)

        files_count_after = capacity(monty.files_paths(output_dir))

        command(overwrite=True)

        files_count_after_overwrite = capacity(monty.files_paths(output_dir))

        assert files_count_after == (files_count_before
                                     + template_dir_files_count)
        assert files_count_after_overwrite == files_count_after

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
