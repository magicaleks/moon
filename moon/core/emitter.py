# SPDX-License-Identifier: Apache-2.0
"""
Final dump stage. Turns events into text.
"""

from typing import Iterator

from moon.core.base import StatefulStreamer
from moon.hooks.tags import resolve_tag
from moon.schemas import EmitterError, Event, EventType


class EventEmitter(StatefulStreamer[Event, str]):
    def __iter__(self) -> Iterator[str]:
        while True:
            try:
                event = self.read()
                if event.type == EventType.document_end:
                    break
                if event.type == EventType.tag_start:
                    hook = resolve_tag(event.value)
                    yield hook.emit(self)
                    peaked = self.peek()
                    if peaked is None:
                        raise EmitterError("Unexpected end of stream.")
                    else:
                        if peaked.type == EventType.tag_start:
                            yield "\n"
                        elif peaked.type == EventType.document_end:
                            break
                        else:
                            raise EmitterError(f"Unknown event type: {peaked.type}")
                else:
                    raise EmitterError(f"Unknown event type: {self.read().type}")

                self.next()
            except StopIteration:
                raise EmitterError("Unexpected end of stream")
