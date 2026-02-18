"""
Test files reading/writing module.
"""

import io
import tempfile
from pathlib import Path

import pytest

from moon.core import fileio
from moon.schemas import ReadError, WriteError
from tests.conftest import BaseFactory
from tests.utils import compare_files, compare_strings


@pytest.mark.order(1)
class TestFileIO(BaseFactory):
    def test_read_path_positive(self, fixtures_path: Path):
        path = fixtures_path / "mixed.moon"
        assert fileio.read(fp=path) == path.read_text()

    @pytest.mark.parametrize(
        "file_path",
        ["path/to/somthing.moon", "invalid<>:path", "../fixtures/integration"],
    )
    def test_read_path_negative(self, file_path: Path):
        with pytest.raises(ReadError):
            fileio.read(fp=file_path)

    def test_read_file_positive(self, fixtures_path: Path):
        moon_file = fixtures_path / "mixed.moon"
        moon_text = moon_file.read_text()
        assert compare_strings(fileio.read(fp=open(moon_file, "r")), moon_text)

        bytes_buffer = io.BytesIO()
        bytes_buffer.write(open(moon_file, "rb").read())
        bytes_buffer.seek(0)
        assert compare_strings(fileio.read(fp=bytes_buffer), moon_text)

        str_buffer = io.StringIO()
        str_buffer.write(open(moon_file, "r").read())
        str_buffer.seek(0)
        assert compare_strings(fileio.read(fp=str_buffer), moon_text)

    def test_write_path_positive(self, fixtures_path: Path):
        moon_path = Path(tempfile.gettempdir()) / "mixed.moon"
        moon_text = (fixtures_path / "mixed.moon").read_text()
        fileio.write(moon_text, fo=moon_path)
        assert compare_files(moon_path, fixtures_path / "mixed.moon")

    @pytest.mark.parametrize(
        "file_path",
        ["not/existing/path/somthing.moon", tempfile.gettempdir()],
    )
    def test_dump_path_negative(self, file_path: Path):
        with pytest.raises(WriteError):
            fileio.write("@object context", file_path)

    def test_dump_file_positive(self, fixtures_path: Path):
        origin_moon_path = fixtures_path / "mixed.moon"
        origin_moon_content = open(origin_moon_path, "r").read()
        moon_path = Path(tempfile.gettempdir()) / "mixed.moon"
        fileio.write(origin_moon_content, fo=open(moon_path, "w"))
        assert compare_files(moon_path, fixtures_path / "mixed.moon")

        bytes_buffer = io.BytesIO()
        fileio.write(origin_moon_content, fo=bytes_buffer)
        bytes_buffer.seek(0)
        assert compare_strings(bytes_buffer.read().decode(), origin_moon_content)

        str_buffer = io.StringIO()
        fileio.write(origin_moon_content, fo=str_buffer)
        str_buffer.seek(0)
        assert compare_strings(str_buffer.read(), origin_moon_content)
