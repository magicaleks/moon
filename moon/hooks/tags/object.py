# SPDX-License-Identifier: Apache-2.0
"""
Object tah hook. Resolving as python dict with str keys.
@object me:
    name: Alex
    role: developer
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Final, Iterator, List, Tuple, Union

from moon.core.base import StatefulStreamer
from moon.hooks.types import represent_type, resolve_type
from moon.schemas import (
    ASTNode,
    DuplicateIdentifierNode,
    EmitterError,
    Event,
    EventType,
    InvalidObjectError,
    LevelIndentationError,
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

INDENTATION: Final[int] = 4


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
class NestedObjectNode(ASTNode):
    """
    Nested object node.
    The same object node just inside other object.
    """

    type: NodeType = field(default=NodeType.nested_object, init=False)
    children: List[KeyValueNode]


@dataclass(slots=True)
class ObjectNode(TagNode):
    """
    @object node.
    Children are list of key_value nodes.
    """

    type: NodeType = field(default=NodeType.object_, init=False)
    name: str
    children: List[Union[KeyValueNode, NestedObjectNode]]


def _parse_pair(streamer: StatefulStreamer[Token, Event]) -> Iterator[Event]:
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
            elif token.type != TokenType.space:
                raise UnexpectedToken(f"Unexpected token: {token}. Expected colon.")
        else:
            if token.type not in [TokenType.newline, TokenType.comment, TokenType.eof]:
                if token.type != TokenType.space or (
                    token.type == TokenType.space and len(value) > 0
                ):
                    value += token.value
            else:
                yield Event(type=EventType.value, value=value)
                return

        streamer.next()


def _compose_object_nodes(
    streamer: StatefulStreamer[Event, ASTNode],
) -> List[KeyValueNode]:
    nodes = []
    while True:
        event = streamer.read()
        if event.type == EventType.key:
            value_event = streamer.next()
            if streamer.peek().type == EventType.nesting_start:
                streamer.next()
                nodes.append(
                    KeyValueNode(
                        key=ScalarNode(value=event.value),
                        value=NestedObjectNode(
                            children=_compose_object_nodes(streamer),
                        ),
                    )
                )
            elif value_event.type == EventType.value:
                nodes.append(
                    KeyValueNode(
                        key=ScalarNode(value=event.value),
                        value=ScalarNode(value=value_event.value),
                    )
                )
            else:
                raise UnexpectedEvent(f"Unexpected event type {value_event.type}")
        if streamer.read().type == EventType.tag_end:
            return nodes
        elif streamer.read().type == EventType.nesting_end:
            streamer.next()
            return nodes
        elif event.type != EventType.key:
            streamer.next()


def _represent_object(
    value: Dict[str, Any],
) -> List[Union[KeyValueNode, NestedObjectNode]]:
    children = []

    for k, v in value.items():
        if not isinstance(k, str):
            raise InvalidObjectError(f"Invalid key: {k}. Must be str got: {type(k)}")

        if isinstance(v, Dict):
            nested_children = _represent_object(v)
            children.append(
                KeyValueNode(
                    key=ScalarNode(value=k),
                    value=NestedObjectNode(children=nested_children),
                )
            )
        elif isinstance(v, List):
            raise NotImplementedError(f"Arrays support not implemented.")
        else:
            value_scalar = represent_type(v)
            children.append(
                KeyValueNode(
                    key=ScalarNode(value=k), value=ScalarNode(value=value_scalar)
                )
            )

    return children


def _serialize_object(node: Union[ObjectNode, NestedObjectNode]) -> Iterator[Event]:
    for child in node.children:
        if isinstance(child, KeyValueNode):
            yield Event(type=EventType.key, value=child.key.value)
            if isinstance(child.value, NestedObjectNode):
                yield Event(type=EventType.nesting_start)
                yield from _serialize_object(child.value)
                yield Event(type=EventType.nesting_end)
            else:
                yield Event(type=EventType.value, value=child.value.value)
        else:
            raise SerializationError(f"Expected KeyValueNode. Got {type(child)}")


class ObjectHook(TagHook):
    tag = "@object"
    object_type = dict

    @classmethod
    def parse(cls, streamer: StatefulStreamer[Token, Event]) -> Iterator[Event]:
        identified = False
        while True:
            token = streamer.read()

            if token.type == TokenType.word and not identified:
                yield Event(type=EventType.ident, value=token.value)
                identified = True
            elif (
                token.type in [TokenType.newline, TokenType.comment, TokenType.eof]
                and identified
            ):
                break
            elif token.type != TokenType.space:
                raise UnexpectedToken(
                    f"Unexpected token: {token}. Expected identifier."
                )

            streamer.next()

        indent_level = 0
        indents: List[int] = []
        while True:
            token = streamer.read()
            if token.type == TokenType.word:
                if not indents:
                    indents.append(indent_level)
                if indent_level == indents[-1]:
                    yield from _parse_pair(streamer)
                elif indent_level < indents[-1] and indent_level in indents:
                    for i in range(len(indents[indents.index(indent_level) + 1 :])):
                        yield Event(type=EventType.nesting_end)
                    del indents[indents.index(indent_level) + 1 :]
                    yield from _parse_pair(streamer)
                elif indent_level > indents[-1]:
                    yield Event(type=EventType.nesting_start)
                    yield from _parse_pair(streamer)
                    indents.append(indent_level)
                else:
                    raise LevelIndentationError(
                        f"Indentation error at {token.line}:{token.column}"
                    )
                indent_level = 0
            elif token.type == TokenType.space:
                indent_level += 1
            elif token.type not in [
                TokenType.eof,
                TokenType.newline,
                TokenType.comment,
            ]:
                raise UnexpectedToken(f"Unexpected token: {token}. Expected field key.")

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
        ident = streamer.next()
        if ident.type != EventType.ident:
            raise UnexpectedEvent(f"Unexpected event type {ident.type}")

        return ObjectNode(
            tag=cls.tag, name=ident.value, children=_compose_object_nodes(streamer)
        )

    @classmethod
    def construct(cls, node: ASTNode) -> Any:

        if not isinstance(node, (ObjectNode, NestedObjectNode)):
            raise UnexpectedNode(
                f"Unexpected node: {node}. Expected ObjectNode or NestedObjectNode."
            )

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
                elif isinstance(pair_value, NestedObjectNode):
                    res[child.key.value] = cls.construct(pair_value)
                else:
                    raise UnexpectedNode(f"Unexpected node: {pair_value}")
            else:
                raise UnexpectedNode(f"Unexpected node: {child}")

        return res

    @classmethod
    def represent(cls, name: str, value: Dict[str, Any]) -> TagNode:
        if not isinstance(value, dict):
            raise InvalidObjectError(f"Expected dict. Got {type(value)}")

        children = _represent_object(value)

        return ObjectNode(tag=cls.tag, name=name, children=children)

    @classmethod
    def serialize(cls, value: TagNode) -> Iterator[Event]:
        if not isinstance(value, ObjectNode):
            raise UnexpectedNode(
                f"Unexpected node: {value}. Expected ObjectNode got {type(value)}"
            )
        yield Event(type=EventType.tag_start, value=cls.tag)
        yield Event(type=EventType.ident, value=value.name)
        yield from _serialize_object(value)
        yield Event(type=EventType.tag_end, value=cls.tag)

    @classmethod
    def emit(cls, streamer: StatefulStreamer[Event, str]) -> str:
        content = "" + cls.tag
        identified = False
        next_event = streamer.read()
        if next_event.type != EventType.tag_start and next_event.value != cls.tag:
            raise EmitterError(f"Unexpected event type {next_event.type}")

        streamer.next()

        indent_level = 1

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
                    content += " " * INDENTATION * indent_level + event.value + ":"
                    if streamer.peek().type == EventType.nesting_start:
                        content += "\n"
                    else:
                        content += " "
                elif event.type == EventType.value:
                    content += event.value + "\n"
                elif event.type == EventType.tag_end:
                    break
                elif event.type == EventType.nesting_start:
                    indent_level += 1
                elif event.type == EventType.nesting_end:
                    indent_level -= 1
                else:
                    raise EmitterError(f"Unexpected event: {event}")

            streamer.next()

        return content
