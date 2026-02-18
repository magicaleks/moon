"""
Test Event parser. Should get tokens and return events.
"""

from typing import List

import pytest

from moon.core.parser import EventParser
from moon.core.tokenizer import Tokenizer
from moon.schemas import Event, EventType, ParserError
from tests.conftest import BaseFactory


@pytest.mark.order(3)
@pytest.mark.dependency(name="parsing_ok", depends=["tokenize_ok"], scope="session")
class TestParser(BaseFactory):
    @pytest.mark.parametrize(
        ["content", "expected"],
        [
            [
                "@object me\nkey1: value1",
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
                "@object me\nkey1: value1\nkey2: value2\n\n@object you\nkey1: value1\n",
                [
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="me"),
                    Event(type=EventType.key, value="key1"),
                    Event(type=EventType.value, value="value1"),
                    Event(type=EventType.key, value="key2"),
                    Event(type=EventType.value, value="value2"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="you"),
                    Event(type=EventType.key, value="key1"),
                    Event(type=EventType.value, value="value1"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.document_end),
                ],
            ],
        ],
    )
    def test_parser_positive(self, content: str, expected: List[Event]):
        assert list(EventParser(Tokenizer(content))) == expected

    @pytest.mark.parametrize(
        "content",
        [
            "@object me key\n@object me",
            "@object me\nkey1:\n:\nvalue1",
            "@unexistingtag me\nkey1: value1",
        ],
    )
    def test_parser_negative(self, content: str):
        with pytest.raises(ParserError):
            list(EventParser(Tokenizer(content)))
