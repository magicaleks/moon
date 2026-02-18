# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Final, List, Tuple, Type

_resolve_bool_kw: Final[dict[str, bool]] = {"true": True, "false": False}
_represent_bool_kw: Final[dict[bool, str]] = {True: "true", False: "false"}


class TypeHook(ABC):
    """Base class for type hooks."""

    def __init_subclass__(cls, **kwargs) -> None:
        _hooks.append(cls)

    @classmethod
    @abstractmethod
    def resolve(cls, value: str) -> Tuple[bool, Any]:
        pass

    @classmethod
    @abstractmethod
    def represent(cls, value: Any) -> Tuple[bool, Any]:
        pass


_hooks: List[Type[TypeHook]] = []


def _is_float(value: str) -> bool:
    try:
        float(value)
    except (ValueError, TypeError):
        return False
    else:
        return True


def resolve_type(value: str) -> Any:
    """
    Resolve a scalar type from a node value.
    :param value: The value to resolve type.
    :return: The resolved scalar type.
    """
    for hook in _hooks:
        resolved, res = hook.resolve(value)
        if resolved:
            return res

    if value.isdigit():
        return int(value)
    elif _is_float(value):
        return float(value)
    elif value in _resolve_bool_kw:
        return _resolve_bool_kw[value]
    elif value == "null":
        return None
    else:
        return str(value)


def represent_type(value: Any) -> str:
    for hook in _hooks:
        represented, res = hook.represent(value)
        if represented:
            return res

    if isinstance(value, bool):
        return _represent_bool_kw[value]
    elif isinstance(value, (int, float, str)):
        return str(value)
    elif value is None:
        return "null"
    else:
        raise TypeError(f"Cannot represent type {type(value)}")
