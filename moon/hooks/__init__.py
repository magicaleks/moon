# SPDX-License-Identifier: Apache-2.0
"""
Hooks are extending adapters.
They can define special tags or types and extend existing features.
"""

from .tags import TagHook, resolve_representer, resolve_tag
from .types import TypeHook, represent_type, resolve_type

__all__ = [
    "TagHook",
    "resolve_tag",
    "resolve_representer",
    "TypeHook",
    "resolve_type",
    "represent_type",
]
