# SPDX-License-Identifier: Apache-2.0
"""
Object tah hook. Resolving as python dict with str keys.
@object me:
    name: Alex
    role: developer
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Union

from moon.core.base import StatefulStreamer
from moon.hooks.types import represent_type, resolve_type
from moon.schemas import (
    ASTNode,
    DuplicateIdentifierNode,
    EmitterError,
    Event,
    EventType,
    InvalidObjectError,
    NodeType,
    ScalarNode,
    SerializationError,
    TagNode,
    Token,
    TokenType,
    UnexpectedEvent,
    UnexpectedNode,
    UnexpectedToken,
)

from .hook import TagHook, resolve_tag


@dataclass(slots=True)
class KeyValueNode(ASTNode):
    """
    Key Value node.
    Can be a child of ObjectNode.
    Key must be a ScalarNode, value Scalar or complex ASTNode.
    """

    type: NodeType = field(default=NodeType.key_value, init=False)
    key: ScalarNode
    value: Union[ScalarNode, ASTNode]


@dataclass(slots=True)
class ObjectNode(TagNode):
    """
    @object node.
    Children are list of key_value nodes.
    """

    type: NodeType = field(default=NodeType.object_, init=False)
    name: str
    children: List[KeyValueNode]


def _parse_pair_hook(streamer: StatefulStreamer[Token, Event]) -> Iterator[Event]:
    value_started = False
    token = streamer.read()
    yield Event(type=EventType.key, value=token.value)
    streamer.next()
    value = ""
    while True:
        token = streamer.read()

        if not value_started:
            if token.type == TokenType.colon:
                value_started = True
            elif token.type not in [TokenType.space, TokenType.tab]:
                raise UnexpectedToken(f"Unexpected token: {token}. Expected colon.")
        else:
            if token.type not in [TokenType.newline, TokenType.comment, TokenType.eof]:
                value += token.value
            else:
                yield Event(type=EventType.value, value=value.strip())
                return

        streamer.next()


class ObjectHook(TagHook):
    tag = "@object"
    object_type = dict

    @classmethod
    def parse(cls, streamer: StatefulStreamer[Token, Event]) -> Iterator[Event]:
        identified = False  # found object identifier mark
        while True:
            token = streamer.read()

            if not identified:
                if token.type == TokenType.word:
                    identified = True
                    yield Event(type=EventType.ident, value=token.value)
                elif token.type not in [TokenType.tab, TokenType.space]:
                    raise UnexpectedToken(
                        f"Unexpected token: {token}. Expected identifier."
                    )

            else:
                if token.type == TokenType.word:
                    yield from _parse_pair_hook(streamer)
                elif token.type not in [
                    TokenType.tab,
                    TokenType.space,
                    TokenType.newline,
                    TokenType.eof,
                ]:
                    raise UnexpectedToken(
                        f"Unexpected token: {token}. Expected field key."
                    )

            peeked = streamer.peek()
            if (
                streamer.read().type == TokenType.eof
                or peeked.type == TokenType.word
                and resolve_tag(peeked.value)
            ):
                break

            streamer.next()

    @classmethod
    def compose(cls, streamer: StatefulStreamer[Event, ASTNode]) -> TagNode:
        nodes = []
        ident = streamer.next()
        if ident.type != EventType.ident:
            raise UnexpectedEvent(f"Unexpected event type {ident.type}")

        while True:
            event = streamer.read()

            if event.type == EventType.key:
                value_event = streamer.next()
                if value_event.type != EventType.value:
                    raise UnexpectedEvent(f"Unexpected event type {value_event.type}")
                nodes.append(
                    KeyValueNode(
                        key=ScalarNode(value=event.value),
                        value=ScalarNode(value=value_event.value),
                    )
                )
            if event.type == EventType.tag_end:
                return ObjectNode(tag=cls.tag, name=ident.value, children=nodes)

            streamer.next()

    @classmethod
    def construct(cls, node: TagNode) -> Any:
        res = {}

        for child in node.children:
            if isinstance(child, KeyValueNode):
                pair_value = child.value
                if isinstance(pair_value, ScalarNode):
                    if child.key.value not in res:
                        res[child.key.value] = resolve_type(pair_value.value)
                    else:
                        raise DuplicateIdentifierNode(
                            f"Duplicate keys {child.key.value}."
                        )
                elif isinstance(pair_value, ASTNode):
                    raise NotImplementedError("Nesting objects not implemented yet")
                else:
                    raise UnexpectedNode(f"Unexpected node: {pair_value}")
            else:
                raise UnexpectedNode(f"Unexpected node: {child}")

        return res

    @classmethod
    def represent(cls, name: str, value: Dict[str, Any]) -> TagNode:
        if not isinstance(value, dict):
            raise InvalidObjectError(f"Expected dict. Got {type(value)}")

        children = []

        for k, v in value.items():
            if not isinstance(k, str):
                raise InvalidObjectError(f"Unexpected key: {k}")

            value_scalar = represent_type(v)
            children.append(
                KeyValueNode(
                    key=ScalarNode(value=k), value=ScalarNode(value=value_scalar)
                )
            )

        return ObjectNode(tag=cls.tag, name=name, children=children)

    @classmethod
    def serialize(cls, value: TagNode) -> Iterator[Event]:
        yield Event(type=EventType.tag_start, value=cls.tag)
        yield Event(type=EventType.ident, value=value.name)
        for child in value.children:
            if not isinstance(child, KeyValueNode):
                raise SerializationError(f"Expected KeyValueNode. Got {type(child)}")
            yield Event(type=EventType.key, value=child.key.value)
            yield Event(type=EventType.value, value=child.value.value)
        yield Event(type=EventType.tag_end, value=cls.tag)

    @classmethod
    def emit(cls, streamer: StatefulStreamer[Event, str]) -> str:
        content = "" + cls.tag
        identified = False
        next_event = streamer.read()
        if next_event.type != EventType.tag_start and next_event.value != cls.tag:
            raise EmitterError(f"Unexpected event type {next_event.type}")

        streamer.next()

        while True:
            event = streamer.read()
            if not identified:
                if event.type == EventType.ident:
                    identified = True
                    content += " " + event.value + "\n"
                else:
                    raise EmitterError(f"Unexpected event: {event}")
            else:
                if event.type == EventType.key:
                    content += " " * 4 + event.value + ": "
                elif event.type == EventType.value:
                    content += event.value + "\n"
                elif event.type == EventType.tag_end:
                    break
                else:
                    raise EmitterError(f"Unexpected event: {event}")

            streamer.next()

        return content
