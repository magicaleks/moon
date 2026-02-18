# SPDX-License-Identifier: Apache-2.0
"""
Tokenization is the first stage of MOON loading.
It separates content into tokens (lexemes), lexical parts of text.
"""

from typing import Dict, Iterator

from moon.core.base import StatefulStreamer
from moon.schemas import TokenizerError
from moon.schemas.tokens import Token, TokenType


def _normalize(raw: str) -> str:
    """Normalize input content"""
    norm = raw.lstrip()

    if not norm or len(norm) == 0:
        raise TokenizerError("Empty content")

    # Removing BOM
    if norm.startswith("\ufeff"):
        norm = norm[1:]

    norm = norm.replace("\r\n", "\n").replace("\r", "\n")

    return norm


class Tokenizer(StatefulStreamer[str, Token]):
    """
    Stateful tokenizer. Turns string into stream of tokens.
    """

    spec_tokens: Dict[str, TokenType] = {
        "\n": TokenType.newline,
        "\t": TokenType.tab,
        " ": TokenType.space,
        ",": TokenType.comma,
        ":": TokenType.colon,
        "'": TokenType.quote,
        '"': TokenType.d_quote,
    }

    def __init__(self, stream: str) -> None:
        super().__init__(_normalize(stream))
        self._pos = 1
        self._line = 1
        self._column = 1

    def _tok(self, ttype: TokenType, value: str = "") -> Token:
        val_len = len(value)
        offset = val_len - 1
        return Token(
            self._pos - offset,
            self._line,
            self._column - offset,
            ttype,
            value,
        )

    def _advance(self) -> None:
        self.next()
        self._column += 1
        self._pos += 1

    def __iter__(self) -> Iterator[Token]:
        while True:
            try:
                char = self.read()

                tt = self.spec_tokens.get(char)
                if tt:
                    yield self._tok(tt, char)
                    if tt == TokenType.newline:
                        self._line += 1
                        self._column = 0
                elif char == "/" and self.peek() in [
                    "/",
                    "*",
                ]:
                    yield self._scan_comment()
                else:
                    yield self._scan_word()
                self._advance()
            except StopIteration:
                break

        yield self._tok(TokenType.eof)

    def _scan_comment(
        self,
    ) -> Token:
        is_multiline = self.peek() == "*"
        val = ""
        while True:
            char = self.read()
            val += char
            if is_multiline:
                if char == "*" and self.peek() == "/":
                    return self._tok(TokenType.comment, val)
            elif self.peek() == "\n":
                return self._tok(TokenType.comment, val)

            self._advance()

    def _scan_word(self) -> Token:
        """Scan word (directive, key, value or other anything)"""
        val = ""
        while True:
            char = self.read()
            val += char
            if self.peek() in self.spec_tokens or self.peek() is None:
                return self._tok(TokenType.word, val)

            self._advance()
