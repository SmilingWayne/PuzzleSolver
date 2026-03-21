import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.formats.penpa_converter import PENPA_PREFIX, PENPA_URLPREFIX, PenpaConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter


def _read_nonempty_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def _resolve_input_urls(args: argparse.Namespace) -> Tuple[str, str]:
    # Priority: --pair-file > (--puzzlink-file/--penpa-file) > (--puzzlink-url/--penpa-url)
    if args.pair_file:
        lines = _read_nonempty_lines(args.pair_file)
        if len(lines) < 2:
            raise ValueError("--pair-file must contain at least 2 non-empty lines.")
        return lines[0], lines[1]

    puzzlink_url = args.puzzlink_url
    penpa_url = args.penpa_url

    if args.puzzlink_file:
        lines = _read_nonempty_lines(args.puzzlink_file)
        if not lines:
            raise ValueError("--puzzlink-file is empty.")
        puzzlink_url = lines[0]

    if args.penpa_file:
        lines = _read_nonempty_lines(args.penpa_file)
        if not lines:
            raise ValueError("--penpa-file is empty.")
        penpa_url = lines[0]

    if not puzzlink_url or not penpa_url:
        raise ValueError(
            "Please provide URLs via --pair-file, or both sides via URL/file arguments."
        )

    return puzzlink_url, penpa_url


def _normalize_penpa_url(url: str) -> str:
    """
    PenpaConverter.decode expects text starting with `m=edit&p=`.
    Accept full Penpa URL and convert it into expected format.
    """
    url = url.strip()
    if url.startswith(PENPA_PREFIX):
        return url
    if url.startswith(PENPA_URLPREFIX):
        frag = url.split("#", 1)[1] if "#" in url else ""
        return frag if frag.startswith(PENPA_PREFIX) else f"{PENPA_PREFIX}{frag}"
    return url


def _detect_format(url: str) -> str:
    u = url.strip()
    if "puzz.link/p?" in u:
        return "puzzlink"
    if u.startswith(PENPA_PREFIX) or u.startswith(PENPA_URLPREFIX):
        return "penpa"
    raise ValueError("Unknown URL format. Please provide puzz.link or penpa URL.")


def decode_url_to_ir(url: str) -> Tuple[str, PuzzleInstance]:
    fmt = _detect_format(url)
    if fmt == "puzzlink":
        return fmt, PuzzlinkConverter().decode(url)
    normalized = _normalize_penpa_url(url)
    return fmt, PenpaConverter().decode(normalized)


def summarize_ir(ir: PuzzleInstance) -> Dict[str, Any]:
    return {
        "grid_type": ir.grid_type,
        "puzzle_type": ir.puzzle_type,
        "rows": ir.rows,
        "cols": ir.cols,
        "margins": ir.margins,
        "cells_count": len(ir.cells),
        "edges_count": len(ir.edges),
        "boxes_count": len(ir.boxes),
        "source": ir.source,
    }


def _diff_dict(
    left: Dict[str, Any], right: Dict[str, Any], max_examples: int
) -> Dict[str, Any]:
    left_keys = set(left.keys())
    right_keys = set(right.keys())
    only_left = sorted(left_keys - right_keys)
    only_right = sorted(right_keys - left_keys)
    common = sorted(left_keys & right_keys)

    changed = []
    for k in common:
        if left[k] != right[k]:
            changed.append(k)

    examples: List[Dict[str, Any]] = []
    for k in changed[:max_examples]:
        examples.append({"key": k, "left": left[k], "right": right[k]})

    return {
        "only_left_count": len(only_left),
        "only_right_count": len(only_right),
        "changed_count": len(changed),
        "only_left_examples": only_left[:max_examples],
        "only_right_examples": only_right[:max_examples],
        "changed_examples": examples,
    }


def _diff_list(left: List[Any], right: List[Any], max_examples: int) -> Dict[str, Any]:
    min_len = min(len(left), len(right))
    changed_indices = [i for i in range(min_len) if left[i] != right[i]]

    examples = []
    for i in changed_indices[:max_examples]:
        examples.append({"index": i, "left": left[i], "right": right[i]})

    extra_left = left[min_len : min_len + max_examples]
    extra_right = right[min_len : min_len + max_examples]

    return {
        "left_len": len(left),
        "right_len": len(right),
        "changed_count": len(changed_indices),
        "extra_left_count": max(0, len(left) - min_len),
        "extra_right_count": max(0, len(right) - min_len),
        "changed_examples": examples,
        "extra_left_examples": extra_left,
        "extra_right_examples": extra_right,
    }


def compare_irs(left: PuzzleInstance, right: PuzzleInstance, max_examples: int = 20) -> Dict[str, Any]:
    ln = left.normalize()
    rn = right.normalize()

    result = {
        "semantic_equal": left.semantic_equals(right),
        "meta": {
            "rows_equal": ln["rows"] == rn["rows"],
            "cols_equal": ln["cols"] == rn["cols"],
            "margins_equal": ln["margins"] == rn["margins"],
            "grid_type_equal": ln["grid_type"] == rn["grid_type"],
            "rows": (ln["rows"], rn["rows"]),
            "cols": (ln["cols"], rn["cols"]),
            "margins": (ln["margins"], rn["margins"]),
            "grid_type": (ln["grid_type"], rn["grid_type"]),
        },
        "cells": _diff_dict(ln["cells"], rn["cells"], max_examples),
        "edges": _diff_dict(ln["edges"], rn["edges"], max_examples),
        "boxes": _diff_list(ln["boxes"], rn["boxes"], max_examples),
    }
    return result


def _print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def print_summary(tag: str, ir: PuzzleInstance) -> None:
    s = summarize_ir(ir)
    _print_section(tag)
    print(json.dumps(s, ensure_ascii=False, indent=2))


def print_diff_report(report: Dict[str, Any]) -> None:
    _print_section("IR Comparison")
    print(f"semantic_equal: {report['semantic_equal']}")
    print("meta:", json.dumps(report["meta"], ensure_ascii=False))
    print("cells:", json.dumps(report["cells"], ensure_ascii=False))
    print("edges:", json.dumps(report["edges"], ensure_ascii=False))
    print("boxes:", json.dumps(report["boxes"], ensure_ascii=False))


def _safe_roundtrip(fmt: str, ir: PuzzleInstance) -> Dict[str, Any]:
    try:
        if fmt == "puzzlink":
            encoded = PuzzlinkConverter().encode(ir)
            decoded = PuzzlinkConverter().decode(encoded)
        elif fmt == "penpa":
            encoded = PenpaConverter().encode(ir)
            decoded = PenpaConverter().decode(encoded)
        else:
            return {"ok": False, "error": f"Unknown format: {fmt}"}

        return {
            "ok": True,
            "encoded_preview": encoded[:120],
            "semantic_equal_after_roundtrip": ir.semantic_equals(decoded),
            "encoded_length": len(encoded),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def dump_normalized(prefix: str, left: PuzzleInstance, right: PuzzleInstance, report: Dict[str, Any]) -> None:
    p = Path(prefix)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(f"{prefix}_left.normalized.json", "w", encoding="utf-8") as f:
        json.dump(left.normalize(), f, ensure_ascii=False, indent=2)
    with open(f"{prefix}_right.normalized.json", "w", encoding="utf-8") as f:
        json.dump(right.normalize(), f, ensure_ascii=False, indent=2)
    with open(f"{prefix}_diff.report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Debug IR equivalence between puzzlink and penpa URLs."
    )
    parser.add_argument("--puzzlink-url", type=str, default="", help="puzz.link URL")
    parser.add_argument("--penpa-url", type=str, default="", help="penpa URL or m=edit&p=...")
    parser.add_argument(
        "--puzzlink-file",
        type=str,
        default="",
        help="read puzz.link URL from file (first non-empty line)",
    )
    parser.add_argument(
        "--penpa-file",
        type=str,
        default="",
        help="read penpa URL from file (first non-empty line)",
    )
    parser.add_argument(
        "--pair-file",
        type=str,
        default="",
        help="read two URLs from one file: line1=puzzlink, line2=penpa",
    )
    parser.add_argument("--max-diff", type=int, default=20, help="max diff examples per section")
    parser.add_argument(
        "--check-roundtrip",
        action="store_true",
        help="also run format self roundtrip checks",
    )
    parser.add_argument(
        "--dump-prefix",
        type=str,
        default="",
        help="optional file prefix to dump normalized json and diff report",
    )
    args = parser.parse_args()

    puzzlink_url, penpa_url = _resolve_input_urls(args)

    left_fmt, left_ir = decode_url_to_ir(puzzlink_url)
    right_fmt, right_ir = decode_url_to_ir(penpa_url)

    print_summary(f"Left ({left_fmt})", left_ir)
    print_summary(f"Right ({right_fmt})", right_ir)

    report = compare_irs(left_ir, right_ir, max_examples=args.max_diff)
    print_diff_report(report)

    if args.check_roundtrip:
        _print_section("Roundtrip Checks")
        print("left:", json.dumps(_safe_roundtrip(left_fmt, left_ir), ensure_ascii=False))
        print("right:", json.dumps(_safe_roundtrip(right_fmt, right_ir), ensure_ascii=False))

    if args.dump_prefix:
        dump_normalized(args.dump_prefix, left_ir, right_ir, report)
        print(f"\nSaved debug artifacts with prefix: {args.dump_prefix}")


if __name__ == "__main__":
    main()

# PYTHONPATH=src python src/puzzlekit/formats/debug.py --pair-file src/puzzlekit/formats/temp/pair.txt