# SPDX-License-Identifier: Apache-2.0
"""
AST nodes schema. Nodes are parts of AST (Abstract syntax tree).
"""

from abc import ABC
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import List, Union


class NodeType(StrEnum):
    """AST node types."""

    # Objects
    object_ = auto()
    key_value = auto()
    scalar = auto()


@dataclass(slots=True)
class ASTNode(ABC):
    """
    Base syntax tree node.
    Root must be always document
    """

    type: Union[NodeType, str] = field(init=False)


@dataclass(slots=True)
class ScalarNode(ASTNode):
    """
    Scalar value node.
    End of AST branch
    """

    type: NodeType = field(default=NodeType.scalar, init=False)
    value: str


@dataclass(slots=True)
class TagNode(ASTNode, ABC):
    """
    Abstract tag node.
    """

    tag: str
    name: str
    children: List[ASTNode]
