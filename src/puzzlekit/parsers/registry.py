from typing import Callable, Dict, Any
from .common import (
    standard_grid_parser, 
    standard_region_grid_parser_from_json
)

ParserFunc = Callable[[str], Dict[str, Any]]

PARSER_MAP: Dict[str, ParserFunc] = {
    "akari": standard_grid_parser,
    "balance_loop": standard_grid_parser,
    "binairo": standard_grid_parser,
    "bosanowa": standard_grid_parser,
    "butterfly_sudoku": standard_grid_parser,
    "buraitoraito": standard_grid_parser,
    "fobidoshi": standard_grid_parser,
    
    
}


def get_parser(puzzle_type: str) -> ParserFunc:
    parser = PARSER_MAP.get(puzzle_type)
    if parser is None:
        raise ValueError(f"No parser defined for puzzle type: {puzzle_type}")
    return parser