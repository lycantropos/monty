import os
import tempfile
from typing import Dict

import pytest
import yaml

from tests import strategies
from tests.utils import example


@pytest.fixture(scope='function')
def settings() -> Dict[str, str]:
    return example(strategies.settings)


@pytest.fixture(scope='function')
def settings_path(settings: Dict[str, str]) -> str:
    file = tempfile.NamedTemporaryFile(mode='w',
                                       encoding='utf8',
                                       delete=False)
    yaml.safe_dump(settings, file)
    file.close()
    result = file.name
    try:
        yield result
    finally:
        os.unlink(result)


@pytest.fixture(scope='function')
def template_dir() -> str:
    return os.path.abspath('template')


@pytest.fixture(scope='function')
def output_dir() -> str:
    with tempfile.TemporaryDirectory() as result:
        yield result
