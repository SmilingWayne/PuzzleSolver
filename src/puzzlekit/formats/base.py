from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Tuple, List
from functools import reduce
import json
from enum import Enum

class NumberColor(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_

    Returns:
        _type_: _description_
    """
    BLACK: int = 1
    GREEN: int = 2
    # ... etc

class SurfaceColor(Enum):
    """Enumeration class for **surface color**.

    Args:
        Enum (_type_): _description_
    """
    DARK_GREY: int = 1
    GREY: int = 2
    LIGHT_GREY: int = 3
    BLACK: int = 4
    GREEN: int = 5
    BLUE: int = 6
    RED: int = 7
    YELLOW: int = 8
    PINK: int = 9
    ORANGE: int = 10
    PURPLE: int = 11
    BROWN: int = 12


COMPRESS_SUB = [
    ('z', 'zZ'),
    ('"qa"', 'z9'),
    ('"pu_q"', 'zQ'),
    ('"pu_a"', 'zA'),
    ('"grid"', 'zG'),
    ('"edit_mode"', 'zM'),
    ('"surface"', 'zS'),
    ('"line"', 'zL'),
    ('"lineE"', 'zE'),
    ('"wall"', 'zW'),
    ('"cage"', 'zC'),
    ('"number"', 'zN'),
    ('"symbol"', 'zY'),
    ('"special"', 'zP'),
    ('"board"', 'zB'),
    ('"command_redo"', 'zR'),
    ('"command_undo"', 'zU'),
    ('"command_replay"', 'z8'),
    ('"numberS"', 'z1'),
    ('"freeline"', 'zF'),
    ('"freelineE"', 'z2'),
    ('"thermo"', 'zT'),
    ('"arrows"', 'z3'),
    ('"direction"', 'zD'),
    ('"squareframe"', 'z0'),
    ('"polygon"', 'z5'),
    ('"deletelineE"', 'z4'),
    ('"killercages"', 'z6'),
    ('"nobulbthermo"', 'z7'),
    ('"_a"', 'z_'),
    ('null', 'zO'),
]
PENPA_MODE = '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}'
PENPA_PU_X_STR = '{zR:{z_:[]},zU:{z_:[]},z8:{z_:[]},zS:{},zN:{},z1:{},zY:{},zF:{},z2:{},zT:[],z3:[],zD:[],z0:[],z5:[],zL:{},zE:{},zW:{},zC:{},z4:{},z6:[],z7:[]}'
PENPA_PU_X_DEFAULT = json.loads(reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, PENPA_PU_X_STR))


@dataclass
class CellState:
    """
    Cell status
    """
    value: Optional[str] = None   # Number clue
    shaded: bool = False          # black?
    # num_color: int = 1            # number color
    num_color: Optional[NumberColor] = None            # number color
    num_style: str = "1"          # number style
    
    surf_color: Optional[SurfaceColor] = None 
    

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
    # blacked: bool = False         # black border
    # deleted: bool = False         # delete mark


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
    boxes: List[Any] = field(default_factory=list)  # same as 'box' of penpa
    edges: Dict[tuple[Any], EdgeState] = field(default_factory=dict) # edge status
    cells: Dict[tuple[Any], CellState] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # =============== Penpa params end ===============
    
    skip_shading: bool = True
    rows_no_margin: int = 0
    cols_no_margin: int = 0
    
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
            cells_normalized[f"{r},{c}"] = {
                "value": state.value,
                "shaded": state.shaded,
                "num_color": state.num_color.value if state.num_color is not None else None,
                "num_style": state.num_style,
                "surf_color": state.surf_color.value if state.surf_color is not None else None
            }
        
        # 2. norm edges - after sort
        edges_normalized = {}
        for (p1, p2), state in sorted(self.edges.items()):
            sorted_coords = tuple(sorted([p1, p2]))
            key = f"{sorted_coords[0][0]},{sorted_coords[0][1]}-{sorted_coords[1][0]},{sorted_coords[1][1]}"
            edges_normalized[key] = {
                "connected": state.connected,
                "edge_type": state.edge_type,
            }
        # print(len(self.cells))
        # 3. core attributes:
        return {
            "grid_type": self.grid_type,
            # "puzzle_type": self.puzzle_type,
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