# SPDX-License-Identifier: Apache-2.0
"""
Events schema. Event is a logical part of text content.
"""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Optional, Union


class EventType(StrEnum):
    # Base events
    document_end = auto()

    # Directives events
    tag_start = auto()
    tag_end = auto()

    # Object pairs
    key = auto()
    value = auto()

    # Idents
    ident = auto()


@dataclass(slots=True)
class Event:
    """
    Event means smth happened into file.
    Ex. object start, type defined, etc
    """

    type: Union[EventType, str]
    value: Optional[str] = None
