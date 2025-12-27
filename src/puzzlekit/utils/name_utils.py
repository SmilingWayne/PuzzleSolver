import re

SPECIAL_CLASS_TO_TYPE_MAP = {
    "ABCEndView": "abc_end_view",
    "Clueless1Sudoku": "clueless_1_sudoku",
    "Clueless2Sudoku": "clueless_2_sudoku",
    "Gattai8Sudoku": "gattai_8_sudoku",
}

SPECIAL_TYPE_TO_CLASS_MAP = {v: k for k, v in SPECIAL_CLASS_TO_TYPE_MAP.items()}


def infer_puzzle_type(class_name: str) -> str:
    if class_name.endswith("Solver"):
        clean_name = class_name[:-6]
    else:
        clean_name = class_name

    if clean_name in SPECIAL_CLASS_TO_TYPE_MAP:
        return SPECIAL_CLASS_TO_TYPE_MAP[clean_name]
    
    return re.sub(r'(?<!^)(?=[A-Z])', '_', clean_name).lower()


def infer_class_name(puzzle_type: str) -> str:
    if puzzle_type in SPECIAL_TYPE_TO_CLASS_MAP:
        return SPECIAL_TYPE_TO_CLASS_MAP[puzzle_type]

    return ''.join(word.title() for word in puzzle_type.split('_'))