# SPDX-License-Identifier: Apache-2.0
"""
AST (Abstract Syntax Tree) Composer. Is a pre-final stage of loading MOON.
"""

from typing import Iterator

from moon.core.base import StatefulStreamer
from moon.hooks.tags import resolve_tag
from moon.schemas import (
    ASTError,
    ASTNode,
    Event,
    EventType,
    UnexpectedEvent,
    UnknownEvent,
)


class ASTComposer(StatefulStreamer[Event, ASTNode]):
    """
    Stateful AST composer. Turns stream of events into stream of AST nodes.
    """

    def __iter__(self) -> Iterator[ASTNode]:
        while True:
            try:
                event = self.read()

                if event.type == EventType.tag_start:
                    tag_hook = resolve_tag(event.value)
                    if not tag_hook:
                        raise UnknownEvent(f"Unknown event: {event}")

                    yield tag_hook.compose(self)

                elif event.type == EventType.document_end:
                    return

                else:
                    raise UnexpectedEvent(
                        f"Unexpected event: {event}. Expected: tag start"
                    )

                self.next()
            except StopIteration:
                raise ASTError("Unexpected end of stream of events.")
