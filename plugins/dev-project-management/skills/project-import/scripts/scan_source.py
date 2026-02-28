#!/usr/bin/env python3
"""
Scan an external project directory and produce a structured summary for import.

Usage:
    python3 scan_source.py <source-directory>

Outputs JSON with:
    - suggested_project_id: kebab-case derived from directory name
    - file_tree: list of {path, size_bytes, type} entries
    - doc_contents: dict mapping filename -> content for markdown/text files
    - structure_hints: {has_code, has_docs, has_subdirs, file_count, extensions}

Stdlib only. Exits non-zero on error.
"""

import json
import os
import re
import sys
from pathlib import Path

MAX_DEPTH = 4
MAX_DOC_SIZE = 50_000
MAX_FILES = 500
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".org"}
DOC_NAMES = {"readme", "project", "todo", "notes", "plan", "spec", "design",
             "changelog", "history", "status", "overview", "description"}
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".c", ".cpp", ".h",
    ".java", ".rb", ".sh", ".bash", ".zsh", ".pl", ".swift", ".kt", ".cs",
    ".lua", ".zig", ".nim", ".ex", ".exs", ".hs", ".ml", ".clj",
}
SKIP_DIRS = {".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv",
             "venv", ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
             ".eggs", "target"}


def to_kebab(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    return s or "unnamed-project"


def classify_file(ext: str) -> str:
    if ext in DOC_EXTENSIONS:
        return "doc"
    if ext in CODE_EXTENSIONS:
        return "code"
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp"}:
        return "image"
    if ext in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env"}:
        return "config"
    if ext in {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"}:
        return "archive"
    return "other"


def is_doc_candidate(path: Path) -> bool:
    if path.suffix.lower() in DOC_EXTENSIONS:
        stem = path.stem.lower()
        if stem in DOC_NAMES or path.suffix.lower() == ".md":
            return True
        if path.parent == path.parents[0]:
            return True
    return False


def scan_directory(root: Path):
    file_tree = []
    doc_contents = {}
    extensions = set()
    has_code = False
    has_docs = False
    has_subdirs = False
    file_count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        rel_dir = Path(dirpath).relative_to(root)
        depth = len(rel_dir.parts)
        if depth > MAX_DEPTH:
            dirnames.clear()
            continue

        if dirnames and depth == 0:
            has_subdirs = True

        for fname in filenames:
            if file_count >= MAX_FILES:
                break

            fpath = Path(dirpath) / fname
            rel_path = fpath.relative_to(root)

            try:
                size = fpath.stat().st_size
            except OSError:
                size = 0

            ext = fpath.suffix.lower()
            ftype = classify_file(ext)
            extensions.add(ext) if ext else None

            if ftype == "code":
                has_code = True
            if ftype == "doc":
                has_docs = True

            file_tree.append({
                "path": str(rel_path),
                "size_bytes": size,
                "type": ftype,
            })
            file_count += 1

            if ftype == "doc" and size <= MAX_DOC_SIZE:
                if is_doc_candidate(fpath) or depth == 0:
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="replace")
                        doc_contents[str(rel_path)] = content
                    except OSError:
                        pass

        if file_count >= MAX_FILES:
            break

    file_tree.sort(key=lambda f: f["path"])

    return {
        "suggested_project_id": to_kebab(root.name),
        "source_path": str(root),
        "file_tree": file_tree,
        "doc_contents": doc_contents,
        "structure_hints": {
            "has_code": has_code,
            "has_docs": has_docs,
            "has_subdirs": has_subdirs,
            "file_count": file_count,
            "extensions": sorted(extensions),
        },
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: scan_source.py <source-directory>"}))
        sys.exit(1)

    source = Path(sys.argv[1]).resolve()
    if not source.exists():
        print(json.dumps({"ok": False, "error": f"Directory not found: {source}"}))
        sys.exit(1)
    if not source.is_dir():
        print(json.dumps({"ok": False, "error": f"Not a directory: {source}"}))
        sys.exit(1)

    result = scan_directory(source)
    result["ok"] = True
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
