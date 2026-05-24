#!/usr/bin/env bash
set -euo pipefail

# One-command review/apply flow for dataset sync + clean.
#
# Usage:
#   bash scripts/run_dataset_flow.sh nurikabe review
#   bash scripts/run_dataset_flow.sh nurikabe apply
#   ASSETS_SRC="/Users/apple/Desktop/puzzlekit-dataset/assets/" \
#     bash scripts/run_dataset_flow.sh masyu review
#
# What it does:
# 1) Sync external assets -> local assets (apply mode).
# 2) Run janko pipeline to a temp cleaned file.
# 3) Produce human review artifacts:
#    - JSON report
#    - Unified diff file
# 4) In review mode: ask confirm before replacing original dataset.
#    In apply mode: replace directly.
# 5) Optional: sync local assets back to external assets.

PUZZLE_KEY="${1:-nurikabe}"
MODE="${2:-review}"  # review | apply

ASSETS_SRC="${ASSETS_SRC:-/Users/apple/Desktop/puzzlekit-dataset/assets/}"
ASSETS_DST="${ASSETS_DST:-assets/}"

DATASET_PATH=""
PUZZLE_TYPE=""
FIX_STRATEGIES="normalize_whitespace remove_blank_lines trim_trailing_annotation_after_grid normalize_dims_from_rows"
GRID_TOKEN_MAP="${GRID_TOKEN_MAP:-}"
GRID_TOKEN_MAP_FILE="${GRID_TOKEN_MAP_FILE:-}"
GRID_TOKEN_MAP_TARGETS="${GRID_TOKEN_MAP_TARGETS:-both}"
SYNC_BACK="${SYNC_BACK:-0}"  # 1 => local -> external after write
AUGMENT_PUZZLINK="${AUGMENT_PUZZLINK:-0}"  # 1 => write puzz.link URL
AUGMENT_PENPA="${AUGMENT_PENPA:-0}"        # 1 => write penpa URL
WRITE_STATUS="${WRITE_STATUS:-0}"          # 1 => write _pipeline status
DEDUPE="${DEDUPE:-0}"                      # 1 => dedupe cases
DEDUPE_KEY="${DEDUPE_KEY:-problem}"        # problem | problem_solution

case "$PUZZLE_KEY" in
  nurikabe)
    DATASET_PATH="assets/data/Nurikabe/Nurikabe_dataset.json"
    PUZZLE_TYPE="nurikabe"
    FIX_STRATEGIES="normalize_whitespace remove_blank_lines trim_trailing_annotation_after_grid normalize_dims_from_rows"
    ;;
  slitherlink)
    DATASET_PATH="assets/data/Slitherlink/Slitherlink_dataset.json"
    PUZZLE_TYPE="slitherlink"
    FIX_STRATEGIES="normalize_whitespace remove_blank_lines trim_trailing_annotation_after_grid normalize_dims_from_rows"
    ;;
  masyu)
    DATASET_PATH="assets/data/Masyu/Masyu_dataset.json"
    PUZZLE_TYPE="masyu"
    FIX_STRATEGIES="normalize_whitespace remove_blank_lines map_grid_tokens"
    if [[ -z "$GRID_TOKEN_MAP" ]]; then
      GRID_TOKEN_MAP="1:w,2:b"
      GRID_TOKEN_MAP_TARGETS="problem"
    fi
    ;;
  *)
    echo "Unsupported puzzle key: $PUZZLE_KEY"
    echo "Try: nurikabe | masyu"
    exit 2
    ;;
esac

STAMP="$(date +%Y%m%d_%H%M%S)"
TMP_CLEANED="scripts/data/reports/tmp.${PUZZLE_KEY}.${STAMP}.cleaned.json"
REPORT_PATH="scripts/data/reports/${PUZZLE_KEY}.sync_clean.report.json"
DIFF_PATH="scripts/data/reports/${PUZZLE_KEY}.${STAMP}.diff"

echo "[1/5] Sync external assets -> local assets"
rsync -avh --delete "$ASSETS_SRC" "$ASSETS_DST"

echo "[2/5] Build cleaned candidate (no overwrite yet)"
CMD=(python "scripts/data/janko_pipeline.py"
  --dataset "$DATASET_PATH"
  --puzzle-type "$PUZZLE_TYPE"
  --apply-fixes
  --fix-strategies $FIX_STRATEGIES
  --output-report "$REPORT_PATH"
  --output-dataset "$TMP_CLEANED"
)
if [[ -n "$GRID_TOKEN_MAP" ]]; then
  CMD+=(--grid-token-map "$GRID_TOKEN_MAP" --grid-token-map-targets "$GRID_TOKEN_MAP_TARGETS")
fi
if [[ -n "$GRID_TOKEN_MAP_FILE" ]]; then
  CMD+=(--grid-token-map-file "$GRID_TOKEN_MAP_FILE" --grid-token-map-targets "$GRID_TOKEN_MAP_TARGETS")
fi
if [[ "$AUGMENT_PUZZLINK" == "1" ]]; then
  CMD+=(--augment-puzzlink)
fi
if [[ "$AUGMENT_PENPA" == "1" ]]; then
  CMD+=(--augment-penpa)
fi
if [[ "$WRITE_STATUS" == "1" ]]; then
  CMD+=(--write-status)
fi
if [[ "$DEDUPE" == "1" ]]; then
  CMD+=(--dedupe --dedupe-key "$DEDUPE_KEY")
fi
"${CMD[@]}"

echo "[3/5] Build review diff"
if cmp -s "$DATASET_PATH" "$TMP_CLEANED"; then
  echo "No content change after cleaning."
  rm -f "$TMP_CLEANED"
  echo "Report: $REPORT_PATH"
  exit 0
fi

git --no-pager diff --no-index -- "$DATASET_PATH" "$TMP_CLEANED" > "$DIFF_PATH" || true
echo "Report: $REPORT_PATH"
echo "Diff:   $DIFF_PATH"

if [[ "$MODE" == "review" ]]; then
  echo "[4/5] Review mode: apply cleaned dataset?"
  read -r -p "Type 'y' to overwrite ${DATASET_PATH}: " ANSWER
  if [[ "$ANSWER" != "y" ]]; then
    echo "Cancelled. Candidate kept at: $TMP_CLEANED"
    exit 0
  fi
fi

echo "[4/5] Writing cleaned dataset"
mv "$TMP_CLEANED" "$DATASET_PATH"
echo "Done. Updated: $DATASET_PATH"
echo "Report: $REPORT_PATH"
echo "Diff:   $DIFF_PATH"

if [[ "$SYNC_BACK" == "1" ]]; then
  echo "[5/5] Sync local assets -> external assets"
  rsync -avh --delete "$ASSETS_DST" "$ASSETS_SRC"
  echo "Done. External assets updated: $ASSETS_SRC"
else
  echo "[5/5] Skip sync-back (set SYNC_BACK=1 to enable)"
fi
