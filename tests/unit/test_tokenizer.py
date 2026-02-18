"""
Test tokenizer. Should get text and return parsed tokens.
"""

import pytest

from moon.core.tokenizer import Tokenizer
from moon.schemas import Token, TokenizerError, TokenType
from tests.conftest import BaseFactory


@pytest.mark.order(2)
@pytest.mark.dependency(name="tokenize_ok")
class TestTokenizer(BaseFactory):
    @pytest.mark.parametrize(
        "content",
        [
            "@object me\nkey1: value1",
            "\ufeff@object me\nkey1: value1",
            "@object me\r\nkey1: value1",
        ],
    )
    def test_tokenize_positive(self, content: str):
        expected = [
            Token(pos=1, line=1, column=1, type=TokenType.word, value="@object"),
            Token(pos=8, line=1, column=8, type=TokenType.space, value=" "),
            Token(pos=9, line=1, column=9, type=TokenType.word, value="me"),
            Token(pos=11, line=1, column=11, type=TokenType.newline, value="\n"),
            Token(pos=12, line=2, column=1, type=TokenType.word, value="key1"),
            Token(pos=16, line=2, column=5, type=TokenType.colon, value=":"),
            Token(pos=17, line=2, column=6, type=TokenType.space, value=" "),
            Token(pos=18, line=2, column=7, type=TokenType.word, value="value1"),
            Token(pos=24, line=2, column=13, type=TokenType.eof, value=""),
        ]
        assert list(Tokenizer(content)) == expected

    @pytest.mark.parametrize(
        "content",
        [
            "",
        ],
    )
    def test_tokenize_negative(self, content: str):
        with pytest.raises(TokenizerError):
            list(Tokenizer(content))
