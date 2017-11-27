from functools import partial
from typing import (Any,
                    Iterable)

import click
import pytest

from scripts.monty import (main,
                           files_paths)


def test_monty(settings_path: str,
               template_dir: str,
               output_dir: str) -> None:
    monty = partial(main.callback,
                    version=False,
                    settings_path=settings_path,
                    template_dir=template_dir,
                    output_dir=output_dir)

    template_dir_files_count = capacity(files_paths(template_dir))
    files_count_before = capacity(files_paths(output_dir))

    monty(overwrite=False)

    files_count_after = capacity(files_paths(output_dir))

    monty(overwrite=True)

    files_count_after_overwrite = capacity(files_paths(output_dir))

    assert files_count_after == files_count_before + template_dir_files_count
    assert files_count_after_overwrite == files_count_after

    with pytest.raises(click.BadOptionUsage):
        monty(overwrite=False)


def capacity(elements: Iterable[Any]) -> int:
    return sum(1 for _ in elements)
