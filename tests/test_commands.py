from functools import partial
from typing import (Any,
                    Iterable,
                    Optional)

import click
import pytest

from monty import monty


def test_main(settings_path: str,
              template_dir: str,
              output_dir: str,
              github_access_token: Optional[str]) -> None:
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

    assert files_count_after == files_count_before + template_dir_files_count
    assert files_count_after_overwrite == files_count_after

    with pytest.raises(click.BadOptionUsage):
        command(overwrite=False)


def capacity(elements: Iterable[Any]) -> int:
    return sum(1 for _ in elements)
