# PuzzleInstance Intermediate Representation Specification

> **PuzzleInstance** is the **Intermediate Representation (IR)** used throughout PuzzleKit. It provides a unified data model for converting and processing puzzles across different formats, including [puzz.link](https://puzz.link), [Penpa+](https://swaroopg92.github.io/penpa-edit/), and [Janko.at](https://www.janko.at).

---

## Table of Contents

1. [Core Structure Overview](#core-structure-overview)
2. [Coordinate System](#coordinate-system)
3. [CellState: Cell State](#cellstate-cell-state)
4. [EdgeState: Edge State](#edgestate-edge-state)
5. [Clue Types](#clue-types)
6. [Usage Examples](#usage-examples)
7. [Format Conversion](#format-conversion)
8. [Related Files](#related-files)

---

## Core Structure Overview

`PuzzleInstance` is defined in [`src/puzzlekit/formats/base.py`](../src/puzzlekit/formats/base.py) as a Python dataclass containing the following core fields:

```python
@dataclass
class PuzzleInstance:
    grid_type: str = "square"           # Grid type (currently "square" is primarily supported)
    puzzle_type: str = "heyawake"       # Puzzle type (e.g., "heyawake", "slitherlink")
    title: str = ""                     # Puzzle title
    author: str = ""                    # Author name
    source: str = ""                    # Source information
    rows: int = 0                       # Grid rows (including margins)
    cols: int = 0                       # Grid columns (including margins)
    margins: List[int] = field(default_factory=list)    # [top, bottom, left, right] margins
    boxes: List[Any] = field(default_factory=list)      # Region/room partition metadata
    edges: Dict[tuple, EdgeState] = field(default_factory=dict)  # Edge state dictionary
    cells: Dict[tuple, CellState] = field(default_factory=dict)  # Cell state dictionary
    metadata: Dict[str, Any] = field(default_factory=dict)       # Additional metadata
```

---

## Coordinate System

### Coordinate Definition

PuzzleInstance uses a 2D coordinate system denoted as **(row, col)**, where:

- **row**: Increases from top to bottom, starting at 0
- **col**: Increases from left to right, starting at 0

### Coordinate System with Margins

```
┌─────────────────────────────────────────────────┐
│               top_margin                        │
│       ┌────────────────────────────────┐        │
│       │                                │        │
│       │    Actual Grid Region          │        │
│left   │     (rows - top - bottom) ×    │  right │ 
│margin │     (cols - left - right)      │  margin│
│       │                                │        │
│       │                                │        │
│       └────────────────────────────────┘        │
│               bottom_margin                     │
└─────────────────────────────────────────────────┘
```

**Example**: For a 10×10 puzzle with `margins = [2, 2, 1, 1]`:
- `rows = 14` (2 + 10 + 2)
- `cols = 12` (1 + 10 + 1)
- The actual puzzle area starts at coordinate `(2, 1)` and ends at `(11, 10)`

### Cells Dictionary Keys

The `cells` dictionary uses `(row, col)` tuples as keys:

```python
# Example: Place a number clue at position (3, 5)
puzzle.cells[(3, 5)] = CellState(clue=NumberClue(value=42))
```

### Edges Dictionary Keys

The `edges` dictionary uses a tuple of **two coordinate points** as keys, representing the edge connecting two cells:

```python
# Example: Place a thick black border between (2, 3) and (2, 4)
puzzle.edges[((2, 3), (2, 4))] = EdgeState(connected=True, edge_type=2)
```

**Note**: The order of the two endpoints does not matter; the system automatically normalizes them. However, it is recommended to follow the **left-to-right, top-to-bottom** convention (left or top coordinate first).

---

## CellState: Cell State

`CellState` describes all state information for a single cell:

```python
@dataclass
class CellState:
    clue: Optional[Clue] = None      # Clue (number, arrow, text, etc.)
    fill: Optional[Color] = None     # Fill color
    symbol: Optional[SymbolState] = None  # Symbol marker
    shaded: bool = False             # Whether the cell is shaded (semantic marker)
```

### Attributes

| Attribute | Type                    | Description                                                       |
|-----------|-------------------------|-------------------------------------------------------------------|
| `clue`    | `Optional[Clue]`        | Clue in the cell, such as numbers, arrows, etc.                   |
| `fill`    | `Optional[str]`         | Fill color, e.g., `"black"`, `"gray"`, `"red"`, etc.              |
| `symbol`  | `Optional[SymbolState]` | Symbol marker, such as circles, crosses, etc.                     |
| `shaded`  | `bool`                  | Whether the cell is black/shaded (used in Heyawake, Nurikabe, etc.) |

### SymbolState: Symbol Markers

```python
@dataclass
class SymbolState:
    symbol_index: int = 0       # Symbol index (Penpa-compatible)
    symbol_type: str = "circle_L"  # Symbol type, e.g., "circle_L", "x", "sun_moon", etc.
    symbol_style: int = 1       # Symbol style
```

---

## EdgeState: Edge State

`EdgeState` describes the state of an edge (boundary line) between two cells:

```python
@dataclass
class EdgeState:
    connected: bool = True        # Whether connected (thin line)
    edge_type: int = 2            # Edge type: 2 = thick black line, 13 = dashed line, etc.
    symbol: Optional[SymbolState] = None  # Symbol on the edge, e.g., ">", "<", "x", etc.
```

### Common Edge Types

| edge_type | Description                          |
|-----------|--------------------------------------|
| `2`       | Default thick black border           |
| `13`      | Dashed border                        |
| `-1`      | Custom edge (used with `symbol`)     |

---

## Clue Types

PuzzleKit supports multiple clue types to represent numbers, arrows, and other markings for different puzzle genres.

### NumberClue

```python
@dataclass
class NumberClue:
    kind: str = "number"
    value: Union[int, str] = ""  # Numeric value, can be integer or string
```

**Usage**:
```python
CellState(clue=NumberClue(value=42))
CellState(clue=NumberClue(value="5"))  # String form
```

### ArrowClue

```python
@dataclass
class ArrowClue:
    kind: str = "arrow"
    value: Optional[Union[int, str]] = None  # Number beside the arrow (optional)
    direction: Direction = Direction.N       # Arrow direction
```

**Direction Enum**:
```python
class Direction(str, Enum):
    N = "n"    # North / Up
    S = "s"    # South / Down
    W = "w"    # West / Left
    E = "e"    # East / Right
    NW = "nw"  # Northwest
    NE = "ne"  # Northeast
    SW = "sw"  # Southwest
    SE = "se"  # Southeast
```

**Usage**:
```python
CellState(clue=ArrowClue(value=5, direction=Direction.E))
```

### TapaClue

```python
@dataclass
class TapaClue:
    kind: str = "tapa"
    value: Optional[Union[int, str]] = None  # Tapa number sequence, e.g., "3 1 2"
```

### TextClue

```python
@dataclass
class TextClue:
    kind: str = "text"
    text: str = ""  # Text content
```

---

## Usage Examples

### Example 1: Creating a Simple Heyawake Puzzle

```python
from puzzlekit.formats.base import (
    PuzzleInstance, CellState, EdgeState, NumberClue
)

# Create a 5x5 Heyawake puzzle
puzzle = PuzzleInstance(
    grid_type="square",
    puzzle_type="heyawake",
    title="Sample Puzzle",
    rows=5,
    cols=5,
    margins=[0, 0, 0, 0],
)

# Add number clues
puzzle.cells[(0, 0)] = CellState(clue=NumberClue(value=3))
puzzle.cells[(2, 2)] = CellState(clue=NumberClue(value=5))

# Add thick black borders (room boundaries)
puzzle.edges[((0, 1), (0, 2))] = EdgeState(connected=True, edge_type=2)
puzzle.edges[((1, 1), (1, 2))] = EdgeState(connected=True, edge_type=2)
puzzle.edges[((2, 1), (2, 2))] = EdgeState(connected=True, edge_type=2)

print(puzzle)
```

### Example 2: Decoding a URL with PuzzlinkConverter

```python
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

converter = PuzzlinkConverter()
url = "https://puzz.link/p?heyawake/10/10/..."
puzzle = converter.decode(url)

# Access data in the puzzle
print(f"Puzzle Type: {puzzle.puzzle_type}")
print(f"Grid Size: {puzzle.rows} x {puzzle.cols}")
print(f"Number of Cells: {len(puzzle.cells)}")
print(f"Number of Edges: {len(puzzle.edges)}")

# Iterate over all cells with clues
for (r, c), cell_state in puzzle.cells.items():
    if cell_state.clue:
        print(f"Position ({r}, {c}) has clue: {cell_state.clue}")
```

### Example 3: Decoding/Encoding with PenpaConverter

```python
from puzzlekit.formats.penpa_converter import PenpaConverter

converter = PenpaConverter()

# Decode Penpa URL
penpa_url = "https://swaroopg92.github.io/penpa-edit/#m=edit&p=..."
puzzle = converter.decode(penpa_url)

# Encode back to Penpa URL
new_url = converter.encode(puzzle)
```

---

## Format Conversion

### From puzz.link

puzz.link uses a compact encoding format. `PuzzlinkConverter` decodes it into a `PuzzleInstance`:

```python
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

converter = PuzzlinkConverter()
puzzle = converter.decode("https://puzz.link/p?heyawake/5/5/...")
```

**Coordinate Mapping**: puzz.link coordinates map directly to PuzzleInstance `(row, col)`, starting from `(0, 0)`.

### From Penpa+

Penpa+ uses a more complex indexing system. `PenpaConverter` handles coordinate transformations:

**Penpa Index System**:
- Penpa uses a 1D index to represent cell positions
- Index calculation accounts for margins and padding
- Conversion formula: `index = row * real_cols + col + offset`

```python
from puzzlekit.formats.penpa_converter import PenpaConverter

converter = PenpaConverter()
puzzle = converter.decode("https://swaroopg92.github.io/penpa-edit/#...")
```

**PenpaConverter Coordinate Transformation**:

```python
# Internal method: Convert Penpa index to (row, col)
def index_to_coord(self, index: int, type_: str = 'cell'):
    # type_ can be "cell", "edge", "edge_center"
    category, index = divmod(index, self.real_rows * self.real_cols)
    if type_ == "cell":
        return (index // self.real_cols - 2, index % self.real_cols - 2), category
```

### From Janko.at

Janko.at uses a human-readable text format. `JankoConverter` handles parsing:

**Input Format**:
```
{puzzle_type}
{rows} {cols}
{cell_0_0} {cell_0_1} ... {cell_0_{cols-1}}
{cell_1_0} {cell_1_1} ... {cell_1_{cols-1}}
...
{cell_{rows-1}_0} ... {cell_{rows-1}_{cols-1}}
```

Where:
- `puzzle_type`: Puzzle type, e.g., "slitherlink", "nurikabe", etc.
- `rows`, `cols`: Grid dimensions
- Cell values: `-` for empty, digits (0-9) for clues, or other type-specific markers

**Example**:

```python
from puzzlekit.formats.janko_converter import JankoConverter

converter = JankoConverter()

# Slitherlink example
slitherlink_input = """slitherlink
5 5
- - 2 3 -
1 - - - 2
- 3 - 1 -
2 - - - 3
- 1 2 - -"""

puzzle = converter.decode(slitherlink_input)

print(f"Puzzle Type: {puzzle.puzzle_type}")
print(f"Grid Size: {puzzle.rows} x {puzzle.cols}")
print(f"Number of Clues: {len(puzzle.cells)}")

# Access clues at specific positions
if (0, 2) in puzzle.cells:
    print(f"Clue at (0, 2): {puzzle.cells[(0, 2)].clue.value}")
```

**17×17 Slitherlink Full Example**:

```python
from puzzlekit.formats.janko_converter import JankoConverter
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

converter = JankoConverter()

test_input = """slitherlink
17 17
- - - 2 3 2 3 - - 2 - - - 2 2 - -
- - 1 - - - 1 3 - - - - - - - - -
2 - 3 2 1 3 - 3 - - 2 - 2 2 2 2 -
3 - - - 2 - 0 3 - 3 1 - 2 - 1 1 2
- - - - - - - - 1 3 - - - 3 3 2 -
- 1 3 - 3 1 - - 3 - - - - 1 2 - 2
- - 2 1 - 1 2 - 2 2 - - - - - 2 0
3 2 - 2 2 2 2 3 2 - - 1 - - - - -
- 1 3 2 2 - 2 - - 2 3 1 - - - 2 -
- 1 - - - - 2 1 - 2 - 1 2 - - - -
- - - - 2 - 3 2 2 2 3 - 2 2 - 0 2
- 2 1 - 2 3 1 1 - 2 - 2 - 3 - - -
- - 1 1 - 2 1 1 2 3 - - - - 2 2 2
- 3 3 3 2 - 2 3 - 2 1 3 - - 3 2 2
- 2 0 2 1 3 2 1 - 1 - 2 - 1 2 - -
- - 2 3 2 2 - 2 - 2 - 3 - 2 - 2 2
- 2 3 2 - - 2 2 - - - - - 2 3 - -"""

puzzle = converter.decode(test_input)
# puzzle.cells contains all number clues
# puzzle.edges is empty (Slitherlink does not preset edges)

# Convert to puzz.link URL
puzzlink_converter = PuzzlinkConverter()
puzzlink_url = puzzlink_converter.encode(puzzle)
# Output: https://puzz.link/p?slither/17/17/i232dcg2chbg1dm73218d72227dg70...
```

**Supported Puzzle Types**:

`JankoConverter` supports digital grid parsing for the following puzzle families:
- **Slitherlink family**: `slitherlink`, `slither`, `vslither`, `tslither`
- **Nurikabe family**: `nurikabe`, `kurodoko`, `kurochute`, `kurotto`, `nurimisaki`
- **Heyawake family**: `heyawake`, `shikaku`, `aqre`, `shimaguni`, `stostone`
- **Other**: `fillomino`, `tapa`, `tapaloop`

---

## Appendix: Complete Data Flow Example

```python
from puzzlekit.formats.base import PuzzleInstance, CellState, EdgeState, NumberClue
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.formats.penpa_converter import PenpaConverter

# 1. Decode from puzz.link
puzzlink_converter = PuzzlinkConverter()
url = "https://puzz.link/p?heyawake/10/10/..."
puzzle = puzzlink_converter.decode(url)

# 2. Inspect/modify puzzle content
print(f"Original puzzle: {puzzle.puzzle_type}, {puzzle.rows}x{puzzle.cols}")

# Add an extra clue
puzzle.cells[(5, 5)] = CellState(clue=NumberClue(value=10))

# 3. Encode as Penpa URL
penpa_converter = PenpaConverter()
penpa_url = penpa_converter.encode(puzzle)
print(f"Penpa URL: {penpa_url}")

# 4. Or re-encode back to puzz.link URL
new_puzzlink_url = puzzlink_converter.encode(puzzle)
print(f"puzz.link URL: {new_puzzlink_url}")
```

---

## Related Files

| File                                                                                          | Description                                                    |
|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| [`src/puzzlekit/formats/base.py`](../src/puzzlekit/formats/base.py)                           | Core class definitions: PuzzleInstance, CellState, EdgeState   |
| [`src/puzzlekit/formats/puzzlink_converter.py`](../src/puzzlekit/formats/puzzlink_converter.py) | puzz.link format converter                                     |
| [`src/puzzlekit/formats/penpa_converter.py`](../src/puzzlekit/formats/penpa_converter.py)     | Penpa+ format converter                                        |
| [`src/puzzlekit/formats/janko_converter.py`](../src/puzzlekit/formats/janko_converter.py)     | Janko.at format converter (decode support)                     |
| [`src/puzzlekit/formats/puzzle_types.py`](../src/puzzlekit/formats/puzzle_types.py)           | Puzzle type definitions and mappings                           |

---

## License

This documentation is part of the PuzzleKit project. See the main repository for licensing information.
