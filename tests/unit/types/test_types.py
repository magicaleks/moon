"""
Test types resolving. Base resolvers and extensions.
"""

from typing import Any, Type

import pytest

from moon.hooks.types import represent_type, resolve_type
from tests.conftest import BaseFactory


class TestTypes(BaseFactory):
    @pytest.mark.parametrize(
        ["scalar", "expected_type"],
        [
            ["123", int],
            ["1234321231", int],
            ["1.012312", float],
            [".12312.3123", str],
            ["smth", str],
            ["true", bool],
            ["false", bool],
            ["null", type(None)],
        ],
    )
    def test_type_resolve(self, scalar: str, expected_type: Type):
        assert type(resolve_type(scalar)) is expected_type

    @pytest.mark.parametrize(
        ["obj", "represented"],
        [
            [123, "123"],
            [1234321231, "1234321231"],
            [1.012312, "1.012312"],
            ["smth", "smth"],
            [True, "true"],
            [False, "false"],
            [None, "null"],
        ],
    )
    def test_type_represent(self, obj: Any, represented: str):
        assert represent_type(obj) == represented
