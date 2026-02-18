"""
Test full dump pipeline.
"""

import json
import tempfile
from pathlib import Path

import moon
from tests.conftest import BaseFactory
from tests.utils import compare_files


class TestDump(BaseFactory):
    def test_dump_positive(self, fixtures_path: Path):
        json_data = json.loads((fixtures_path / "mixed.json").read_text())
        moon_path = Path(tempfile.gettempdir()) / "mixed.moon"
        moon.dump(magicked=json_data, fo=moon_path)
        assert compare_files(moon_path, fixtures_path / "mixed.moon")

    def test_dump_file_positive(self, fixtures_path: Path):
        json_file = fixtures_path / "mixed.json"
        json_obj = json.loads(json_file.read_text())
        moon_path = Path(tempfile.gettempdir()) / "mixed.moon"
        moon.dump(magicked=json_obj, fo=open(moon_path, "w"))
        assert compare_files(moon_path, fixtures_path / "mixed.moon")
