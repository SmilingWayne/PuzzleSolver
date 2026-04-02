from __future__ import annotations
from typing import List, TypedDict, Type, Any, Dict
from puzzlekit.formats.puzzle_types import normalize_puzzle_type
from dataclasses import dataclass, field
import json 
from functools import reduce

# Penpa+ payload compression substitutions (in order).
# These are Penpa-specific implementation details and should not leak into the IR.
COMPRESS_SUB = [
    ("z", "zZ"),
    ('"qa"', "z9"),
    ('"pu_q"', "zQ"),
    ('"pu_a"', "zA"),
    ('"grid"', "zG"),
    ('"edit_mode"', "zM"),
    ('"surface"', "zS"),
    ('"line"', "zL"),
    ('"lineE"', "zE"),
    ('"wall"', "zW"),
    ('"cage"', "zC"),
    ('"number"', "zN"),
    ('"symbol"', "zY"),
    ('"special"', "zP"),
    ('"board"', "zB"),
    ('"command_redo"', "zR"),
    ('"command_undo"', "zU"),
    ('"command_replay"', "z8"),
    ('"numberS"', "z1"),
    ('"freeline"', "zF"),
    ('"freelineE"', "z2"),
    ('"thermo"', "zT"),
    ('"arrows"', "z3"),
    ('"direction"', "zD"),
    ('"squareframe"', "z0"),
    ('"polygon"', "z5"),
    ('"deletelineE"', "z4"),
    ('"killercages"', "z6"),
    ('"nobulbthermo"', "z7"),
    ('"_a"', "z_"),
    ("null", "zO"),
]

# standard pu_q skeleton
PENPA_PU_X_STR = '{zR:{z_:[]},zU:{z_:[]},z8:{z_:[]},zS:{},zN:{},z1:{},zY:{},zF:{},z2:{},zT:[],z3:[],zD:[],z0:[],z5:[],zL:{},zE:{},zW:{},zC:{},z4:{},z6:[],z7:[]}'

# Default pu_q skeleton (expanded form), used when forging Penpa payloads.
PENPA_PU_X_DEFAULT = json.loads(
    reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, PENPA_PU_X_STR)
)

PENPA_MODE_TEMPLATE = {
    "heyawake": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface"],
    },
    "shikaku": {
        "mode": '{z9:zA,zG:["2","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["edgesub",3],"sudoku":["1",9]}}',
        'user_tab_setting': ["Surface","Composite"]
    },
    "aqre": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",9]}}',
        "user_tab_setting": ['Surface'],
    },
    "shimaguni": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",9]}}',
        "user_tab_setting": ['Surface'],
    },
    "stostone": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",9]}}',
        "user_tab_setting": ['Surface'],
    },
    "ayeheya": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:zS,zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",9]}}',
        "user_tab_setting": ['Surface'],
    },
    "country": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["lineox",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"],
    },
    "nonogram": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "nurikabe": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "kurochute": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting":  ["Surface","Composite"],
    },
    "kurodoko": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "kurotto": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "nurimisaki": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "moonsun": {
        "mode": '{z9:zA,zG:["2","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["linex",3],"sudoku":["1",9]}}',
        'user_tab_setting': ["Surface","Composite"]
    },
    "masyu": {
        "mode": '{z9:zA,zG:["2","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["linex",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "slitherlink": {
        "mode": '{z9:zA,zG:["3","1","2"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["edgex",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "yajilin" : {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["linex",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"],
    },
    "castle": {
        'mode': '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["linex",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"],
    },
    "hebi": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:zN,zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Number Normal"]
    },
    "tapa": {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface","Composite"]
    },
    "default" : {
        "mode": '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}',
        "user_tab_setting": ["Surface"],
    },
    
}

def get_penpa_template(puzzle_type: str) -> dict:
    normalized = normalize_puzzle_type(puzzle_type)
    template = PENPA_MODE_TEMPLATE.get(normalized, PENPA_MODE_TEMPLATE["default"])
    return template

def penpa_str_to_dict(mode_str: str):
    return json.loads(reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, mode_str))

@dataclass
class PenpaHeader:
    size: int = 38
    theta: int = 0
    reflect: List[int] = field(default_factory=lambda: [1, 1])
    sudoku: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    rules: str = ""
    border_status: str = "OFF"
    multisolution: bool = False
    bg_image_encrypted: str = "JYjBDkAwEAX/5Z33UNf+jDQUjdWV1Q0i/r0Nl8nMPDBl+GzZMhAveEe6PsochleadazZWJxlnF8ghf1CJhC8fan0sq8T9vBQ=="

class PenpaFixedFields(TypedDict):
    # for auto fill
    header: PenpaHeader 
    sol_check_or: Dict[str, Any]

PENPA_FIXED_FIELDS: PenpaFixedFields = {
    # HEADER (Line 1)
    "header": PenpaHeader(),
    # Line 5
    "pu_a": PENPA_PU_X_DEFAULT.copy(),
    # Line 8
    "sol_check": {
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
    },
    # Line 9
    "timer_placeholder": '"x"',
    # Line 10
    "comp_mode": '"x"',
    # Line 11
    "version": [3, 2, 1],
    # Line 13
    "theme_placeholder": '"x"',
    # Line 14
    "theme_colors_on": '0',
    # Line 15
    "pu_q_col": PENPA_PU_X_DEFAULT.copy(),
    # Line 16
    "pu_a_col": PENPA_PU_X_DEFAULT.copy(),
    # Line 17
    "sol_check_or": {
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
    },
    # Line 19
    "custom_message" : ""
}

