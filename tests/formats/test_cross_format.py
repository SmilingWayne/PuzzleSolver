# tests/test_roundtrip.py
import pytest
from puzzlekit.formats.penpa_converter import PenpaConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

class TestCrossFormatPenpaPuzzlink:
    """
    TEST Puzzlink Round Trip.
    """
    
    def test_cross_penpa_puzzlink(self, puzzlink_test_urls, penpa_test_urls):
        for pid, url_pzl in puzzlink_test_urls.items():
            if pid in penpa_test_urls:
                url_ppa = penpa_test_urls[pid]
                # First decode, from url -> IR1
                converter1 = PuzzlinkConverter()
                ir1 = converter1.decode(url_pzl)
                print(ir1.cells)
                # Second decode, from url2 -> IR2
                converter2 = PenpaConverter()
                ir2 = converter2.decode(url_ppa)
                print(ir2.cells)
                
                # If IR1 ?== IR2 
                assert ir1 == ir2, f"[Puzzlink] Puzzle {pid} wrong. URL: {url_pzl}"
