"""
Some functions to simplify testing
"""

from hashlib import sha256
from pathlib import Path


def compare_strings(*strings: str) -> bool:
    """Compare two or many strings as hashes."""
    if len(strings) < 2:
        raise ValueError("Must have at least 2 strings to compare")

    iterator = map(lambda s: sha256(s.encode()).hexdigest(), strings)
    original = next(iterator)
    for hashed in iterator:
        if hashed != original:
            return False

    return True


def compare_files(*files: Path, encoding: str = "utf-8") -> bool:
    """Compare two or many files by comparing their contents."""
    if len(files) < 2:
        raise ValueError("Must have at least 2 files to compare")

    return compare_strings(
        *[file_path.read_text(encoding=encoding) for file_path in files]
    )
