# SPDX-License-Identifier: Apache-2.0
"""
Files IO module. Define read and write methods.
"""

from io import BufferedIOBase, TextIOBase
from os import PathLike
from pathlib import Path
from typing import AnyStr, BinaryIO, Iterable, Optional, TextIO, Union

from moon.schemas import ArgumentsError, ReadError, WriteError

FileOrPath = Union[
    AnyStr,
    PathLike[AnyStr],
    TextIO,
    BinaryIO,
    TextIOBase,
    BufferedIOBase,
]


def read(
    fp: FileOrPath,
    encoding: Optional[str] = None,
) -> str:
    """
    Read str content using filepath or file-like object.

    :param fp: File path or file-like object.
    :param encoding: File encoding.
    :raises ArgumentsError: If fp is not a path or file-like object.
    :raises ReadError: If any error occurs.
    :return: Content string.
    """

    if isinstance(fp, (PathLike, str, bytes)):
        try:
            if isinstance(fp, bytes):
                fp = fp.decode()
            if not Path(fp).exists():
                raise ReadError(f"File {fp!r} does not exist.")
            if not Path(fp).is_file():
                raise ReadError(f"File {fp!r} is not a file.")
            with open(fp, "r", encoding=encoding) as f:
                content = f.read()
        except FileNotFoundError as e:
            raise ReadError(f"File {fp!r} not found") from e
        except PermissionError as e:
            raise ReadError(f"Cannot read {fp!r} because access denied") from e
        except UnicodeDecodeError as e:
            raise ReadError(f"Cannot read {fp!r} because encoding error") from e
        except OSError as e:
            raise ReadError(f"Cannot read {fp!r} because {e}") from e

    elif isinstance(fp, (TextIO, BinaryIO, TextIOBase, BufferedIOBase)):
        try:
            raw = fp.read()
            if isinstance(raw, bytes):
                # Default encoding UTF-8
                raw = raw.decode(encoding=encoding or "utf-8")
            content = raw
        except UnicodeDecodeError as e:
            raise ReadError(f"Cannot read {fp} because encoding error") from e
        except IOError as e:
            raise ReadError(f"Cannot read {fp} because {e}") from e

    else:
        raise ArgumentsError(
            f"'fp' argument must be a file-like or path-like object. Got {type(fp)}"
        )

    return content


def write(
    content: Union[Iterable[str], str],
    fo: FileOrPath,
    encoding: Optional[str] = None,
) -> None:
    """
    Write str content using filepath or file-like object.

    :param content: Text content or iterator of strings.
    :param fo: File object or file-like object.
    :param encoding: File encoding.
    :raises ArgumentsError: If fo is not a path or file-like object.
    :raises WriteError: If any other error occurs.
    :return: Content string.
    """

    if isinstance(fo, (str, bytes, PathLike)):
        try:
            with open(fo, "w", encoding=encoding) as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    for chunk in content:
                        f.write(chunk)
        except PermissionError as e:
            raise WriteError(f"Cannot write {fo!r} because access denied") from e
        except OSError as e:
            raise WriteError(f"Cannot write {fo!r} because {e}") from e

    elif isinstance(fo, (TextIO, TextIOBase)):
        try:
            if isinstance(content, str):
                fo.write(content)
            else:
                for chunk in content:
                    fo.write(chunk)
        except IOError as e:
            raise WriteError(f"Cannot write {fo} because {e}") from e

    elif isinstance(fo, (BinaryIO, BufferedIOBase)):
        try:
            if isinstance(content, str):
                fo.write(content.encode("utf-8"))
            else:
                for chunk in content:
                    fo.write(chunk.encode("utf-8"))
        except IOError as e:
            raise WriteError(f"Cannot write {fo} because {e}") from e

    else:
        raise ArgumentsError(
            f"'fo' argument must be a file-like or path-like object. Got {type(fo)}"
        )
