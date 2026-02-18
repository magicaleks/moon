# SPDX-License-Identifier: Apache-2.0
"""
Tags hooks module. Define resolving, representing methods and Base TagHook class.
"""

from .hook import TagHook, resolve_representer, resolve_tag
from .object import (
    ObjectHook,  # noqa: F401 TODO: until static extensions loading under dev
)

__all__ = ["TagHook", "resolve_tag", "resolve_representer"]
