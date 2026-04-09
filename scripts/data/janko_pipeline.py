"""
Generic Janko dataset cleanup scaffold.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from puzzlekit.formats.janko_converter import JankoConverter
from puzzlekit.formats.penpa_converter import PenpaConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

FixFunc = Callable[[str], str]


@dataclass
class CaseResult:
    case_id: str
    success_decode: bool
    decode_error: str | None = None
    success_puzzlink: bool = False
    puzzlink_error: str | None = None
    success_penpa: bool = False
    penpa_error: str | None = None


def _normalize_whitespace(raw: str) -> str:
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    for line in lines:
        tokens = line.strip().split()
        out.append(" ".join(tokens) if tokens else "")
    return "\n".join(out).strip()


def _remove_blank_lines(raw: str) -> str:
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join([line for line in lines if line.strip() != ""]).strip()


def _parse_dims_and_rows(raw: str) -> Tuple[int, int, List[List[str]]]:
    lines = [x for x in raw.split("\n") if x.strip() != ""]
    if not lines:
        raise ValueError("empty puzzle string")
    dims = lines[0].split()
    if len(dims) != 2:
        raise ValueError(f"invalid dimensions line: {lines[0]!r}")
    rows = int(dims[0])
    cols = int(dims[1])
    parsed_rows: List[List[str]] = [line.split() for line in lines[1:]]
    return rows, cols, parsed_rows


def _normalize_dims_from_rows(raw: str) -> str:
    _, _, parsed_rows = _parse_dims_and_rows(raw)
    if not parsed_rows:
        return raw.strip()
    inferred_rows = len(parsed_rows)
    inferred_cols = max((len(r) for r in parsed_rows), default=0)
    normalized_lines = [f"{inferred_rows} {inferred_cols}"]
    for row_tokens in parsed_rows:
        if len(row_tokens) < inferred_cols:
            row_tokens = row_tokens + (["-"] * (inferred_cols - len(row_tokens)))
        elif len(row_tokens) > inferred_cols:
            row_tokens = row_tokens[:inferred_cols]
        normalized_lines.append(" ".join(row_tokens))
    return "\n".join(normalized_lines).strip()


def _pad_or_truncate_rows(raw: str) -> str:
    rows, cols, parsed_rows = _parse_dims_and_rows(raw)
    normalized = [f"{rows} {cols}"]
    body = parsed_rows[:rows]
    if len(body) < rows:
        body.extend([["-"] * cols for _ in range(rows - len(body))])
    for row_tokens in body:
        if len(row_tokens) < cols:
            row_tokens = row_tokens + (["-"] * (cols - len(row_tokens)))
        elif len(row_tokens) > cols:
            row_tokens = row_tokens[:cols]
        normalized.append(" ".join(row_tokens))
    return "\n".join(normalized).strip()


def _trim_trailing_annotation_after_grid(raw: str) -> str:
    """
    Keep declared grid rows and trim trailing annotation blocks (e.g. [moves], ';' logs).

    Safety rule:
    - Only trim when there are extra lines after declared rows AND those extra lines
      look non-grid-like (contain ';', brackets, or irregular token counts).
    - If extra lines look like a valid secondary matrix (same column count),
      do not trim (helps avoid damaging formats like board+region).
    """
    lines = [x for x in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n") if x.strip() != ""]
    if not lines:
        return raw
    dims = lines[0].split()
    if len(dims) != 2:
        return raw
    try:
        rows = int(dims[0])
        cols = int(dims[1])
    except ValueError:
        return raw

    body = lines[1:]
    if len(body) <= rows:
        return raw
    declared = body[:rows]
    extras = body[rows:]

    def _looks_non_grid(line: str) -> bool:
        if ";" in line or "[" in line or "]" in line:
            return True
        tokens = line.split()
        if len(tokens) != cols:
            return True
        return False

    if any(_looks_non_grid(line) for line in extras):
        return "\n".join([lines[0]] + declared).strip()
    return raw


def _map_grid_tokens(raw: str, mapping: Dict[str, str]) -> str:
    """
    Generic grid token mapper.
    Only maps the declared grid area (first `rows` body lines).
    """
    if not mapping:
        return raw
    rows, cols, parsed_rows = _parse_dims_and_rows(raw)
    normalized = [f"{rows} {cols}"]
    for row_tokens in parsed_rows[:rows]:
        mapped = [mapping.get(tok, tok) for tok in row_tokens]
        normalized.append(" ".join(mapped))
    for row_tokens in parsed_rows[rows:]:
        normalized.append(" ".join(row_tokens))
    return "\n".join(normalized).strip()


FIX_STRATEGIES: Dict[str, FixFunc] = {
    "normalize_whitespace": _normalize_whitespace,
    "remove_blank_lines": _remove_blank_lines,
    "trim_trailing_annotation_after_grid": _trim_trailing_annotation_after_grid,
    "normalize_dims_from_rows": _normalize_dims_from_rows,
    "pad_or_truncate_rows": _pad_or_truncate_rows,
    "map_grid_tokens": lambda raw: raw,  # handled in _apply_fixes with user mapping
}


def _parse_token_map(args: argparse.Namespace) -> Dict[str, str]:
    if getattr(args, "grid_token_map_file", ""):
        path = Path(args.grid_token_map_file)
        mapping = json.loads(path.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in mapping.items()}

    raw_map = getattr(args, "grid_token_map", "").strip()
    if raw_map:
        out: Dict[str, str] = {}
        for pair in raw_map.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" not in pair:
                raise ValueError(f"invalid token map pair: {pair!r}, expected src:dst")
            src, dst = pair.split(":", 1)
            out[src.strip()] = dst.strip()
        return out

    return {}


def _apply_fixes(
    raw: str,
    strategies: List[str],
    field_name: str,
    token_map: Dict[str, str],
    token_map_targets: str,
) -> Tuple[str, List[str]]:
    applied: List[str] = []
    current = raw
    for strategy_name in strategies:
        func = FIX_STRATEGIES.get(strategy_name)
        if func is None:
            raise ValueError(f"unknown fix strategy: {strategy_name}")
        if strategy_name == "trim_trailing_annotation_after_grid" and field_name != "solution":
            continue
        if strategy_name == "map_grid_tokens":
            if token_map_targets not in ("both", field_name):
                continue
            if not token_map:
                continue
            new_value = _map_grid_tokens(current, token_map)
        else:
            new_value = func(current)
        if new_value != current:
            applied.append(strategy_name)
            current = new_value
    return current, applied


def _error_code_from_exception(exc: Exception) -> str:
    return f"{type(exc).__name__}:{str(exc).splitlines()[0][:200]}"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _infer_puzzle_type(dataset: Dict[str, Any], fallback: str) -> str:
    name = str(dataset.get("name", "")).strip().lower()
    return name or fallback


def run_pipeline(args: argparse.Namespace) -> Dict[str, Any]:
    dataset_path = Path(args.dataset)
    raw_dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    working_dataset = copy.deepcopy(raw_dataset)
    puzzle_type = args.puzzle_type or _infer_puzzle_type(working_dataset, "nurikabe")
    token_map = _parse_token_map(args)
    token_map_targets = args.grid_token_map_targets

    janko = JankoConverter()
    puzzlink = PuzzlinkConverter()
    penpa = PenpaConverter()

    now = datetime.now(timezone.utc).isoformat()
    results: List[CaseResult] = []
    error_to_cases: Dict[str, List[str]] = defaultdict(list)
    changed_cases: List[str] = []
    dedupe_removed_cases: List[str] = []
    dedupe_groups: Dict[str, Dict[str, Any]] = {}
    seen_key_to_kept_case: Dict[str, str] = {}
    filtered_data_map: Dict[str, Any] = {}

    data_map = working_dataset.get("data", {})
    for case_id, case in data_map.items():
        problem = str(case.get("problem", ""))
        solution = str(case.get("solution", ""))
        case_source = str(case.get("source", "")).strip()
        applied_problem: List[str] = []
        applied_solution: List[str] = []

        if args.apply_fixes and args.fix_strategies:
            problem, applied_problem = _apply_fixes(
                problem,
                args.fix_strategies,
                "problem",
                token_map,
                token_map_targets,
            )
            if solution:
                solution, applied_solution = _apply_fixes(
                    solution,
                    args.fix_strategies,
                    "solution",
                    token_map,
                    token_map_targets,
                )
            if applied_problem or applied_solution:
                case["problem"] = problem
                if solution:
                    case["solution"] = solution
                changed_cases.append(case_id)

        # Optional dedupe happens after normalization fixes and before conversion.
        if args.dedupe:
            if args.dedupe_key == "problem":
                dedupe_key = problem.strip()
            else:
                dedupe_key = f"{problem.strip()}\n---\n{solution.strip()}"

            if dedupe_key in seen_key_to_kept_case:
                kept = seen_key_to_kept_case[dedupe_key]
                dedupe_removed_cases.append(case_id)
                group = dedupe_groups.setdefault(kept, {"removed": []})
                group["removed"].append(case_id)
                continue
            seen_key_to_kept_case[dedupe_key] = case_id

        filtered_data_map[case_id] = case

        case_result = CaseResult(case_id=case_id, success_decode=False)
        try:
            inst = janko.decode(problem, puzzle_type=puzzle_type)
            # Prefer per-case source URL from dataset when available.
            # This avoids writing generic "janko.at" into exported URLs.
            if case_source:
                inst.source = case_source
                inst.metadata["source_url"] = case_source
            case_result.success_decode = True
        except Exception as exc:  # noqa: BLE001
            error_code = _error_code_from_exception(exc)
            case_result.decode_error = error_code
            error_to_cases[error_code].append(case_id)
            results.append(case_result)
            continue

        if args.augment_puzzlink:
            try:
                # case.setdefault("artifacts", {})["puzzlink_url"] = puzzlink.encode(inst)
                case["puzzlink_url"] = puzzlink.encode(inst)
                case_result.success_puzzlink = True
            except Exception as exc:  # noqa: BLE001
                case_result.puzzlink_error = _error_code_from_exception(exc)
                error_to_cases[f"puzzlink::{case_result.puzzlink_error}"].append(case_id)

        if args.augment_penpa:
            try:
                # case.setdefault("artifacts", {})["penpa_url"] = penpa.encode(inst)
                case["penpa_url"] = penpa.encode(inst)
                case_result.success_penpa = True
            except Exception as exc:  # noqa: BLE001
                case_result.penpa_error = _error_code_from_exception(exc)
                error_to_cases[f"penpa::{case_result.penpa_error}"].append(case_id)

        if args.write_status:
            case["_pipeline"] = {
                "updated_at": now,
                "puzzle_type": puzzle_type,
                "decode_ok": case_result.success_decode,
                "decode_error": case_result.decode_error,
                "puzzlink_ok": case_result.success_puzzlink if args.augment_puzzlink else None,
                "puzzlink_error": case_result.puzzlink_error if args.augment_puzzlink else None,
                "penpa_ok": case_result.success_penpa if args.augment_penpa else None,
                "penpa_error": case_result.penpa_error if args.augment_penpa else None,
                "fixes_applied_problem": applied_problem,
                "fixes_applied_solution": applied_solution,
            }

        results.append(case_result)

    # Persist deduped map (or original map if dedupe disabled)
    if args.dedupe:
        working_dataset["data"] = filtered_data_map
        if "count" in working_dataset:
            working_dataset["count"] = len(filtered_data_map)
        if "count_sol" in working_dataset:
            working_dataset["count_sol"] = len(filtered_data_map)

    total = len(results)
    decode_ok = sum(1 for r in results if r.success_decode)
    puzzlink_ok = sum(1 for r in results if r.success_puzzlink)
    penpa_ok = sum(1 for r in results if r.success_penpa)

    top_errors = sorted(
        (
            {"error": err, "count": len(case_ids), "examples": case_ids[: args.max_error_examples]}
            for err, case_ids in error_to_cases.items()
        ),
        key=lambda x: x["count"],
        reverse=True,
    )

    report: Dict[str, Any] = {
        "dataset": str(dataset_path),
        "timestamp_utc": now,
        "puzzle_type": puzzle_type,
        "total_cases": total,
        "decode": {
            "ok": decode_ok,
            "fail": total - decode_ok,
            "ok_ratio": round((decode_ok / total), 6) if total else 0.0,
        },
        "puzzlink": {
            "requested": args.augment_puzzlink,
            "ok": puzzlink_ok,
            "ok_ratio_over_total": round((puzzlink_ok / total), 6) if total else 0.0,
            "ok_ratio_over_decoded": round((puzzlink_ok / decode_ok), 6) if decode_ok else 0.0,
        },
        "penpa": {
            "requested": args.augment_penpa,
            "ok": penpa_ok,
            "ok_ratio_over_total": round((penpa_ok / total), 6) if total else 0.0,
            "ok_ratio_over_decoded": round((penpa_ok / decode_ok), 6) if decode_ok else 0.0,
        },
        "fix": {
            "applied": bool(args.apply_fixes and args.fix_strategies),
            "strategies": args.fix_strategies,
            "grid_token_map": token_map,
            "grid_token_map_targets": token_map_targets,
            "changed_cases_count": len(changed_cases),
            "changed_case_examples": changed_cases[: args.max_error_examples],
        },
        "dedupe": {
            "enabled": bool(args.dedupe),
            "key": args.dedupe_key,
            "removed_count": len(dedupe_removed_cases),
            "removed_examples": dedupe_removed_cases[: args.max_error_examples],
            "group_examples": [
                {"kept": kept, "removed": meta["removed"][: args.max_error_examples]}
                for kept, meta in list(dedupe_groups.items())[: args.max_error_examples]
            ],
            "remaining_cases": len(working_dataset.get("data", {})),
        },
        "top_errors": top_errors,
    }

    if args.output_report:
        report_path = Path(args.output_report)
        _ensure_parent(report_path)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.output_dataset:
        out_dataset = Path(args.output_dataset)
        _ensure_parent(out_dataset)
        out_dataset.write_text(json.dumps(working_dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generic Janko dataset cleanup scaffold")
    parser.add_argument("--dataset", required=True, help="Path to dataset json file")
    parser.add_argument("--puzzle-type", default="", help="Puzzle type for Janko decode")
    parser.add_argument("--apply-fixes", action="store_true", help="Enable fix strategies")
    parser.add_argument(
        "--fix-strategies",
        nargs="*",
        default=[],
        choices=sorted(FIX_STRATEGIES.keys()),
        help="Fix strategies to apply in order",
    )
    parser.add_argument("--augment-puzzlink", action="store_true", help="Write puzz.link URLs")
    parser.add_argument("--augment-penpa", action="store_true", help="Write penpa URLs")
    parser.add_argument("--write-status", action="store_true", help="Write case._pipeline")
    parser.add_argument(
        "--grid-token-map",
        default="",
        help="Custom mapping for grid token normalization, format: '1:w,2:b,x:o'",
    )
    parser.add_argument(
        "--grid-token-map-file",
        default="",
        help="Path to JSON token mapping file, e.g. {\"1\":\"w\",\"2\":\"b\"}",
    )
    parser.add_argument(
        "--grid-token-map-targets",
        default="both",
        choices=["problem", "solution", "both"],
        help="Where token mapping applies when using map_grid_tokens",
    )
    parser.add_argument(
        "--output-report",
        default="scripts/data/reports/janko_pipeline_report.json",
        help="Path for JSON report output",
    )
    parser.add_argument("--output-dataset", default="", help="Path for updated dataset json")
    parser.add_argument("--max-error-examples", type=int, default=10, help="Max error examples")
    parser.add_argument("--dedupe", action="store_true", help="Remove duplicate cases before output")
    parser.add_argument(
        "--dedupe-key",
        default="problem",
        choices=["problem", "problem_solution"],
        help="Duplicate criteria: problem only, or problem+solution",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    print(json.dumps(run_pipeline(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


# ASSETS_SRC="/Users/apple/Desktop/puzzlekit-dataset/assets/" \
# GRID_TOKEN_MAP_FILE="scripts/data/maps/map.json" \
# GRID_TOKEN_MAP_TARGETS="problem" \
# AUGMENT_PUZZLINK=1 \
# DEDUPE=1 \
# DEDUPE_KEY=problem \
# SYNC_BACK=1 \
# bash scripts/run_dataset_flow.sh slitherlink review