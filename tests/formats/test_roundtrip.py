# tests/test_roundtrip.py
import pytest
from puzzlekit.formats.penpa_converter import PenpaConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

class TestPuzzlelinkRoundTrip:
    """
    TEST Puzzlink Round Trip.
    """
    
    def test_self_roundtrip(self, puzzlink_test_urls):
        for puzzle, url in puzzlink_test_urls.items():
            # First decode, from url -> IR1
            converter1 = PuzzlinkConverter()
            ir1 = converter1.decode(url)
            
            # First Encode, from IR -> url2
            url2 = converter1.encode(ir1)
            
            # Second decode, from url2 -> IR2
            converter2 = PuzzlinkConverter()
            ir2 = converter2.decode(url2)
            
            # If IR1 ?== IR2 
            assert ir1 == ir2, f"[Puzzlink] Puzzle {puzzle} wrong. URL: {url}"

    def test_yajilin_roundtrip(self, puzzlink_test_urls):
        """Keep yajilin coverage explicit even when cross-format is disabled."""
        yajilin_cases = {
            k: v for k, v in puzzlink_test_urls.items() if k.startswith("yajilin")
        }
        for puzzle, url in yajilin_cases.items():
            converter1 = PuzzlinkConverter()
            ir1 = converter1.decode(url)

            url2 = converter1.encode(ir1)

            converter2 = PuzzlinkConverter()
            ir2 = converter2.decode(url2)

            assert ir1 == ir2, f"[Puzzlink][Yajilin] Puzzle {puzzle} wrong. URL: {url}"

    def test_yajilin_roundtrip_with_shading_config(self):
        """Yajilin /b mode: encode with explicit shading config."""
        shaded_url = "https://puzz.link/p?yajilin/b/9/11/j21a11b40y21a33k21a41y11b31a13j"

        decoder = PuzzlinkConverter()
        ir1 = decoder.decode(shaded_url)

        encoder = PuzzlinkConverter(config={"yajilin_encode_with_shading": True})
        url2 = encoder.encode(ir1)
        assert "?yajilin/b/" in url2, f"Expected shaded yajilin url, got: {url2}"

        decoder2 = PuzzlinkConverter()
        ir2 = decoder2.decode(url2)
        assert ir1 == ir2, f"[Puzzlink][Yajilin][Shading] wrong. URL: {shaded_url}"


class TestPenpaTrip:
    """
    TEST Penpa Round Trip.
    """
    
    def test_self_roundtrip(self, penpa_test_urls):
        for puzzle, url in penpa_test_urls.items():
            # First decode, from url -> IR1
            converter1 = PenpaConverter()
            ir1 = converter1.decode(url)
            
            # First Encode, from IR -> url2
            url2 = converter1.encode(ir1)
            
            # Second decode, from url2 -> IR2
            converter2 = PenpaConverter()
            ir2 = converter2.decode(url2)
            
            # If IR1 ?== IR2 
            assert ir1 == ir2, f"[Penpa] Puzzle {puzzle} wrong. URL: {url}"

