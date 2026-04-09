# PuzzleInstance 数据结构文档

> PuzzleInstance 是 PuzzleKit 中的**中间表示（Intermediate Representation, IR）**，用于在不同谜题格式（如 puzz.link、Penpa+、Janko 等）之间进行统一的转换和处理。

---

## 目录

1. [核心结构概览](#核心结构概览)
2. [坐标系统详解](#坐标系统详解)
3. [CellState: 单元格状态](#cellstate-单元格状态)
4. [EdgeState: 边状态](#edgestate-边状态)
5. [Clue Types: 线索类型](#clue-types-线索类型)
6. [实际使用示例](#实际使用示例)
7. [从不同格式转换](#从不同格式转换)

---

## 核心结构概览

`PuzzleInstance` 定义于 [`src/puzzlekit/formats/base.py`](../src/puzzlekit/formats/base.py)，是一个数据类（dataclass），包含以下核心字段：

```python
@dataclass
class PuzzleInstance:
    grid_type: str = "square"           # 网格类型（目前主要支持 "square"）
    puzzle_type: str = "heyawake"       # 谜题类型（如 "heyawake", "slitherlink" 等）
    title: str = ""                     # 谜题标题
    author: str = ""                    # 作者
    source: str = ""                    # 来源
    rows: int = 0                       # 网格行数（含 margins）
    cols: int = 0                       # 网格列数（含 margins）
    margins: List[int] = field(default_factory=list)  # [上，下，左，右] 边距
    boxes: List[Any] = field(default_factory=list)    # 区域/房间划分元数据
    edges: Dict[tuple, EdgeState] = field(default_factory=dict)  # 边状态字典
    cells: Dict[tuple, CellState] = field(default_factory=dict)  # 单元格状态字典
    metadata: Dict[str, Any] = field(default_factory=dict)       # 额外元数据
```

---

## 坐标系统详解

### 坐标系定义

PuzzleInstance 使用 **(row, col)** 的二维坐标系统，其中：

- **row**: 从上到下递增，从 0 开始
- **col**: 从左到右递增，从 0 开始

### 带边距的坐标系统

```
┌─────────────────────────────────────────────────┐
│               top_margin                        │
│       ┌────────────────────────────────┐        │
│       │                                │        │
│       │    Actual Grid Region          │        │
│left   │     (rows - top - bottom) ×    │   right│ 
│margin │     (cols - left - right)      │  margin│
│       │                                │        │
│       │                                │        │
│       └────────────────────────────────┘        │
│               bottom_margin                     │
└─────────────────────────────────────────────────┘

```

**示例**: 一个 10x10 的谜题，如果有 `margins = [2, 2, 1, 1]`：
- `rows = 14` (2 + 10 + 2)
- `cols = 12` (1 + 10 + 1)
- 实际谜题区域从坐标 `(2, 1)` 开始，到 `(11, 10)` 结束

### cells 字典的键

`cells` 字典使用 `(row, col)` 元组作为键：

```python
# 示例：在位置 (3, 5) 放置一个数字 clue
puzzle.cells[(3, 5)] = CellState(clue=NumberClue(value=42))
```

### edges 字典的键

`edges` 字典使用**两个坐标点**的元组作为键，表示一条边连接的两个单元格：

```python
# 示例：在 (2, 3) 和 (2, 4) 之间放置一条粗黑边
puzzle.edges[((2, 3), (2, 4))] = EdgeState(connected=True, edge_type=2)
```

**注意**: 边的两个端点坐标顺序不重要，系统会自动规范化。但是写的时候，最好遵循**从左到右，从上到下**（左在前、上在前）的顺序。

---

## CellState: 单元格状态

`CellState` 描述单个单元格的所有状态信息：

```python
@dataclass
class CellState:
    clue: Optional[Clue] = None      # 线索（数字、箭头、文本等）
    fill: Optional[Color] = None     # 填充颜色
    symbol: Optional[SymbolState] = None  # 符号标记
    shaded: bool = False             # 是否为黑色单元格（语义标记）
```

### 属性说明

| 属性     | 类型                    | 说明                                           |
| -------- | ----------------------- | ---------------------------------------------- |
| `clue`   | `Optional[Clue]`        | 单元格中的线索，如数字、箭头等                 |
| `fill`   | `Optional[str]`         | 填充颜色，如 `"black"`, `"gray"`, `"red"` 等   |
| `symbol` | `Optional[SymbolState]` | 符号标记，如圆圈、叉号等                       |
| `shaded` | `bool`                  | 是否为黑色单元格（用于 Heyawake、Nurikabe 等） |

### SymbolState 符号标记

```python
@dataclass
class SymbolState:
    symbol_index: int = 0       # 符号索引（Penpa 兼容）
    symbol_type: str = "circle_L"  # 符号类型，如 "circle_L", "x", "sun_moon" 等
    symbol_style: int = 1       # 符号样式
```

---

## EdgeState: 边状态

`EdgeState` 描述两个单元格之间的边（边界线）状态：

```python
@dataclass
class EdgeState:
    connected: bool = True        # 是否连通（细线）
    edge_type: int = 2            # 边类型：2 = 粗黑线，13 = 虚线等
    symbol: Optional[SymbolState] = None  # 边上的符号，如 ">", "<", "x" 等
```

### 常见边类型

| edge_type | 说明                         |
| --------- | ---------------------------- |
| `2`       | 默认粗黑边框                 |
| `13`      | 虚线边框                     |
| `-1`      | 自定义边（配合 symbol 使用） |

---

## Clue Types: 线索类型

PuzzleKit 支持多种线索类型，用于表示不同谜题的数字、箭头等标记。

### NumberClue（数字线索）

```python
@dataclass
class NumberClue:
    kind: str = "number"
    value: Union[int, str] = ""  # 数字值，可以是整数或字符串
```

**使用示例**:
```python
CellState(clue=NumberClue(value=42))
CellState(clue=NumberClue(value="5"))  # 字符串形式
```

### ArrowClue（箭头线索）

```python
@dataclass
class ArrowClue:
    kind: str = "arrow"
    value: Optional[Union[int, str]] = None  # 箭头旁的数字（可选）
    direction: Direction = Direction.N       # 箭头方向
```

**方向枚举**:
```python
class Direction(str, Enum):
    N = "n"    # 北/上
    S = "s"    # 南/下
    W = "w"    # 西/左
    E = "e"    # 东/右
    NW = "nw"  # 西北
    NE = "ne"  # 东北
    SW = "sw"  # 西南
    SE = "se"  # 东南
```

**使用示例**:
```python
CellState(clue=ArrowClue(value=5, direction=Direction.E))
```

### TapaClue（Tapa 线索）

```python
@dataclass
class TapaClue:
    kind: str = "tapa"
    value: Optional[Union[int, str]] = None  # Tapa 数字串，如 "3 1 2"
```

### TextClue（文本线索）

```python
@dataclass
class TextClue:
    kind: str = "text"
    text: str = ""  # 文本内容
```

---

## 实际使用示例

### 示例 1: 创建一个简单的 Heyawake 谜题

```python
from puzzlekit.formats.base import (
    PuzzleInstance, CellState, EdgeState, NumberClue
)

# 创建一个 5x5 的 Heyawake 谜题
puzzle = PuzzleInstance(
    grid_type="square",
    puzzle_type="heyawake",
    title="示例谜题",
    rows=5,
    cols=5,
    margins=[0, 0, 0, 0],
)

# 添加数字线索
puzzle.cells[(0, 0)] = CellState(clue=NumberClue(value=3))
puzzle.cells[(2, 2)] = CellState(clue=NumberClue(value=5))

# 添加粗黑边（房间边界）
puzzle.edges[((0, 1), (0, 2))] = EdgeState(connected=True, edge_type=2)
puzzle.edges[((1, 1), (1, 2))] = EdgeState(connected=True, edge_type=2)
puzzle.edges[((2, 1), (2, 2))] = EdgeState(connected=True, edge_type=2)

print(puzzle)
```

### 示例 2: 使用 PuzzlinkConverter 解码 URL

```python
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

converter = PuzzlinkConverter()
url = "https://puzz.link/p?heyawake/10/10/..."
puzzle = converter.decode(url)

# 访问 puzzle 中的数据
print(f"谜题类型：{puzzle.puzzle_type}")
print(f"网格大小：{puzzle.rows} x {puzzle.cols}")
print(f"单元格数量：{len(puzzle.cells)}")
print(f"边数量：{len(puzzle.edges)}")

# 遍历所有有线索的单元格
for (r, c), cell_state in puzzle.cells.items():
    if cell_state.clue:
        print(f"位置 ({r}, {c}) 有线索：{cell_state.clue}")
```

### 示例 3: 使用 PenpaConverter 解码/编码

```python
from puzzlekit.formats.penpa_converter import PenpaConverter

converter = PenpaConverter()

# 解码 Penpa URL
penpa_url = "https://swaroopg92.github.io/penpa-edit/#m=edit&p=..."
puzzle = converter.decode(penpa_url)

# 编码回 Penpa URL
new_url = converter.encode(puzzle)
```

---

## 从不同格式转换

### 从 puzz.link 转换

puzz.link 使用紧凑的编码格式，通过 `PuzzlinkConverter` 可以解码为 `PuzzleInstance`：

```python
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter

converter = PuzzlinkConverter()
puzzle = converter.decode("https://puzz.link/p?heyawake/5/5/...")
```

**坐标映射**: puzz.link 的坐标直接映射到 PuzzleInstance 的 `(row, col)`，从 `(0, 0)` 开始。

### 从 Penpa+ 转换

Penpa+ 使用复杂的索引系统，`PenpaConverter` 负责坐标转换：

**Penpa 索引系统**:
- Penpa 使用一维索引表示单元格位置
- 索引计算考虑了边距和 padding
- 转换公式：`index = row * real_cols + col + offset`

```python
from puzzlekit.formats.penpa_converter import PenpaConverter

converter = PenpaConverter()
puzzle = converter.decode("https://swaroopg92.github.io/penpa-edit/#...")
```

**PenpaConverter 的坐标转换方法**:

```python
# 内部方法：将 Penpa 索引转换为 (row, col)
def index_to_coord(self, index: int, type_: str = 'cell'):
    # type_ 可以是 "cell", "edge", "edge_center"
    category, index = divmod(index, self.real_rows * self.real_cols)
    if type_ == "cell":
        return (index // self.real_cols - 2, index % self.real_cols - 2), category
```

### 从 Janko.at 转换

Janko.at 使用人类可读的文本格式，`JankoConverter` 负责解析：

**输入格式**:
```
{puzzle_type}
{rows} {cols}
{cell_0_0} {cell_0_1} ... {cell_0_{cols-1}}
{cell_1_0} {cell_1_1} ... {cell_1_{cols-1}}
...
{cell_{rows-1}_0} ... {cell_{rows-1}_{cols-1}}
```

其中：
- `puzzle_type`: 谜题类型，如 "slitherlink", "nurikabe" 等
- `rows`, `cols`: 网格尺寸
- 单元格值：`-` 表示空，数字 (0-9) 表示线索，或其他类型特定的标记

**示例**:

```python
from puzzlekit.formats.janko_converter import JankoConverter

converter = JankoConverter()

# Slitherlink 示例
slitherlink_input = """slitherlink
5 5
- - 2 3 -
1 - - - 2
- 3 - 1 -
2 - - - 3
- 1 2 - -"""

puzzle = converter.decode(slitherlink_input)

print(f"谜题类型：{puzzle.puzzle_type}")
print(f"网格大小：{puzzle.rows} x {puzzle.cols}")
print(f"线索数量：{len(puzzle.cells)}")

# 访问特定位置的线索
if (0, 2) in puzzle.cells:
    print(f"位置 (0, 2) 的线索：{puzzle.cells[(0, 2)].clue.value}")
```

**17x17 Slitherlink 完整示例**:

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
# puzzle.cells 包含所有数字线索
# puzzle.edges 为空字典（Slitherlink 不预设边）

# 转换为 puzz.link URL
puzzlink_converter = PuzzlinkConverter()
puzzlink_url = puzzlink_converter.encode(puzzle)
# 输出：https://puzz.link/p?slither/17/17/i232dcg2chbg1dm73218d72227dg70...
```

**支持的谜题类型**:

`JankoConverter` 支持以下谜题类型的数字网格解析：
- Slitherlink 家族：`slitherlink`, `slither`, `vslither`, `tslither`
- Nurikabe 家族：`nurikabe`, `kurodoko`, `kurochute`, `kurotto`, `nurimisaki`
- Heyawake 家族：`heyawake`, `shikaku`, `aqre`, `shimaguni`, `stostone`
- 其他：`fillomino`, `tapa`, `tapaloop`

## 附录：完整的数据流示例

```python
from puzzlekit.formats.base import PuzzleInstance, CellState, EdgeState, NumberClue
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.formats.penpa_converter import PenpaConverter

# 1. 从 puzzlink 解码
puzzlink_converter = PuzzlinkConverter()
url = "https://puzz.link/p?heyawake/10/10/..."
puzzle = puzzlink_converter.decode(url)

# 2. 检查/修改 puzzle 内容
print(f"原始谜题：{puzzle.puzzle_type}, {puzzle.rows}x{puzzle.cols}")

# 添加额外的线索
puzzle.cells[(5, 5)] = CellState(clue=NumberClue(value=10))

# 3. 编码为 Penpa URL
penpa_converter = PenpaConverter()
penpa_url = penpa_converter.encode(puzzle)
print(f"Penpa URL: {penpa_url}")

# 4. 或者重新编码回 puzzlink URL
new_puzzlink_url = puzzlink_converter.encode(puzzle)
print(f"puzz.link URL: {new_puzzlink_url}")
```

---

## 相关文件

| 文件                                                                                            | 说明                                              |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| [`src/puzzlekit/formats/base.py`](../src/puzzlekit/formats/base.py)                             | PuzzleInstance、CellState、EdgeState 等核心类定义 |
| [`src/puzzlekit/formats/puzzlink_converter.py`](../src/puzzlekit/formats/puzzlink_converter.py) | puzz.link 格式转换器                              |
| [`src/puzzlekit/formats/penpa_converter.py`](../src/puzzlekit/formats/penpa_converter.py)       | Penpa+ 格式转换器                                 |
| [`src/puzzlekit/formats/janko_converter.py`](../src/puzzlekit/formats/janko_converter.py)       | Janko.at 格式转换器（支持 decode）                |
| [`src/puzzlekit/formats/puzzle_types.py`](../src/puzzlekit/formats/puzzle_types.py)             | 谜题类型定义和映射                                |
