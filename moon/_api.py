# SPDX-License-Identifier: Apache-2.0
"""
Public API methods.
Should be

from moon import load, dump

Shouldn`t be imported directly.
"""

from typing import Any, Dict, Optional

from moon.core.composer import ASTComposer
from moon.core.constructor import construct
from moon.core.emitter import EventEmitter
from moon.core.fileio import FileOrPath, read, write
from moon.core.parser import EventParser
from moon.core.representer import represent
from moon.core.serializer import serialize
from moon.core.tokenizer import Tokenizer


def load(
    fp: FileOrPath,
    *,
    encoding: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Load MOON file and convert to python object.
    :param fp: path to MOON file or file-like object.
    :param encoding: file encoding, defaults to utf-8.
    :return: python dict.
    """

    content = read(fp=fp, encoding=encoding)
    tokenizer = Tokenizer(content)
    events = EventParser(tokenizer)
    ast = ASTComposer(events)
    result = construct(ast)
    return result


def dump(
    magicked: Dict[str, Any],
    fo: FileOrPath,
    *,
    encoding: Optional[str] = None,
) -> None:
    """
    Dump python object to MOON format.
    :param magicked: python object to dump.
    :param fo: path to MOON file. It will be created if not exist.
    :param encoding: encoding, defaults to utf-8.
    :return:
    """

    representation = represent(magicked)
    serialization = serialize(representation)
    content = EventEmitter(serialization)
    write(content, fo=fo, encoding=encoding)
