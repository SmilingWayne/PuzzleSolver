import argparse
import logging
import runpy
import os
from pathlib import Path

from puzzlekit.formats.penpa_converter import PenpaConverter


def _read_first_nonempty_line(path: str) -> str:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                return s
    raise ValueError(f"No non-empty lines found in: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="One-click debugger for penpa_converter."
    )
    parser.add_argument(
        "--level",
        default="DEBUG",
        help="Logging level (DEBUG/INFO/WARNING...). Default: DEBUG",
    )
    parser.add_argument(
        "--run-main",
        action="store_true",
        help="Run penpa_converter.py __main__ block directly.",
    )
    parser.add_argument(
        "--url",
        default="",
        help="Penpa payload/url to decode directly (m=edit&p=... or full URL).",
    )
    parser.add_argument(
        "--url-file",
        default="",
        help="Read URL from first non-empty line in file.",
    )
    parser.add_argument(
        "--show-parts",
        action="store_true",
        help="Enable debug_penpa_parts when decoding URL.",
    )
    args = parser.parse_args()

    level = getattr(logging, str(args.level).upper(), logging.DEBUG)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.run_main:
        if args.show_parts:
            # Let penpa_converter decode() enable parts dump even in __main__ flow.
            os.environ["PUZZLEKIT_DEBUG_PENPA_PARTS"] = "1"
        runpy.run_path("src/puzzlekit/formats/penpa_converter.py", run_name="__main__")
        return

    url = args.url.strip()
    if args.url_file:
        url = _read_first_nonempty_line(args.url_file)

    if not url:
        parser.error("Provide --run-main, or --url/--url-file.")

    cfg = {"debug_penpa_parts": True} if args.show_parts else {}
    converter = PenpaConverter(cfg)
    ir = converter.decode(url)
    print(
        f"decoded puzzle_type={ir.puzzle_type} rows={ir.rows} cols={ir.cols} "
        f"cells={len(ir.cells)} edges={len(ir.edges)} boxes={len(ir.boxes)}"
    )


if __name__ == "__main__":
    main()

