# SPDX-License-Identifier: Apache-2.0
"""
Representing stage. Represents Python dict as AST.
"""

from typing import Any, Dict, Iterator

from moon.hooks.tags import resolve_representer
from moon.schemas import InvalidObjectError, TagNode


def represent(obj: Dict[str, Any]) -> Iterator[TagNode]:
    """
    Represents Python dict as AST.
    :param obj: Python dict.
    :return: ASTNode iterator.
    """
    if not isinstance(obj, dict):
        raise InvalidObjectError(f"Expected obj dict, got {type(obj)}")
    for k, v in obj.items():
        if not isinstance(k, str):
            raise InvalidObjectError(f"Key {k} is not a string. Got {type(k)}")

        hook = resolve_representer(type(v))

        yield hook.represent(k, v)
