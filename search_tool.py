#!/usr/bin/env python3
"""File search tool with CLI and GUI interfaces."""

import argparse
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox


def search_in_file(file_path: Path, query: str, ignore_case: bool) -> list[str]:
    """Return matching lines in file as formatted strings."""
    results = []
    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as fh:
            for lineno, line in enumerate(fh, 1):
                haystack = line
                needle = query
                if ignore_case:
                    haystack = haystack.lower()
                    needle = needle.lower()
                if needle in haystack:
                    results.append(f"{file_path}:{lineno}:{line.rstrip()}")
    except (UnicodeDecodeError, PermissionError):
        pass
    return results


def search_directory(directory: Path, query: str, ignore_case: bool, ext: str | None = None) -> list[str]:
    """Recursively search files under directory for query."""
    matches = []
    for path in directory.rglob('*'):
        if path.is_file() and (ext is None or path.suffix == ext):
            matches.extend(search_in_file(path, query, ignore_case))
    return matches


def run_gui() -> None:
    """Launch GUI for searching files."""
    if not os.environ.get("DISPLAY"):
        raise RuntimeError("DISPLAY environment variable is not set")

    root = tk.Tk()
    root.title("File Search Tool")

    directory_var = tk.StringVar()
    query_var = tk.StringVar()
    ignore_case_var = tk.BooleanVar()
    ext_var = tk.StringVar()

    def browse_directory() -> None:
        path = filedialog.askdirectory()
        if path:
            directory_var.set(path)

    def do_search() -> None:
        directory = Path(directory_var.get())
        query = query_var.get()
        if not directory.is_dir():
            messagebox.showerror("Error", "指定したフォルダが存在しません")
            return
        results_text.delete('1.0', tk.END)
        matches = search_directory(directory, query, ignore_case_var.get(), ext_var.get() or None)
        if matches:
            for line in matches:
                results_text.insert(tk.END, line + "\n")
        else:
            results_text.insert(tk.END, "見つかりませんでした\n")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.X)

    tk.Label(frame, text="フォルダ").grid(row=0, column=0, sticky=tk.W)
    tk.Entry(frame, textvariable=directory_var, width=40).grid(row=0, column=1, sticky=tk.W)
    tk.Button(frame, text="参照", command=browse_directory).grid(row=0, column=2, padx=5)

    tk.Label(frame, text="検索文字列").grid(row=1, column=0, sticky=tk.W)
    tk.Entry(frame, textvariable=query_var, width=40).grid(row=1, column=1, sticky=tk.W)

    tk.Checkbutton(frame, text="大文字小文字を無視", variable=ignore_case_var).grid(row=2, column=1, sticky=tk.W)
    tk.Label(frame, text="拡張子").grid(row=3, column=0, sticky=tk.W)
    tk.Entry(frame, textvariable=ext_var, width=10).grid(row=3, column=1, sticky=tk.W)

    tk.Button(frame, text="検索", command=do_search).grid(row=4, column=1, pady=5, sticky=tk.W)

    results_text = scrolledtext.ScrolledText(root, width=80, height=20)
    results_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Search for a string in files within a directory.")
    parser.add_argument("directory", nargs="?", help="Path of directory to search")
    parser.add_argument("query", nargs="?", help="String to search for")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Perform case-insensitive search")
    parser.add_argument("--ext", metavar="EXT", help="Only search files with this extension (e.g. .txt)")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    args = parser.parse_args()

    if args.gui or not (args.directory and args.query):
        try:
            run_gui()
        except RuntimeError as exc:
            parser.error(str(exc))
        return

    directory = Path(args.directory)
    if not directory.is_dir():
        parser.error(f"{directory} is not a directory")
    matches = search_directory(directory, args.query, args.ignore_case, args.ext)
    for line in matches:
        print(line)


if __name__ == "__main__":
    main()
