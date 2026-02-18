# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Iterator, Optional, Tuple, Type, Union

from moon.core.base import StatefulStreamer
from moon.schemas import ASTNode, Event, TagNode
from moon.schemas.tokens import Token


class TagHook(ABC):
    """Base class for tag hooks."""

    tag: ClassVar[str]
    object_type: ClassVar[Union[Type, Tuple[Type]]]

    def __init_subclass__(cls, **kwargs) -> None:
        if not hasattr(cls, "tag"):
            raise AttributeError("TagHook subclasses must define 'tag' attribute")

        if not isinstance(cls.tag, str):
            raise TypeError("'tag' attribute must be a string")

        if not cls.tag.startswith("@"):
            raise AttributeError("Tag attribute must starts with '@'")

        _parsing_hooks[cls.tag] = cls

        if not hasattr(cls, "object_type"):
            raise AttributeError(
                "TagHook subclasses must define 'object_type' attribute"
            )

        if isinstance(cls.object_type, type):
            _representing_hooks[cls.object_type] = cls
        elif isinstance(cls.object_type, tuple):
            for object_type in cls.object_type:
                if not isinstance(object_type, type):
                    raise TypeError(
                        "'object_type' attribute must be a type or a tuple of types"
                    )
                _representing_hooks[object_type] = cls

        else:
            raise TypeError(
                "'object_type' attribute must be a type or a tuple of types"
            )

    @classmethod
    @abstractmethod
    def parse(cls, streamer: StatefulStreamer[Token, Event]) -> Iterator[Event]:
        pass

    @classmethod
    @abstractmethod
    def compose(cls, streamer: StatefulStreamer[Event, ASTNode]) -> TagNode:
        pass

    @classmethod
    @abstractmethod
    def construct(cls, node: TagNode) -> Any:
        pass

    @classmethod
    @abstractmethod
    def represent(cls, name: str, value: Any) -> TagNode:
        pass

    @classmethod
    @abstractmethod
    def serialize(cls, value: TagNode) -> Iterator[Event]:
        pass

    @classmethod
    @abstractmethod
    def emit(cls, stream: StatefulStreamer[Event, str]) -> str:
        pass


_parsing_hooks: Dict[str, Type[TagHook]] = {}
_representing_hooks: Dict[Type, Type[TagHook]] = {}


def resolve_tag(tag: str) -> Optional[Type[TagHook]]:
    """Resolve tag and returns parsing hook"""
    return _parsing_hooks.get(tag)


def resolve_representer(obj_type: Type) -> Optional[Type[TagHook]]:
    """Resolve tag and returns representer hook"""
    return _representing_hooks.get(obj_type)
