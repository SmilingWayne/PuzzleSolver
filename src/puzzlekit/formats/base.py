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


PENPA_MODE = '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}'
PENPA_PU_X_STR = '{zR:{z_:[]},zU:{z_:[]},z8:{z_:[]},zS:{},zN:{},z1:{},zY:{},zF:{},z2:{},zT:[],z3:[],zD:[],z0:[],z5:[],zL:{},zE:{},zW:{},zC:{},z4:{},z6:[],z7:[]}'
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

# element 8: __export_solcheck_shared

PENPA_SOL_CHECK_DICT_DEFAULT = {
    "sol_surface_exact": False,
    "sol_surface": False,
    "sol_number": False,
    "sol_loopline_exact": False,
    "sol_loopline": False,
    "sol_ignoreloopline": False,
    "sol_loopedge_exact": False,
    "sol_loopedge": False,
    "sol_ignoreborder": False,
    "sol_wall": False,
    "sol_square": False,
    "sol_circle": False,
    "sol_tri": False,
    "sol_arrow": False,
    "sol_math": False,
    "sol_battleship": False,
    "sol_tent": False,
    "sol_star": False,
    "sol_akari": False,
    "sol_mine": False
}

PENPA_PU_X_DEFAULT = json.loads(reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, PENPA_PU_X_STR))
PENPA_MODE_DEFAULT = json.loads(reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, PENPA_MODE))

# element 18: __export_checker_shared
PENPA_SOL_CHECK_OR_DICT_DEFAULT = {
    "sol_or_surface_exact": False,
    "sol_or_surface": False,
    "sol_or_number": False,
    "sol_or_loopline_exact": False,
    "sol_or_loopline": False,
    "sol_or_loopedge_exact": False,
    "sol_or_loopedge": False,
    "sol_or_wall": False,
    "sol_or_square": False,
    "sol_or_circle": False,
    "sol_or_tri": False,
    "sol_or_arrow": False,
    "sol_or_math": False,
    "sol_or_battleship": False,
    "sol_or_tent": False,
    "sol_or_star": False,
    "sol_or_akari": False,
    "sol_or_mine": False
}

PENPA_BG_IMAGE_ENCRYPTED = "JYjBDkAwEAX/5Z33UNf+jDQUjdWV1Q0i/r0Nl8nMPDBl+GzZMhAveEe6PsochleadazZWJxlnF8ghf1CJhC8fan0sq8T9vBQ=="


@dataclass
class PenpaMetadata:
    
    # ========== Line 1: header ==========
    grid_type: str = "square"
    nx: int = 5
    ny: int = 5
    size: int = 38                # size of each cell on penpa 
    theta: int = 0                # for rotate
    reflect: List[int] = field(default_factory=lambda: [1, 1])
    canvasx: int = 0              # canvas size x
    canvasy: int = 0              # canvas size y
    center_n: int = 0             # center cell
    center_n0: int = 0            # center cell (?)
    sudoku: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    title: str = ""               # name of the puzzle e.g., heyawake, nonogram
    author: str = ""              # author of the puzzle, optional
    source: str = ""              # (source) url of the puzzle
    rules: str = ""               # rules of the puzzle 
    border_status: str = "OFF"    # unknown
    multisolution: bool = False   # is multi solution ? 
    bg_image_encrypted: str = ""  # (placeholder) for background picture

    # ========== Line 2: space ==========
    space: List[int] = field(default_factory=lambda: [0, 0, 0, 0])  # [top, bottom, left, right]
    
    # ========== Line 3: mode ==========
    mode: Dict[str, Any] = field(default_factory=dict)
    
    # ========== Line 4: pu_q ==========
    pu_q: Dict[str, Any] = field(default_factory=dict)
    
    # ========== Line 5: pu_a ==========
    pu_a: Dict[str, Any] = field(default_factory=dict)
    
    # ========== Line 6-7: __export_list_tab_shared ==========
    centerlist_diff: List[int] = field(default_factory=list)  # diff encoding centerlist
    tab_settings: List[str] = field(default_factory=lambda: [])
    
    # ========== Line 8: sol_check ==========
    sol_check: Dict[str, bool] = field(default_factory=dict)
    
    # ========== Line 9-14: version shared ==========
    timer_placeholder: str = '"x"'     # default 'x'
    comp_mode: str = '"x"'             # default 'x'
    version: List[int] = field(default_factory=lambda: [3, 2, 1]) # v3.2.1, aha~
    mode_snapshot: Dict[str, Any] = field(default_factory=dict)
    theme_placeholder: str = '"x"'     # default 'x'
    custom_colors_on: str = '0'        # either 1 or 0
    
    # ========== Line 15-16: pu_q_col / pu_a_col ==========
    pu_q_col: Dict[str, Any] = field(default_factory=dict)
    pu_a_col: Dict[str, Any] = field(default_factory=dict)
    
    # ========== Line 17: sol_check (OR) ==========
    sol_check_or: Dict[str, bool] = field(default_factory=dict)
    
    # ========== Line 18: genre_tags ==========
    genre_tags: List[str] = field(default_factory=list)
    
    # ========== Line 19: custom_message ==========
    custom_message: str = ""
    
    def __post_init__(self):
        """
        Auto fill default after init
        """
        if not self.mode: self.mode = PENPA_MODE_DEFAULT.copy()
        
        if not self.pu_q: self.pu_q = PENPA_PU_X_DEFAULT.copy()
        
        if not self.pu_a: self.pu_a = PENPA_PU_X_DEFAULT.copy()
        
        if not self.mode_snapshot: self.mode_snapshot = PENPA_MODE_DEFAULT.copy()
        
        if not self.sol_check: self.sol_check = PENPA_SOL_CHECK_DICT_DEFAULT.copy()

        if not self.sol_check_or: self.sol_check_or = PENPA_SOL_CHECK_OR_DICT_DEFAULT.copy()
            
        if not self.bg_image_encrypted: self.bg_image_encrypted = PENPA_BG_IMAGE_ENCRYPTED
            
        if not self.pu_q_col: self.pu_q_col = PENPA_PU_X_DEFAULT.copy()
            
        if not self.pu_a_col: self.pu_a_col = PENPA_PU_X_DEFAULT.copy()
        

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