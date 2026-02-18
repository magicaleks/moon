"""
Test AST composing. Should get events and return AST (Abstract syntax tree)
"""

from typing import List

import pytest

from moon.core.composer import ASTComposer
from moon.core.parser import EventParser
from moon.core.tokenizer import Tokenizer
from moon.hooks.tags.object import KeyValueNode, ObjectNode
from moon.schemas import ASTError, ASTNode, Event, EventType, ScalarNode
from tests.conftest import BaseFactory


@pytest.mark.order(4)
@pytest.mark.dependency(name="composing_ok", depends=["parsing_ok"], scope="session")
class TestComposer(BaseFactory):
    @pytest.mark.parametrize(
        ["content", "expected"],
        [
            [
                "@object me",
                [
                    ObjectNode(tag="@object", name="me", children=[]),
                ],
            ],
            [
                "@object me\nkey1: value1",
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
                "@object me\nkey1: value1\n\n@object you\nkey2: value2",
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
    def test_compose_positive(self, content: str, expected: List[ASTNode]):
        assert list(ASTComposer(EventParser(Tokenizer(content)))) == expected

    @pytest.mark.parametrize(
        "events",
        [
            [
                Event(type=EventType.tag_start, value="@object"),
                Event(type=EventType.ident, value="me"),
                Event(type=EventType.tag_start, value="@object"),
            ],
            [
                Event(type=EventType.tag_start, value="@object"),
                Event(type=EventType.ident, value="me"),
                Event(type=EventType.tag_end, value="@object"),
                Event(type=EventType.ident, value="me"),
            ],
        ],
    )
    def test_compose_negative(self, events: List[Event]):
        with pytest.raises(ASTError):
            list(ASTComposer(events))
