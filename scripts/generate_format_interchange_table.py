#!/usr/bin/env python3
"""
Emit or sync the Markdown table of puzz.link <-> Penpa+ URL conversion types.

Single source of truth: ``puzzlekit.formats.puzzle_types.PUZZLE_TYPES_DICT``.

Usage (from repo root)::

    PYTHONPATH=src python scripts/generate_format_interchange_table.py
    PYTHONPATH=src python scripts/generate_format_interchange_table.py --update-readme
    PYTHONPATH=src python scripts/generate_format_interchange_table.py --check-readme
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from puzzlekit.formats.puzzle_types import PUZZLE_TYPES_DICT  # noqa: E402

README_PATH = _REPO_ROOT / "README.md"
TABLE_HEADER = "| Canonical (IR) | puzz.link token | puzz.link aliases | Penpa genre tag |"
SECTION_TITLE = "Supported puzzle types for URL interchange"


def _fmt_list(x: object) -> str:
    if x is None:
        return ""
    if isinstance(x, list):
        return ", ".join(str(i) for i in x)
    return str(x)


def render_table() -> str:
    lines = [
        "| Canonical (IR) | puzz.link token | puzz.link aliases | Penpa genre tag |",
        "| --- | --- | --- | --- |",
    ]
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
        lines.append(
            f"| `{canonical}` | `{primary}` | {pl_aliases} | {penpa_cell} |"
        )
    return "\n".join(lines) + "\n"


def _section_note() -> str:
    n = len(PUZZLE_TYPES_DICT)
    return (
        f"> ({n} canonical IR types; generated from "
        f"`src/puzzlekit/formats/puzzle_types.py` — run "
        f"`python scripts/generate_format_interchange_table.py --update-readme` to refresh.)\n\n"
    )


def _render_details_block(table: str) -> str:
    return (
        "<details>\n"
        f"<summary><strong>{SECTION_TITLE}</strong>\n"
        "</summary>\n\n"
        f"{_section_note()}"
        f"{table}"
        "</details>\n"
    )


def _locate_interchange_section(readme_text: str) -> tuple[int, int]:
    """Return (start, end) slice indices for the URL interchange <details> block."""
    title_idx = readme_text.find(SECTION_TITLE)
    if title_idx == -1:
        raise RuntimeError(
            f"Could not find '{SECTION_TITLE}' in README.md"
        )

    details_start = readme_text.rfind("<details>", 0, title_idx)
    if details_start == -1:
        raise RuntimeError("Could not find opening <details> for URL interchange section")

    table_idx = readme_text.find(TABLE_HEADER, title_idx)
    if table_idx == -1:
        raise RuntimeError(f"Could not find table header '{TABLE_HEADER}' in README.md")

    # End at closing </details>, or after the last markdown table row.
    close_idx = readme_text.find("</details>", table_idx)
    if close_idx != -1:
        end = close_idx + len("</details>")
        if end < len(readme_text) and readme_text[end] == "\n":
            end += 1
        return details_start, end

    pos = table_idx
    last_row_end = table_idx
    while pos < len(readme_text):
        line_end = readme_text.find("\n", pos)
        if line_end == -1:
            line_end = len(readme_text)
        line = readme_text[pos:line_end]
        if line.startswith("|"):
            last_row_end = line_end + 1 if line_end < len(readme_text) else line_end
            pos = line_end + 1 if line_end < len(readme_text) else line_end
            continue
        break
    return details_start, last_row_end


def _replace_readme_table(readme_text: str, table: str) -> str:
    start, end = _locate_interchange_section(readme_text)
    block = _render_details_block(table)
    return readme_text[:start] + block + readme_text[end:]


def update_readme() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    table = render_table()
    README_PATH.write_text(_replace_readme_table(readme, table), encoding="utf-8")
    print(f"Updated {README_PATH} ({len(PUZZLE_TYPES_DICT)} types)")


def check_readme() -> int:
    readme = README_PATH.read_text(encoding="utf-8")
    expected = render_table().strip()
    table_idx = readme.find(TABLE_HEADER)
    if table_idx == -1:
        print("README.md: interchange table not found", file=sys.stderr)
        return 1
    _, end = _locate_interchange_section(readme)
    block = readme[table_idx:end].strip()
    if block.endswith("</details>"):
        block = block[: -len("</details>")].strip()
    if block != expected:
        print(
            "README.md URL interchange table is out of date.\n"
            "Run: PYTHONPATH=src python scripts/generate_format_interchange_table.py --update-readme",
            file=sys.stderr,
        )
        return 1
    print(f"README.md table matches puzzle_types.py ({len(PUZZLE_TYPES_DICT)} types)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Replace the table inside README.md",
    )
    parser.add_argument(
        "--check-readme",
        action="store_true",
        help="Exit 1 if README.md table does not match puzzle_types.py",
    )
    args = parser.parse_args()

    if args.update_readme:
        update_readme()
        return
    if args.check_readme:
        raise SystemExit(check_readme())

    print(render_table(), end="")


if __name__ == "__main__":
    main()
