# tests/formats/test_cross_format.py
from puzzlekit.formats.penpa_converter import PenpaConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter


class TestCrossFormatPenpaPuzzlink:
    """Cross-format checks: same puzzle from puzz.link vs Penpa+ URLs."""

    def test_cross_penpa_puzzlink_semantic(self, puzzlink_test_urls, penpa_test_urls):
        for pid, url_pzl in puzzlink_test_urls.items():
            if pid not in penpa_test_urls:
                continue
            url_ppa = penpa_test_urls[pid]
            ir_pzl = PuzzlinkConverter().decode(url_pzl)
            ir_ppa = PenpaConverter().decode(url_ppa)
            assert ir_pzl.cross_format_semantic_equals(ir_ppa), (
                f"[cross-format] Puzzle {pid} content mismatch.\n"
                f"  puzz.link: {url_pzl}\n"
                f"  penpa: {url_ppa[:80]}..."
            )

    def test_cross_penpa_puzzlink_strict_when_aligned(self, puzzlink_test_urls, penpa_test_urls):
        """Full ``semantic_equals`` still holds for fixtures where both decoders align."""
        for pid, url_pzl in puzzlink_test_urls.items():
            if pid not in penpa_test_urls:
                continue
            ir_pzl = PuzzlinkConverter().decode(url_pzl)
            ir_ppa = PenpaConverter().decode(penpa_test_urls[pid])
            if ir_pzl == ir_ppa:
                assert ir_pzl.cross_format_semantic_equals(ir_ppa)
