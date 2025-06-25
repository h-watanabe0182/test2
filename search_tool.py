#!/usr/bin/env python3
"""Simple CLI tool to search for a string in files within a directory."""

import argparse
from pathlib import Path


def search_in_file(file_path: Path, query: str, ignore_case: bool) -> None:
    """Print occurrences of query in the given file."""
    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as fh:
            for lineno, line in enumerate(fh, 1):
                haystack = line
                needle = query
                if ignore_case:
                    haystack = haystack.lower()
                    needle = needle.lower()
                if needle in haystack:
                    print(f"{file_path}:{lineno}:{line.strip()}")
    except (UnicodeDecodeError, PermissionError):
        # Skip files that can't be read as text or accessed
        pass


def search_directory(directory: Path, query: str, ignore_case: bool, ext: str | None = None) -> None:
    """Recursively search files under directory for query.

    Parameters
    ----------
    directory: Path
        Root directory to search.
    query: str
        String to look for.
    ignore_case: bool
        Whether to ignore case differences.
    ext: str | None
        If provided, only files with this extension (e.g. '.txt') are searched.
    """
    for path in directory.rglob('*'):
        if path.is_file() and (ext is None or path.suffix == ext):
            search_in_file(path, query, ignore_case)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search for a string in files within a directory."
    )
    parser.add_argument("directory", help="Path of directory to search")
    parser.add_argument("query", help="String to search for")
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Perform case-insensitive search",
    )
    parser.add_argument(
        "--ext",
        metavar="EXT",
        help="Only search files with this extension (e.g. .txt)",
    )
    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.is_dir():
        parser.error(f"{directory} is not a directory")
    search_directory(directory, args.query, args.ignore_case, args.ext)


if __name__ == "__main__":
    main()
