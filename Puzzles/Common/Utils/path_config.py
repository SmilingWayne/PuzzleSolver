import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
# DATA_DIR = os.path.join(ASSETS_DIR, "data")
# AKARI_PROBLEMS = os.path.join(DATA_DIR, "Akari", "problems", "Akari_puzzles.json")

def get_asset_path(relative_path):
    """Get absolute route of asset"""
    return os.path.join(ASSETS_DIR, relative_path)