# SPDX-License-Identifier: Apache-2.0
"""
Serialization stage. Turns AST into a stream of events
"""

from typing import Iterable, Iterator

from moon.hooks.tags import resolve_tag
from moon.schemas import Event, EventType, SerializationError, TagNode


def serialize(ast: Iterable[TagNode]) -> Iterator[Event]:
    """
    Serialize an AST nodes into a stream of events
    :param ast: AST nodes
    :return: stream of events
    """
    for node in ast:
        if not isinstance(node, TagNode):
            raise SerializationError(f"expected TagNode, got {type(node)}")

        hook = resolve_tag(node.tag)
        if hook is None:
            raise SerializationError(f"Cannot resolve tag {node.tag}")
        yield from hook.serialize(node)

    yield Event(type=EventType.document_end)
