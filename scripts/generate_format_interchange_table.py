#!/usr/bin/env python3
"""
Emit a Markdown table of puzzle types supported for puzz.link <-> Penpa+ URL conversion.

Single source of truth: ``puzzlekit.formats.puzzle_types.PUZZLE_TYPES_DICT``.

Usage (from repo root)::

    PYTHONPATH=src python scripts/generate_format_interchange_table.py

Paste the output into README.md inside the ``<details>`` block for URL interchange,
or use it in release notes.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from puzzlekit.formats.puzzle_types import PUZZLE_TYPES_DICT  # noqa: E402


def _fmt_list(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, list):
        return ", ".join(str(i) for i in x)
    return str(x)


def main() -> None:
    print(
        "| Canonical (IR) | puzz.link token | puzz.link aliases | Penpa genre tag |\n"
        "| --- | --- | --- | --- |"
    )
    for canonical in sorted(PUZZLE_TYPES_DICT.keys()):
        meta = PUZZLE_TYPES_DICT[canonical]
        pl = meta.get("puzzlink", {})
        pp = meta.get("penpa", {})
        primary = pl.get("primary", canonical)
        pl_aliases = _fmt_list(pl.get("aliases", []))
        genre = pp.get("genre_tag", canonical)
        genre_s = _fmt_list(genre)
        pa = pp.get("aliases", [])
        if isinstance(pa, str):
            pa = [pa]
        extra = [
            str(a) for a in pa
            if str(a).strip().lower() != genre_s.strip().lower()
        ]
        penpa_cell = f"`{genre_s}`"
        if extra:
            penpa_cell += f" · *also:* {', '.join(extra)}"
        print(
            f"| `{canonical}` | `{primary}` | {pl_aliases} | {penpa_cell} |"
        )


if __name__ == "__main__":
    main()
