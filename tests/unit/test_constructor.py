"""
Test final Python dict constructor. Turns AST into Python dict.
"""

import pytest

from moon.core.composer import ASTComposer
from moon.core.constructor import construct
from moon.core.parser import EventParser
from moon.core.tokenizer import Tokenizer
from moon.schemas import ConstructorError
from tests.conftest import BaseFactory


@pytest.mark.order(5)
@pytest.mark.dependency(name="construct_ok", depends=["composing_ok"], scope="session")
class TestConstructor(BaseFactory):
    @pytest.mark.parametrize(
        ["content", "expected"],
        [
            [
                "@object me",
                {"me": {}},
            ],
            [
                "@object me\nkey1: value1",
                {"me": {"key1": "value1"}},
            ],
            [
                "@object me\nkey1: value1\n\n@object you\nkey2: value2",
                {"me": {"key1": "value1"}, "you": {"key2": "value2"}},
            ],
        ],
    )
    def test_constructor_positive(self, content: str, expected: object):
        assert construct(ASTComposer(EventParser(Tokenizer(content)))) == expected

    @pytest.mark.parametrize(
        "content",
        [
            "@object me @object me",
        ],
    )
    def test_constructor_negative(self, content: str):
        with pytest.raises(ConstructorError):
            construct(ASTComposer(EventParser(Tokenizer(content))))
