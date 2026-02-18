"""
Test full load pipeline and compares to JSON analogue.
"""

import json
from pathlib import Path

import moon
from tests.conftest import BaseFactory


class TestLoad(BaseFactory):
    def test_load_positive(self, fixtures_path: Path):
        json_file = fixtures_path / "mixed.json"
        assert moon.load(fp=fixtures_path / "mixed.moon") == json.loads(
            json_file.read_text()
        )

    def test_load_file_positive(self, fixtures_path: Path):
        json_file = fixtures_path / "mixed.json"
        json_obj = json.loads(json_file.read_text())
        moon_file = fixtures_path / "mixed.moon"
        assert moon.load(fp=open(moon_file, "r")) == json_obj
