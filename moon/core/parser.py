# SPDX-License-Identifier: Apache-2.0
"""
Events parsing stage. Events are logical parts of MOON file between tokens and AST.
"""

from typing import Iterator

from moon.core.base import StatefulStreamer
from moon.hooks.tags import resolve_tag
from moon.schemas import Event, EventType, ParserError, UnexpectedEOF, UnexpectedToken
from moon.schemas.tokens import Token, TokenType


class EventParser(StatefulStreamer[Token, Event]):
    """
    Stateful event parser. Turns a stream of tokens into a stream of events.
    """

    def __iter__(self) -> Iterator[Event]:
        while True:
            try:
                token = self.read()
                if token.type in [
                    TokenType.tab,
                    TokenType.space,
                    TokenType.newline,
                    TokenType.comment,
                ]:
                    pass
                elif token.type == TokenType.eof:
                    yield Event(type=EventType.document_end)
                    return
                elif token.type == TokenType.word:
                    yield from self._parse_tag()
                    continue
                else:
                    raise UnexpectedToken(token)
                self.next()
            except StopIteration:
                raise UnexpectedEOF("Unexpected EOF")

    def _parse_tag(self) -> Iterator[Event]:
        """Parse tag struct from tokens using resolved tag hook."""
        tag = self.read()
        self.next()
        yield Event(type=EventType.tag_start, value=tag.value)

        hook = resolve_tag(tag.value)
        if hook is None:
            raise ParserError(f"Unknown tag: {tag}")
        yield from hook.parse(self)
        yield Event(type=EventType.tag_end, value=tag.value)
