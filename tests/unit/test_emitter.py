"""
Test emitter stage. Turns events to text.
"""

from typing import List

import pytest

from moon.core.emitter import EventEmitter
from moon.schemas import EmitterError, Event, EventType
from tests.conftest import BaseFactory


@pytest.mark.order(8)
@pytest.mark.dependency(name="emitter_ok", depends=["serializer_ok"], scope="session")
class TestEmitter(BaseFactory):
    @pytest.mark.parametrize(
        ["events", "expected"],
        [
            [
                [
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="me"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.document_end),
                ],
                "@object me\n",
            ],
            [
                [
                    Event(type=EventType.tag_start, value="@object"),
                    Event(type=EventType.ident, value="me"),
                    Event(type=EventType.key, value="key1"),
                    Event(type=EventType.value, value="value1"),
                    Event(type=EventType.tag_end, value="@object"),
                    Event(type=EventType.document_end),
                ],
                "@object me\n    key1: value1\n",
            ],
            [
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
                "@object me\n    key1: value1\n\n@object you\n    key2: value2\n",
            ],
        ],
    )
    def test_emitter_positive(self, events: List[Event], expected: str):
        assert "".join(list(EventEmitter(events))) == expected

    @pytest.mark.parametrize(
        "events",
        [
            [
                Event(type=EventType.tag_start, value="@object"),
                Event(type=EventType.ident, value="me"),
                Event(type=EventType.tag_start, value="@object"),
                Event(type=EventType.tag_end, value="@object"),
                Event(type=EventType.document_end),
            ],
            [
                Event(type=EventType.tag_start, value="@object"),
                Event(type=EventType.ident, value="me"),
                Event(type=EventType.tag_start, value="@object"),
                Event(type=EventType.tag_end, value="@object"),
            ],
        ],
    )
    def test_emitter_negative(self, events: List[Event]):
        with pytest.raises(EmitterError):
            print(list(EventEmitter(events)))
