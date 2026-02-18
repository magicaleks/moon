"""
Factory for all tests. Used only as fixture argument.
"""

from pathlib import Path

import pytest
import pytest_dependency
from _pytest.config import Config as PytestConfig


class BaseFactory:
    @pytest.fixture()
    def fixtures_path(self) -> Path:
        return Path(__file__).parent / "fixtures"


@pytest.hookimpl(trylast=True)
def pytest_configure(config: PytestConfig) -> None:
    pytest_dependency._ignore_unknown = True
