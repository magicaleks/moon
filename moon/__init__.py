# SPDX-License-Identifier: Apache-2.0
"""
A framework for working with MOON (Magic Oriented Object Notation) in Python.
It is a hybrid of YAML and TOON.
Its distinguishing feature is its multi-data model support and unlimited extensibility.

Quickstart with:

# ./example.moon
@object context
  task: Our favorite hikes together
  location: Boulder
  season: spring_2025

# ./main.py
from moon import load

config = load("./example.moon")

print(config["context"])

[0]: {"task": "Our favorite hikes together", "location": "Boulder", "season": "spring_2025"}

"""

from ._api import dump, load

__all__ = ["load", "dump"]
