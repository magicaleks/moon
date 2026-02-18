"""
Test serializing stage. Turns AST into events.
"""

from typing import List

import pytest

from moon.core.serializer import serialize
from moon.hooks.tags.object import KeyValueNode, ObjectNode
from moon.schemas import Event, EventType, ScalarNode, SerializationError, TagNode
from tests.conftest import BaseFactory


class _InvalidTag(TagNode):
    type = "invalid"


@pytest.mark.order(7)
@pytest.mark.dependency(
    name="serializer_ok", depends=["representer_ok"], scope="session"
)
class TestSerializer(BaseFactory):
    @pytest.mark.parametrize(
        ["ast", "expected"],
        [
            [
                [
                    ObjectNode(
                        tag="@object",
                        name="me",
                        children=[],
                    ),
                ],
                [
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="me"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.document_end),
                ],
            ],
            [
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
                [
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="me"),
                    Event(type=EventType.key, value="key1"),
                    Event(type=EventType.value, value="value1"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.document_end),
                ],
            ],
            [
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
                [
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="me"),
                    Event(type=EventType.key, value="key1"),
                    Event(type=EventType.value, value="value1"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="you"),
                    Event(type=EventType.key, value="key2"),
                    Event(type=EventType.value, value="value2"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.document_end),
                ],
            ],
        ],
    )
    def test_serializer_positive(self, ast: List[TagNode], expected: List[Event]):
        assert list(serialize(ast)) == expected

    @pytest.mark.parametrize(
        "ast",
        [
            [
                KeyValueNode(
                    key=ScalarNode(value="key1"), value=ScalarNode(value="value1")
                ),
            ],
            [
                _InvalidTag(tag="invalid", name="invalid", children=[]),
            ],
        ],
    )
    def test_serializer_negative(self, ast: List[TagNode]):
        with pytest.raises(SerializationError):
            list(serialize(ast))
