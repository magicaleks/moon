# SPDX-License-Identifier: Apache-2.0
"""
MOON internal errors.
"""


class _MOONError(Exception):
    """
    Base MOON error class.
    """


class ArgumentsError(_MOONError):
    """
    Raised when arguments are invalid.
    """


class ReadError(_MOONError):
    """
    Raised when reading failed.
    """


class WriteError(_MOONError):
    """
    Raised when writing failed.
    """


class TokenizerError(_MOONError):
    """
    Base tokenizer error.
    """


class ParserError(_MOONError):
    """
    Base parser error.
    """


class UnexpectedToken(ParserError):
    """
    Raised when unexpected token is encountered.
    """


class UnexpectedEOF(ParserError):
    """
    Raised when unexpected eof is encountered.
    """


class ASTError(_MOONError):
    """
    Base AST composing error.
    """


class UnexpectedEvent(ASTError):
    """
    Raised when unexpected event is encountered.
    """


class UnknownEvent(ASTError):
    """
    Raised when unknown event is encountered.
    """


class ConstructorError(_MOONError):
    """
    Base constructor error.
    """


class UnexpectedNode(ConstructorError):
    """
    Raised when unexpected node is encountered.
    """


class UnknownNode(ConstructorError):
    """
    Raised when an unknown node is encountered.
    """


class DuplicateIdentifierNode(ConstructorError):
    """
    Raised when found duplicate tag identifier.
    """


class RepresenterError(_MOONError):
    """
    Base representer error.
    """


class InvalidObjectError(RepresenterError):
    """
    Raised when an invalid object is encountered.
    """


class SerializationError(_MOONError):
    """
    Base serialization error.
    """


class EmitterError(_MOONError):
    """
    Base emitter error.
    """
