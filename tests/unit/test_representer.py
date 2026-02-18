"""
Test representing stage. Turns Python dict into MOON AST.
"""

from typing import Any, Dict, List

import pytest

from moon.core.representer import represent
from moon.hooks.tags.object import KeyValueNode, ObjectNode
from moon.schemas import ASTNode, ScalarNode
from moon.schemas.errors import RepresenterError
from tests.conftest import BaseFactory


@pytest.mark.order(6)
@pytest.mark.dependency(name="representer_ok")
class TestRepresenter(BaseFactory):
    @pytest.mark.parametrize(
        ["obj", "expected"],
        [
            [
                {"me": {}},
                [
                    ObjectNode(
                        tag="@object",
                        name="me",
                        children=[],
                    ),
                ],
            ],
            [
                {"me": {"key1": "value1"}},
                [
                    ObjectNode(
                        tag="@object",
                        name="me",
                        children=[
                            KeyValueNode(
                                key=ScalarNode(value="key1"),
                                value=ScalarNode(value="value1"),
                            )
                        ],
                    ),
                ],
            ],
            [
                {"me": {"key1": "value1"}, "you": {"key2": "value2"}},
                [
                    ObjectNode(
                        tag="@object",
                        name="me",
                        children=[
                            KeyValueNode(
                                key=ScalarNode(value="key1"),
                                value=ScalarNode(value="value1"),
                            )
                        ],
                    ),
                    ObjectNode(
                        tag="@object",
                        name="you",
                        children=[
                            KeyValueNode(
                                key=ScalarNode(value="key2"),
                                value=ScalarNode(value="value2"),
                            )
                        ],
                    ),
                ],
            ],
        ],
    )
    def test_representer_positive(self, obj: Dict[str, Any], expected: List[ASTNode]):
        assert list(represent(obj)) == expected

    @pytest.mark.parametrize(
        "obj",
        [{123: {}}, None, [{"me": {}}]],
    )
    def test_representer_negative(self, obj: Any):
        with pytest.raises(RepresenterError):
            list(represent(obj))
