#!/usr/bin/env python3
"""Create a compact local inventory for PRD folders or frontend repos."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


TEXT_EXTS = {
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".yaml",
    ".yml",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".css",
    ".scss",
}

DOC_EXTS = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK_RE = re.compile(r"https?://[^\s)>\"]+")
CODE_HINT_RE = re.compile(
    r"(route|router|path|component|permission|feature.?flag|api|service|"
    r"loading|empty|error|retry|i18n|formatMessage|defineMessages|t\()",
    re.IGNORECASE,
)


def read_headings(path: Path, limit: int) -> list[str]:
    headings: list[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                match = HEADING_RE.match(line)
                if match:
                    headings.append(match.group(0).strip())
                    if len(headings) >= limit:
                        break
    except OSError:
        return []
    return headings


def read_links(path: Path, limit: int) -> list[str]:
    links: list[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                for link in LINK_RE.findall(line):
                    links.append(link)
                    if len(links) >= limit:
                        return links
    except OSError:
        return []
    return links


def code_hints(path: Path, limit: int) -> list[str]:
    hints: list[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for idx, line in enumerate(fh, 1):
                if CODE_HINT_RE.search(line):
                    hints.append(f"{idx}: {line.strip()[:160]}")
                    if len(hints) >= limit:
                        break
    except OSError:
        return []
    return hints


def inventory(root: Path, max_files: int, max_items: int) -> dict:
    files = []
    skipped_dirs = {".git", "node_modules", "dist", "build", ".next", "coverage"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skipped_dirs]
        for filename in filenames:
            path = Path(dirpath) / filename
            rel = path.relative_to(root)
            suffix = path.suffix.lower()
            if suffix not in TEXT_EXTS and suffix not in DOC_EXTS:
                continue
            item = {
                "path": str(rel),
                "ext": suffix,
                "size": path.stat().st_size if path.exists() else None,
            }
            if suffix in {".md", ".txt"}:
                item["headings"] = read_headings(path, max_items)
                item["links"] = read_links(path, max_items)
            elif suffix in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}:
                item["code_hints"] = code_hints(path, max_items)
            files.append(item)
            if len(files) >= max_files:
                return {"root": str(root), "truncated": True, "files": files}
    return {"root": str(root), "truncated": False, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--max-files", type=int, default=200)
    parser.add_argument("--max-items", type=int, default=12)
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Path not found: {root}")
    print(json.dumps(inventory(root, args.max_files, args.max_items), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
