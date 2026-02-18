# SPDX-License-Identifier: Apache-2.0
"""
Final loading stage. Python object construction from MOON AST.
"""

from typing import Any, Dict, Iterable

from moon.hooks.tags import resolve_tag
from moon.schemas import (
    ASTNode,
    DuplicateIdentifierNode,
    TagNode,
    UnexpectedNode,
    UnknownNode,
)


def construct(ast: Iterable[ASTNode]) -> Dict[str, Any]:
    """
    Builds Python dict from MOON AST.
    :param ast: MOON AST node.
    :return: Python dict.
    """

    res = dict()

    for node in ast:
        if isinstance(node, TagNode):
            hook = resolve_tag(node.tag)
            if not hook:
                raise UnknownNode(f"Unexpected AST node: {node}")
            if node.name in res:
                raise DuplicateIdentifierNode(f"Duplicate identifier: {node.name}")
            res[node.name] = hook.construct(node)
        else:
            raise UnexpectedNode(
                f"Unexpected AST node: {node}. Only tag nodes allowed on top level."
            )

    return res
