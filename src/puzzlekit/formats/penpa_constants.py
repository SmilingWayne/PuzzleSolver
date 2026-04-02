from __future__ import annotations

from functools import reduce
import json

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

# Kept for compatibility; some code paths may still use this template string.
PENPA_MODE = '{z9:zA,zG:["1","2","1"],zQ:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",2],zE:["1",2],zW:["",2],zC:["1",10],zN:["1",1],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["battleship",3],"sudoku":["1",1]},zA:{zM:"combi",zS:["",1],"multicolor":["",1],zL:["1",3],zE:["1",3],zW:["",3],zC:["1",10],zN:["1",2],zY:["circle_L",1],zP:[zT,""],zB:["",""],"move":["1",""],"combi":["blpo",3],"sudoku":["1",9]}}'

PENPA_PU_X_STR = '{zR:{z_:[]},zU:{z_:[]},z8:{z_:[]},zS:{},zN:{},z1:{},zY:{},zF:{},z2:{},zT:[],z3:[],zD:[],z0:[],z5:[],zL:{},zE:{},zW:{},zC:{},z4:{},z6:[],z7:[]}'

# Default pu_q skeleton (expanded form), used when forging Penpa payloads.
PENPA_PU_X_DEFAULT = json.loads(
    reduce(lambda s, abbr: s.replace(abbr[1], abbr[0]), COMPRESS_SUB, PENPA_PU_X_STR)
)

