# SPDX-License-Identifier: Apache-2.0
"""
Tokens schema. Token is a lexical part of text content.
"""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Optional


class TokenType(StrEnum):
    # Base tokens
    eof = auto()
    tab = auto()
    space = auto()
    newline = auto()

    # Literals
    word = auto()

    # Comments
    comment = auto()

    # Punctuation
    comma = auto()  # ,
    colon = auto()  # :
    quote = auto()  # '
    d_quote = auto()  # "


@dataclass(slots=True)
class Token:
    """
    Base class for all tokens.
    """

    pos: int
    line: int
    column: int
    type: TokenType
    value: Optional[str] = None

    def __repr__(self) -> str:
        return f"<Token '{self.value}' type: '{self.type}' at line {self.line} column {self.column}>"
