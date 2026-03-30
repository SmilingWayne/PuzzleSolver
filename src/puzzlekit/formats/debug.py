import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Iterable
import copy

from puzzlekit.formats.base import PuzzleInstance
from puzzlekit.formats.penpa_converter import PENPA_PREFIX, PENPA_URLPREFIX, PenpaConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter, parse_puzzlink_input


def _read_nonempty_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def _first_line_from_file(path: str, flag_name: str) -> str:
    lines = _read_nonempty_lines(path)
    if not lines:
        raise ValueError(f"{flag_name} is empty.")
    return lines[0]


def _resolve_two_inputs(args: argparse.Namespace) -> Tuple[str, str]:
    """
    Resolve two inputs (left/right) with backward compatibility.

    Priority:
    - --pair-file (two non-empty lines)
    - --left/--right
    - --left-file/--right-file
    - legacy: --puzzlink-url/--penpa-url (+ corresponding *-file)
    """
    # 1) pair-file
    if args.pair_file:
        lines = _read_nonempty_lines(args.pair_file)
        if len(lines) < 2:
            raise ValueError("--pair-file must contain at least 2 non-empty lines.")
        return lines[0], lines[1]

    # 2) explicit left/right
    left = args.left
    right = args.right

    if args.left_file:
        left = _first_line_from_file(args.left_file, "--left-file")
    if args.right_file:
        right = _first_line_from_file(args.right_file, "--right-file")

    if left and right:
        return left, right

    # 3) legacy flags (kept for compatibility)
    puzzlink_url = args.puzzlink_url
    penpa_url = args.penpa_url

    if args.puzzlink_file:
        puzzlink_url = _first_line_from_file(args.puzzlink_file, "--puzzlink-file")
    if args.penpa_file:
        penpa_url = _first_line_from_file(args.penpa_file, "--penpa-file")

    if puzzlink_url and penpa_url:
        return puzzlink_url, penpa_url

    raise ValueError(
        "Please provide two inputs via --pair-file, or --left/--right, "
        "or --left-file/--right-file (legacy: --puzzlink-url/--penpa-url)."
    )


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
    if u.startswith(PENPA_PREFIX) or u.startswith(PENPA_URLPREFIX):
        return "penpa"
    if "#" in u:
        frag = u.split("#", 1)[1]
        if "m=" in frag and "p=" in frag:
            return "penpa"
    try:
        parse_puzzlink_input(u)
        return "puzzlink"
    except ValueError:
        pass
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


def _parse_ignore_paths(raw: str) -> List[str]:
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def _iter_dict_items(obj: Any) -> Iterable[Tuple[Any, Any]]:
    if isinstance(obj, dict):
        return obj.items()
    return []


def _apply_ignore_paths(data: Any, ignore_paths: List[str]) -> Any:
    """
    Remove fields from a nested JSON-like structure.

    Path syntax:
    - dot-separated keys, e.g. "cells", "meta.rows", "cells.*.number.number_style"
    - "*" matches all dict keys / list items at that level
    """
    if not ignore_paths:
        return data
    root = copy.deepcopy(data)

    def _delete_at(node: Any, parts: List[str]) -> None:
        if not parts:
            return
        head, *tail = parts

        # delete the node itself (parent handles actual deletion)
        if isinstance(node, dict):
            if head == "*":
                for k in list(node.keys()):
                    if tail:
                        _delete_at(node.get(k), tail)
                    else:
                        node.pop(k, None)
                return

            if head not in node:
                return

            if not tail:
                node.pop(head, None)
                return
            _delete_at(node.get(head), tail)
            return

        if isinstance(node, list):
            if head == "*":
                for item in node:
                    _delete_at(item, tail)
                return
            # numeric index for lists
            if head.isdigit():
                idx = int(head)
                if 0 <= idx < len(node):
                    if not tail:
                        node[idx] = None
                    else:
                        _delete_at(node[idx], tail)
            return

    for path in ignore_paths:
        _delete_at(root, path.split("."))
    return root


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _value_equal_ratio(left: Dict[str, Any], right: Dict[str, Any]) -> float:
    lk = set(left.keys())
    rk = set(right.keys())
    common = lk & rk
    if not common:
        return 1.0 if not lk and not rk else 0.0
    eq = sum(1 for k in common if left.get(k) == right.get(k))
    return eq / len(common)


def _similarity_report(ln: Dict[str, Any], rn: Dict[str, Any]) -> Dict[str, Any]:
    cells_l = ln.get("cells", {}) if isinstance(ln.get("cells"), dict) else {}
    cells_r = rn.get("cells", {}) if isinstance(rn.get("cells"), dict) else {}
    edges_l = ln.get("edges", {}) if isinstance(ln.get("edges"), dict) else {}
    edges_r = rn.get("edges", {}) if isinstance(rn.get("edges"), dict) else {}
    boxes_l = ln.get("boxes", []) if isinstance(ln.get("boxes"), list) else []
    boxes_r = rn.get("boxes", []) if isinstance(rn.get("boxes"), list) else []

    # boxes: simple positional equality ratio on the overlapping prefix
    min_len = min(len(boxes_l), len(boxes_r))
    if min_len == 0:
        boxes_eq_ratio = 1.0 if not boxes_l and not boxes_r else 0.0
    else:
        boxes_eq_ratio = sum(1 for i in range(min_len) if boxes_l[i] == boxes_r[i]) / min_len

    return {
        "cells": {
            "key_jaccard": _jaccard(set(cells_l.keys()), set(cells_r.keys())),
            "value_equal_ratio_on_common_keys": _value_equal_ratio(cells_l, cells_r),
            "left_count": len(cells_l),
            "right_count": len(cells_r),
        },
        "edges": {
            "key_jaccard": _jaccard(set(edges_l.keys()), set(edges_r.keys())),
            "value_equal_ratio_on_common_keys": _value_equal_ratio(edges_l, edges_r),
            "left_count": len(edges_l),
            "right_count": len(edges_r),
        },
        "boxes": {
            "left_len": len(boxes_l),
            "right_len": len(boxes_r),
            "equal_ratio_on_common_prefix": boxes_eq_ratio,
        },
        "meta": {
            "grid_type_equal": ln.get("grid_type") == rn.get("grid_type"),
            "puzzle_type_equal": ln.get("puzzle_type") == rn.get("puzzle_type"),
            "rows_equal": ln.get("rows") == rn.get("rows"),
            "cols_equal": ln.get("cols") == rn.get("cols"),
            "margins_equal": ln.get("margins") == rn.get("margins"),
        },
    }


def compare_irs(
    left: PuzzleInstance,
    right: PuzzleInstance,
    max_examples: int = 20,
    ignore_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    ignore_paths = ignore_paths or []

    # normalize -> apply ignores
    ln_raw = left.normalize()
    rn_raw = right.normalize()
    ln = _apply_ignore_paths(ln_raw, ignore_paths)
    rn = _apply_ignore_paths(rn_raw, ignore_paths)

    # tolerate missing keys after ignore filtering
    ln_cells = ln.get("cells", {}) if isinstance(ln.get("cells", {}), dict) else {}
    rn_cells = rn.get("cells", {}) if isinstance(rn.get("cells", {}), dict) else {}
    ln_edges = ln.get("edges", {}) if isinstance(ln.get("edges", {}), dict) else {}
    rn_edges = rn.get("edges", {}) if isinstance(rn.get("edges", {}), dict) else {}
    ln_boxes = ln.get("boxes", []) if isinstance(ln.get("boxes", []), list) else []
    rn_boxes = rn.get("boxes", []) if isinstance(rn.get("boxes", []), list) else []

    ln_rows = ln.get("rows")
    rn_rows = rn.get("rows")
    ln_cols = ln.get("cols")
    rn_cols = rn.get("cols")
    ln_margins = ln.get("margins")
    rn_margins = rn.get("margins")
    ln_grid = ln.get("grid_type")
    rn_grid = rn.get("grid_type")
    ln_type = ln.get("puzzle_type")
    rn_type = rn.get("puzzle_type")

    result = {
        "semantic_equal": ln == rn,
        "ignore_paths": ignore_paths,
        "similarity": _similarity_report(ln, rn),
        "meta": {
            "rows_equal": ln_rows == rn_rows,
            "cols_equal": ln_cols == rn_cols,
            "margins_equal": ln_margins == rn_margins,
            "grid_type_equal": ln_grid == rn_grid,
            "puzzle_type_equal": ln_type == rn_type,
            "rows": (ln_rows, rn_rows),
            "cols": (ln_cols, rn_cols),
            "margins": (ln_margins, rn_margins),
            "grid_type": (ln_grid, rn_grid),
            "puzzle_type": (ln_type, rn_type),
        },
        "cells": _diff_dict(ln_cells, rn_cells, max_examples),
        "edges": _diff_dict(ln_edges, rn_edges, max_examples),
        "boxes": _diff_list(ln_boxes, rn_boxes, max_examples),
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
    if report.get("ignore_paths"):
        print("ignore_paths:", json.dumps(report["ignore_paths"], ensure_ascii=False))
    if report.get("similarity") is not None:
        print("similarity:", json.dumps(report["similarity"], ensure_ascii=False))
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


def dump_normalized(
    prefix: str,
    left: PuzzleInstance,
    right: PuzzleInstance,
    report: Dict[str, Any],
    ignore_paths: Optional[List[str]] = None,
) -> None:
    p = Path(prefix)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(f"{prefix}_left.normalized.json", "w", encoding="utf-8") as f:
        json.dump(left.normalize(), f, ensure_ascii=False, indent=2)
    with open(f"{prefix}_right.normalized.json", "w", encoding="utf-8") as f:
        json.dump(right.normalize(), f, ensure_ascii=False, indent=2)
    if ignore_paths:
        with open(f"{prefix}_left.filtered.json", "w", encoding="utf-8") as f:
            json.dump(_apply_ignore_paths(left.normalize(), ignore_paths), f, ensure_ascii=False, indent=2)
        with open(f"{prefix}_right.filtered.json", "w", encoding="utf-8") as f:
            json.dump(_apply_ignore_paths(right.normalize(), ignore_paths), f, ensure_ascii=False, indent=2)
    with open(f"{prefix}_diff.report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

# 🔧 新增辅助函数（放在 main() 之前或之后都可以）
def _setup_logging(args: argparse.Namespace) -> None:
    """Configure logging based on CLI arguments."""
    
    # 决定日志级别
    if args.debug or args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose >= 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    # 决定输出目标
    handlers = []
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, mode="w", encoding="utf-8"))
    else:
        handlers.append(logging.StreamHandler(sys.stdout))
    
    # 配置 root logger（force=True：脚本入口强制接管输出，库代码不应 basicConfig）
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
        force=True,
    )
    
    # 精准控制 puzzlekit 的日志级别
    logging.getLogger("puzzlekit").setLevel(level)
    
    # 屏蔽第三方库噪音（按需调整）
    for noisy in ["urllib3", "httpx", "PIL", "matplotlib"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    
    # 如果是 debug 模式，打印配置信息（验证是否生效）
    logger = logging.getLogger(__name__)
    logger.debug("Logging configured: level=%s, handlers=%s", 
                 logging.getLevelName(level), [type(h).__name__ for h in handlers])

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two puzzle URLs (puzz.link / penpa) by IR diff + similarity."
    )
    # New generic interface
    parser.add_argument("--left", type=str, default="", help="Left input: puzz.link URL or penpa URL/payload")
    parser.add_argument("--right", type=str, default="", help="Right input: puzz.link URL or penpa URL/payload")
    parser.add_argument("--left-file", type=str, default="", help="Read left input from file (first non-empty line)")
    parser.add_argument("--right-file", type=str, default="", help="Read right input from file (first non-empty line)")

    # Legacy interface (kept for compatibility)
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
        "--ignore",
        type=str,
        default="",
        help=(
            "Comma-separated ignore paths applied to normalized IR before diff. "
            "Examples: 'meta.source,cells.*.number.number_style,edges'. "
            "Supported: dot paths with '*' wildcard."
        ),
    )
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
    
    # 🔧 新增调试参数
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable DEBUG logging for puzzlekit"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count", 
        default=0,
        help="Increase verbosity: -v=INFO, -vv=DEBUG"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="",
        help="Optional: write logs to file instead of stdout"
    )
    
    args = parser.parse_args()
    
    _setup_logging(args)

    left_url, right_url = _resolve_two_inputs(args)
    ignore_paths = _parse_ignore_paths(args.ignore)

    left_fmt, left_ir = decode_url_to_ir(left_url)
    right_fmt, right_ir = decode_url_to_ir(right_url)

    print_summary(f"Left ({left_fmt})", left_ir)
    print_summary(f"Right ({right_fmt})", right_ir)

    report = compare_irs(left_ir, right_ir, max_examples=args.max_diff, ignore_paths=ignore_paths)
    print_diff_report(report)

    if args.check_roundtrip:
        _print_section("Roundtrip Checks")
        print("left:", json.dumps(_safe_roundtrip(left_fmt, left_ir), ensure_ascii=False))
        print("right:", json.dumps(_safe_roundtrip(right_fmt, right_ir), ensure_ascii=False))

    if args.dump_prefix:
        dump_normalized(args.dump_prefix, left_ir, right_ir, report, ignore_paths=ignore_paths)
        print(f"\nSaved debug artifacts with prefix: {args.dump_prefix}")


if __name__ == "__main__":
    main()

# python src/puzzlekit/formats/debug.py --pair-file src/puzzlekit/formats/temp/pair.txt