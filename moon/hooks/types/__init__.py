# SPDX-License-Identifier: Apache-2.0
"""
Types hooks module. Define resolving, representing methods and Base TypeHook class.
"""

from .hook import TypeHook, represent_type, resolve_type

__all__ = ["TypeHook", "resolve_type", "represent_type"]
