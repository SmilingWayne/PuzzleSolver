# formats/debug.py
from puzzlekit.formats.penpa_converter import PenpaConverter as Ppc
from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter as Plc
from puzzlekit.formats.base import PuzzleInstance
from typing import Dict, Any, List, Tuple

import json

def compare_edges(edges1: Dict, edges2: Dict) -> List[str]:
    """比较两个 edges dict，返回差异列表"""
    diffs = []
    all_keys = set(edges1.keys()) | set(edges2.keys())
    
    for key in sorted(all_keys):
        e1, e2 = edges1.get(key), edges2.get(key)
        if e1 is None:
            diffs.append(f"❌ edge [{key}] missing in first, expected: {e2}")
        elif e2 is None:
            diffs.append(f"❌ edge [{key}] missing in second, expected: {e1}")
        else:
            # 比较 EdgeState 的各个字段
            if e1.connected != e2.connected:
                diffs.append(f"⚠️  edge [{key}].connected: {e1.connected} != {e2.connected}")
            if e1.edge_type != e2.edge_type:
                diffs.append(f"⚠️  edge [{key}].edge_type: {e1.edge_type} != {e2.edge_type}")
    return diffs


def debug_edges_summary(edges: Dict, label: str = "Edges"):
    """打印 edges 的统计摘要，方便快速定位问题"""
    if not edges:
        print(f"📋 {label}: empty")
        return
    
    # 按 edge_type 分组统计
    type_count = {}
    for edge_state in edges.values():
        t = edge_state.edge_type
        type_count[t] = type_count.get(t, 0) + 1
    
    print(f"📋 {label}: total={len(edges)}, by edge_type: {type_count}")
    
    # 可选：打印前 5 个 edge 详情
    # for i, (k, v) in enumerate(list(edges.items())[:5]):
    #     print(f"   [{k}] -> connected={v.connected}, type={v.edge_type}")

def compare_cells(cells1: Dict, cells2: Dict, tolerance: float = 0) -> List[str]:
    """比较两个 cells dict，返回差异列表"""
    diffs = []
    all_keys = set(cells1.keys()) | set(cells2.keys())
    
    for key in sorted(all_keys):
        c1, c2 = cells1.get(key), cells2.get(key)
        if c1 is None:
            diffs.append(f"❌ [{key}] missing in first: {c2}")
        elif c2 is None:
            diffs.append(f"❌ [{key}] missing in second: {c1}")
        else:
            # 比较各个字段
            for field in ['value', 'num_color', 'num_style', 'surf_color', 'shaded']:
                v1 = getattr(c1, field, None)
                v2 = getattr(c2, field, None)
                # 处理 Enum 比较
                if hasattr(v1, 'value'): v1 = v1.value
                if hasattr(v2, 'value'): v2 = v2.value
                if v1 != v2:
                    diffs.append(f"⚠️  [{key}].{field}: {v1} != {v2}")
    return diffs

def compare_edges(edges1: Dict, edges2: Dict) -> List[str]:
    """比较两个 edges dict"""
    diffs = []
    all_keys = set(edges1.keys()) | set(edges2.keys())
    
    for key in sorted(all_keys):
        e1, e2 = edges1.get(key), edges2.get(key)
        if e1 is None:
            diffs.append(f"❌ edge [{key}] missing in first")
        elif e2 is None:
            diffs.append(f"❌ edge [{key}] missing in second")
        elif e1.edge_type != e2.edge_type or e1.connected != e2.connected:
            diffs.append(f"⚠️  edge [{key}]: {e1} != {e2}")
    return diffs

def debug_roundtrip(converter, url: str, name: str, skip_compare: List[str] = None):
    """
    执行双向转换并打印调试信息
    
    Args:
        converter: 转换器实例 (PuzzlinkConverter 或 PenpaConverter)
        url: 原始 URL
        name: 测试名称
        skip_compare: 跳过比较的字段列表，如 ['metadata', 'source']
    """
    skip_compare = skip_compare or []
    print(f"\n{'='*60}")
    print(f"🔍 {name} Roundtrip Debug")
    print(f"{'='*60}")
    
    # Step 1: Decode
    print(f"\n📥 Decoding: {url[:80]}...")
    ir1 = converter.decode(url)
    print(f"✅ IR decoded: {ir1.rows}x{ir1.cols}, cells={len(ir1.cells)}, edges={len(ir1.edges)}")
    
    # Step 2: Encode
    print(f"\n📤 Encoding back...")
    try:
        url2 = converter.encode(ir1)
        print(f"✅ Encoded URL: {url2[:80]}...")
    except Exception as e:
        print(f"❌ Encode failed: {e}")
        import traceback
        traceback.print_exc()
        return ir1, None, None
    
    # Step 3: Decode again
    print(f"\n📥 Re-decoding encoded URL...")
    ir2 = converter.decode(url2)
    print(f"✅ Re-decoded IR: {ir2.rows}x{ir2.cols}, cells={len(ir2.cells)}, edges={len(ir2.edges)}")
    
    # Step 4: Compare
    print(f"\n🔎 Comparing IRs...")
    all_diffs = []
    
    # 基础属性比较
    for attr in ['rows', 'cols', 'puzzle_type', 'grid_type']:
        if attr in skip_compare: continue
        v1, v2 = getattr(ir1, attr), getattr(ir2, attr)
        if v1 != v2:
            all_diffs.append(f"❌ {attr}: {v1} != {v2}")
        else:
            print(f"✅ {attr}: {v1}")
    
    # margins 比较
    if 'margins' not in skip_compare:
        if ir1.margins != ir2.margins:
            all_diffs.append(f"❌ margins: {ir1.margins} != {ir2.margins}")
        else:
            print(f"✅ margins: {ir1.margins}")
    
    # cells 比较 (只显示前 10 个差异)
    if 'cells' not in skip_compare:
        cell_diffs = compare_cells(ir1.cells, ir2.cells)
        if cell_diffs:
            print(f"⚠️  Cell differences ({len(cell_diffs)} total, showing first 10):")
            for d in cell_diffs[:10]:
                print(f"   {d}")
            if len(cell_diffs) > 10:
                print(f"   ... and {len(cell_diffs) - 10} more")
            all_diffs.extend(cell_diffs)
        else:
            print(f"✅ cells: all {len(ir1.cells)} cells match")
    
    # edges 比较
    if 'edges' not in skip_compare:
        edge_diffs = compare_edges(ir1.edges, ir2.edges)
        if edge_diffs:
            print(f"⚠️  Edge differences ({len(edge_diffs)} total):")
            # 打印详细差异
            for d in edge_diffs[:20]:  # 限制输出数量
                print(f"   {d}")
            if len(edge_diffs) > 20:
                print(f"   ... and {len(edge_diffs) - 20} more")
            all_diffs.extend(edge_diffs)
        else:
            print(f"✅ edges: all {len(ir1.edges)} edges match")
        
        # 打印 edges 摘要（可选，方便调试）
        debug_edges_summary(ir1.edges, "IR1 Edges")
        debug_edges_summary(ir2.edges, "IR2 Edges")
    # Summary
    print(f"\n{'-'*60}")
    if all_diffs:
        print(f"🔴 FAILED: {len(all_diffs)} differences found")
        # 可选：保存差异到文件
        # with open(f"debug_{name}_diffs.txt", "w") as f:
        #     f.write("\n".join(all_diffs))
    else:
        print(f"🟢 SUCCESS: Roundtrip perfect! ✅")
    print(f"{'-'*60}\n")
    
    return ir1, ir2, all_diffs

def debug_nonogram_specific(ir: Any):
    """针对 nonogram 的专项调试：打印 margin 区域的数字"""
    if ir.puzzle_type != "nonogram":
        return
    
    print(f"\n🧩 Nonogram Specific Debug ({ir.rows}x{ir.cols}, margins={ir.margins})")
    rows_offset, cols_offset = ir.margins[0], ir.margins[2]
    
    # 打印顶部行提示 (row clues)
    print(f"\n📋 Top row clues (rows 0~{rows_offset-1}):")
    for r in range(rows_offset):
        clues = [(c, ir.cells[(r, c)].value) for c in range(ir.cols) 
                 if (r, c) in ir.cells and ir.cells[(r, c)].value]
        if clues:
            print(f"   Row {r}: {clues}")
    
    # 打印左侧列提示 (col clues)
    print(f"\n📋 Left col clues (cols 0~{cols_offset-1}):")
    for c in range(cols_offset):
        clues = [(r, ir.cells[(r, c)].value) for r in range(ir.rows) 
                 if (r, c) in ir.cells and ir.cells[(r, c)].value]
        if clues:
            print(f"   Col {c}: {clues}")

def compare_ir(ir1: PuzzleInstance, ir2: PuzzleInstance, 
               ignore_fields: List[str] = None,
               verbose: bool = True) -> Tuple[bool, List[str]]:
    """
    Cross-compare two PuzzleInstance objects.
    
    Args:
        ir1, ir2: Two PuzzleInstance to compare
        ignore_fields: Fields to skip comparison (e.g., ['source', 'metadata', 'author'])
        verbose: Whether to print detailed differences
    
    Returns:
        (is_equal: bool, diffs: List[str])
    """
    ignore_fields = ignore_fields or ['source', 'metadata', 'author', 'title']
    diffs = []
    
    # ===== 1. 基础属性对比 =====
    basic_fields = ['grid_type', 'puzzle_type', 'rows', 'cols', 'margins', 'boxes']
    for field in basic_fields:
        if field in ignore_fields:
            continue
        v1, v2 = getattr(ir1, field, None), getattr(ir2, field, None)
        if v1 != v2:
            diffs.append(f"❌ {field}: {v1} != {v2}")
        elif verbose:
            print(f"✅ {field}: {v1}")
    
    # ===== 2. Cells 对比 =====
    if 'cells' not in ignore_fields:
        cell_diffs = _compare_cells_detail(ir1.cells, ir2.cells)
        if cell_diffs:
            diffs.extend(cell_diffs)
            if verbose:
                print(f"⚠️  Cell differences ({len(cell_diffs)}):")
                for d in cell_diffs[:10]:
                    print(f"   {d}")
                if len(cell_diffs) > 10:
                    print(f"   ... and {len(cell_diffs) - 10} more")
        elif verbose and ir1.cells:
            print(f"✅ cells: all {len(ir1.cells)} cells match")
    
    # ===== 3. Edges 对比 =====
    if 'edges' not in ignore_fields:
        edge_diffs = _compare_edges_detail(ir1.edges, ir2.edges)
        if edge_diffs:
            diffs.extend(edge_diffs)
            if verbose:
                print(f"⚠️  Edge differences ({len(edge_diffs)}):")
                for d in edge_diffs[:10]:
                    print(f"   {d}")
                if len(edge_diffs) > 10:
                    print(f"   ... and {len(edge_diffs) - 10} more")
        elif verbose and ir1.edges:
            print(f"✅ edges: all {len(ir1.edges)} edges match")
    
    # ===== 4. 可选：CellState/EdgeState 字段级对比配置 =====
    # 如需更细粒度控制，可扩展 _compare_cells_detail 的 compare_fields 参数
    
    is_equal = len(diffs) == 0
    if verbose:
        print(f"\n{'='*50}")
        if is_equal:
            print("🟢 IRs are SEMANTICALLY EQUAL ✅")
        else:
            print(f"🔴 IRs DIFFER: {len(diffs)} issues found")
        print(f"{'='*50}\n")
    
    return is_equal, diffs


def _compare_cells_detail(cells1: Dict, cells2: Dict, 
                          compare_fields: List[str] = None) -> List[str]:
    """
    详细对比两个 cells dict，返回差异列表。
    """
    if compare_fields is None:
        compare_fields = ['value', 'num_color', 'num_style', 'surf_color', 'shaded']
    
    diffs = []
    all_keys = set(cells1.keys()) | set(cells2.keys())
    
    # 先检查数量
    if len(cells1) != len(cells2):
        diffs.append(f"❌ cells count: {len(cells1)} != {len(cells2)}")
    
    for key in sorted(all_keys):
        c1, c2 = cells1.get(key), cells2.get(key)
        
        if c1 is None:
            diffs.append(f"❌ [{key}] missing in ir1, ir2 has: {c2}")
            continue
        if c2 is None:
            diffs.append(f"❌ [{key}] missing in ir2, ir1 has: {c1}")
            continue
        
        # 字段级对比
        for field in compare_fields:
            v1 = getattr(c1, field, None)
            v2 = getattr(c2, field, None)
            # 处理 Enum 值比较
            if hasattr(v1, 'value'): v1 = v1.value
            if hasattr(v2, 'value'): v2 = v2.value
            if v1 != v2:
                diffs.append(f"⚠️  [{key}].{field}: '{v1}' != '{v2}'")
    
    return diffs


def _compare_edges_detail(edges1: Dict, edges2: Dict) -> List[str]:
    """
    详细对比两个 edges dict，返回差异列表。
    """
    diffs = []
    all_keys = set(edges1.keys()) | set(edges2.keys())
    
    if len(edges1) != len(edges2):
        diffs.append(f"❌ edges count: {len(edges1)} != {len(edges2)}")
    
    for key in sorted(all_keys):
        # key 是 ((r1,c1), (r2,c2)) 元组，需要标准化顺序
        k_std = tuple(sorted(key)) if isinstance(key, tuple) and len(key) == 2 else key
        
        e1 = edges1.get(key) or edges1.get(k_std)
        e2 = edges2.get(key) or edges2.get(k_std)
        
        if e1 is None:
            diffs.append(f"❌ edge {key} missing in ir1")
            continue
        if e2 is None:
            diffs.append(f"❌ edge {key} missing in ir2")
            continue
        
        if e1.connected != e2.connected:
            diffs.append(f"⚠️  edge {key}.connected: {e1.connected} != {e2.connected}")
        if e1.edge_type != e2.edge_type:
            diffs.append(f"⚠️  edge {key}.edge_type: {e1.edge_type} != {e2.edge_type}")
    
    return diffs


# ============ 主测试入口 ============


if __name__ == "__main__":
    # 测试 URL
    PUZZLINK_URL = "https://puzz.link/p?nurikabe/10/10/j2m3i2i2h.j6t4k..k3t6j.h4i4i2m2j"
    PENPA_URL = "m=edit&p=7VZrb+o4EP3Or1j5ay2Ik5AbIlUVz0pVy5YtXbYghAKYJpDE3DzaKoj/3rEDJQ5ppd2VVl3pKniYOWPPw8YnRD8TO6SYKPyjmRi+4dGJKYZqGmIoh2foxh61fsPNJHZYCIoTx9vIqtW2STpOx1XPDTa17VWQhO7GntMaUfhnrfqaq7qqU10bsb6pVjdabKyrju7qruqra4x/7/XwyvYiim+e1q3Opvnabf5Vq4817bG/ulh3Bo/r5ehPMlDcWqj0PTO4u++0vIvrdHznNF9olxr3EVs4HrWXdjoe3bx5Qc98dlakfeO0zZUdKNFPc9h4aQ0uLyuTQzfTyi5tWGkTp9fWBBGEkQqDoClOB9YuvbPQgvlzF+H0AfwIkylGfuLF7oJ5LERHLL3NVqugdk/qSPi51s5AooDeP+igPoG6cMOFR2e3GXJvTdIhRryAlljNVeSzF8qT8QK5nRUFwNyO4TQix90irIEjSpZskxymkukep81/0AZEOrbB1awNrpW0wbv79214W1bSQGO638MB/QEtzKwJ7+bxpJon9cHagexbO6TpsFSFX684Q6QbYGofZl2RvHVTMg3C015BA0eArzY+TLMBpv5hNuqF6UTh4WVEzk9UHuIUkYhypRXaDykJ0XmWvM0jnGomouijDZtAxFY8CdkTUhVyCDuFU03IjpCKkHUhb8WcrpAjIdtC6kIaYs4Pvtd/6zT+g3ImWkZW8lP//2HTygQ9JOHKXlC4HG3mb1nkxhQBQaGIebMo883om72IkZURZd4jYUHizync6xzkMbYFai6LcHRJoPscsJCWujhIl8+fheKuklBzFi4LNb3anif3It5EEpTxigTFIZBGzrbDkL1KiG/HjgTkeFKKRIPCZsa2XKK9sQvZ/NN27CvoDYkBlxwu4a+3ybd/m/DDUr4bi323csTvnIVfkM7JWYRLqAfQL9gn5y3DPyGanLeIn7EKL/acWAAt4RZAi/QC0DnDAHhGMoB9wjM8apFqeFVFtuGpzgiHp8pzzgQd/1ujaeUd"
    plc = Plc()
    ppc = Ppc()
    ir1 = plc.decode(PUZZLINK_URL)
    ir2 = ppc.decode(PENPA_URL)
    # debug_roundtrip(plc, PUZZLINK_URL, "Puzzlink Nonogram", skip_compare=['source', 'metadata'])
    

    print("\n🔍 Cross-comparing IR1 vs IR2:")
    is_equal, diffs = compare_ir(ir1, ir2, ignore_fields=['source', 'metadata'])