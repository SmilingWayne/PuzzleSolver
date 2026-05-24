"""
Puzzlink URL parser module.

This module handles parsing of puzz.link URLs and puzzle path headers.
"""

import re
from typing import Dict, Any, Tuple
from urllib.parse import unquote, urlsplit


_PUZZLINK_FIRST_SEG_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")


def looks_like_puzzlink_path(puzzle_path: str) -> bool:
    """Heuristic: first segment is a genre token; avoid penpa/m=edit&p= style strings."""
    s = (puzzle_path or "").strip().lstrip("/")
    if "/" not in s:
        return False
    parts = [p for p in s.split("/") if p != ""]
    if len(parts) < 4:
        return False
    first = parts[0]
    if "=" in first or "&" in first:
        return False
    return bool(_PUZZLINK_FIRST_SEG_RE.match(first))


def parse_puzzlink_input(url: str) -> Dict[str, Any]:
    """Extract the puzz.link payload path from many URL shapes or a bare path.

    Accepts:
    - ``https://puzz.link/p?hebi/10/10/...``
    - ``https://pzplus.tck.mn/p.html?hebi/10/10/...``
    - ``http://pzv.jp/p?hebi/10/10/...``
    - ``?hebi/10/10/...`` (paste without scheme)
    - ``hebi/10/10/...`` (bare path)

    Extra query pairs (e.g. ``&a=...``) are ignored; only the first ``&``-separated
    chunk of the query is used as the puzzle path when it looks like puzz.link.
    """
    raw = (url or "").strip()
    if not raw:
        raise ValueError("puzz.link input must be a non-empty string")

    # Paste-only: "?genre/..." without a scheme
    if raw.startswith("?") and looks_like_puzzlink_path(raw[1:]):
        puzzle_path = raw[1:].split("#", 1)[0].split("&", 1)[0].strip()
        return {"puzzle_path": puzzle_path}

    sp = urlsplit(raw)
    puzzle_path = ""

    if sp.query:
        candidate = unquote(sp.query.split("&", 1)[0]).lstrip("/")
        if looks_like_puzzlink_path(candidate):
            puzzle_path = candidate

    if not puzzle_path and sp.fragment:
        candidate = unquote(sp.fragment).lstrip("/").split("?", 1)[0].split("&", 1)[0]
        if looks_like_puzzlink_path(candidate):
            puzzle_path = candidate

    if not puzzle_path and sp.path:
        path = unquote(sp.path).lstrip("/")
        if path.startswith("?"):
            candidate = path[1:].split("#", 1)[0].split("&", 1)[0]
        else:
            candidate = path.split("#", 1)[0].split("&", 1)[0]
        if looks_like_puzzlink_path(candidate):
            puzzle_path = candidate

    if not puzzle_path:
        raise ValueError(
            f"Cannot extract puzz.link puzzle path from input: {raw[:160]!r}"
        )

    return {"puzzle_path": puzzle_path}


class ParsedPuzzleHeader:
    """Parsed puzzle header information."""

    def __init__(self, puzzle_type: str, num_cols: int, num_rows: int, body: str, skip_shading: bool = True):
        self.puzzle_type = puzzle_type
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.body = body
        self.skip_shading = skip_shading


def parse_puzzle_header(puzzle_path: str) -> ParsedPuzzleHeader:
    """Parse the header of the puzzle, such as: slither/10/10/body_str

    Args:
        puzzle_path: The puzzle path string (e.g., "slither/10/10/abc123")

    Returns:
        ParsedPuzzleHeader with puzzle type, dimensions, body, and shading flag
    """
    urldata = puzzle_path.split("/")
    if len(urldata) > 1 and urldata[1] == 'v:':
        urldata.pop(1)

    puzzle_type = puzzle_type_from_string(urldata[0])
    skip_shading = (puzzle_type != "castle") and (puzzle_type != "hebi")

    if urldata[1] == "b":
        skip_shading = False
        num_cols = int(urldata[2])
        num_rows = int(urldata[3])
        body = urldata[4]
    else:
        num_cols = int(urldata[1])
        num_rows = int(urldata[2])
        body = urldata[3]

    return ParsedPuzzleHeader(
        puzzle_type=puzzle_type,
        num_cols=num_cols,
        num_rows=num_rows,
        body=body,
        skip_shading=skip_shading
    )


def puzzle_type_from_string(type_str: str) -> str:
    """Normalize puzzle type string.

    This is a placeholder that currently just returns the input.
    Actual normalization logic should be imported from puzzle_types module.
    """
    # Import here to avoid circular dependency
    from puzzlekit.formats.puzzle_types import normalize_puzzle_type
    return normalize_puzzle_type(type_str)
