from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# -----------------------------
# Format-agnostic semantic types
# -----------------------------

# A format-neutral color token.
#
# Recommended conventions:
# - semantic names: "black", "white", "light_gray", "gray", ...
# - rich colors: "#RRGGBB" or "#RRGGBBAA"
Color = str


class Direction(str, Enum):
    """Compass direction for directional clues/marks."""

    N = "n"
    S = "s"
    W = "w"
    E = "e"
    NW = "nw"
    NE = "ne"
    SW = "sw"
    SE = "se"


@dataclass(frozen=True)
class TextClue:
    kind: str = "text"
    text: str = ""

    def to_dict(self) -> dict:
        return {"kind": self.kind, "text": self.text}


@dataclass(frozen=True)
class NumberClue:
    kind: str = "number"
    value: Union[int, str] = ""

    def to_dict(self) -> dict:
        return {"kind": self.kind, "value": self.value}


@dataclass(frozen=True)
class ArrowClue:
    kind: str = "arrow"
    value: Optional[Union[int, str]] = None
    direction: Direction = Direction.N

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "value": self.value,
            "direction": self.direction.value,
        }

@dataclass(frozen = True)
class TapaClue:
    kind: str = "tapa"
    value: Optional[Union[int, str]] = None
    
    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "value": self.value,
        }

Clue = Union[TextClue, NumberClue, ArrowClue, TapaClue]

@dataclass
class EdgeState:
    """Edge Status
    
    - edge_type: 
        2:    black border line
        13:   dot line
        ...
    """
    connected: bool = True        # thin line
    edge_type: int = 2            # default = 2
    symbol: Optional[SymbolState] = None # symbol, such as ">", "<", "x" ... 
    # blacked: bool = False         # black border
    # deleted: bool = False         # delete mark
    
@dataclass
class SymbolState:
    """A lightweight symbol marker.

    `symbol_type` is a free-form token (converter-defined), e.g. "circle", "x",
    "sun_moon", etc.
    """
    symbol_index: int = 0
    symbol_type: str = "circle_L"
    symbol_style: int = 1
    
    def to_dict(self) -> dict:
        """Convert to dict.

        Returns:
            dict: dict of symbol_index, symbol_type, symbol_style
        """
        return {
            "symbol_index": self.symbol_index,
            "symbol_type": self.symbol_type,
            "symbol_style": self.symbol_style
        }
    
@dataclass
class CellState:
    """
    Cell status
    """
    clue: Optional[Clue] = None
    fill: Optional[Color] = None
    symbol: Optional[SymbolState] = None

    # Legacy convenience: some encodings express “black cell” as a fill color.
    # Solvers/step-by-step tools should prefer semantic `fill` and explicit state layers.
    shaded: bool = False
    


@dataclass
class PuzzleInstance:
    """
    Puzzle Intermediate Representation (IR)
    
    Start from Heyawake!
    """
    grid_type: str = "square"
    puzzle_type: str = "heyawake"
    title: str = ""
    author: str = ""
    source: str = ""
    rows: int = 0                       # for rectangle with margins
    cols: int = 0                       # for rectangle with margins
    hex_len: int = 0                    # placeholder
    margins: List[int] = field(default_factory = list)   # for margins, top, bottom, left, right
    boxes: List[Any] = field(default_factory=list)  # layout/cut-out metadata (kept as-is for now)
    edges: Dict[tuple[Any], EdgeState] = field(default_factory=dict)
    cells: Dict[tuple[Any], CellState] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        """Custom format.
        """
        return f"""
        Puzzle Instance for {self.puzzle_type}.
        
        grid_type:         {self.grid_type} 
        title:             {self.title}
        shape:             {self.rows} x {self.cols} 
        margins:           {', '.join(map(str, self.margins))}
        author:            {self.author}
        source:            {self.source}
        edges (len):       {len(self.edges.keys())}
        boxes (len):       {len(self.boxes)}
        cells (len):       {len(self.cells.keys())}
        """

    def normalize(self) -> dict:
        """Normalize IR to comparable dict.

        Returns:
            dict: _description_
        """
        # 1. norm cells - after sort
        cells_normalized = {}
        for (r, c), state in sorted(self.cells.items()):
            clue_dict = state.clue.to_dict() if state.clue is not None else None
            cells_normalized[f"{r},{c}"] = {
                "shaded": state.shaded,
                "fill": state.fill,
                "clue": clue_dict,
                "symbol": state.symbol.to_dict() if state.symbol is not None else None,
            }
        
        # 2. norm edges - after sort
        edges_normalized = {}
        for (p1, p2), state in sorted(self.edges.items()):
            sorted_coords = tuple(sorted([p1, p2]))
            key = f"{sorted_coords[0][0]},{sorted_coords[0][1]}-{sorted_coords[1][0]},{sorted_coords[1][1]}"
            edges_normalized[key] = {
                "connected": state.connected,
                "edge_type": state.edge_type,
                "symbol": state.symbol.to_dict() if state.symbol is not None else None,
            }
        # print(len(self.cells))
        # 3. core attributes:
        return {
            "grid_type": self.grid_type,
            "puzzle_type": self.puzzle_type,
            "rows": self.rows,
            "cols": self.cols,
            "margins": self.margins,
            "cells": cells_normalized,
            "edges": edges_normalized,
            "boxes": self.boxes,
        }
    
    def semantic_equals(self, other: 'PuzzleInstance') -> bool:
        """
        If two IR is semantic equal.
        """
        if not isinstance(other, PuzzleInstance):
            return False
        return self.normalize() == other.normalize()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PuzzleInstance):
            return False
        return self.semantic_equals(other)