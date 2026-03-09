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

