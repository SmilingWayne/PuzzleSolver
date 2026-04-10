#!/usr/bin/env python3
"""
Test script for Slitherlink inference engine.

Usage:
    python test_slither_inference.py [--verbose]
"""

import argparse

from puzzlekit.formats.puzzlink_converter import PuzzlinkConverter
from puzzlekit.formats.penpa_converter import PenpaConverter
from puzzlekit.formats.base import NumberClue
from puzzlekit.inference import (
    initial_state_from_instance,
    apply_trace,
    project_state_to_instance,
)
from puzzlekit.inference.rules.slither import create_engine


def main():
    parser = argparse.ArgumentParser(description="Run Slitherlink inference trace demo")
    parser.add_argument("--verbose", action="store_true", help="print per-step edge updates")
    args = parser.parse_args()

    # Test URL: https://puzz.link/p?slither/10/10/g81cg18bgci7dg86dg878abnd888cg78dg8cidg53dg36d
    # test_url = "https://puzz.link/p?slither/60/60/211732328cd282177cccdi3228338327c262111c732dg016bg22ci7122b72c62cg231232ci3cibh37dh2121822d81237213277cd821212021d7612b657233dg873223c8378d77377ch2bg1223bh372c7cg2122bgb1211bhbi32222122323c623ck8327212c22238887228828222262322bg3225233328d71282cg3bg6cgcg121777cg23cgc2dh227dh8bg7728122cj66cj3db212111232317222cg8122277162323282dj3776bh3772d721b0ch232cg227121217370832c72327722c127b7ch22772278dg22dg2836ch23b671c231d7112222c2121cibj1cag2c772cg287dg2bg1cg3222383333ch33d2c1b217377d222ck3bg71272112bh7bg137c321ddc1cg1cg71d32122313bch172271cg28cg1cg2cj3d3212b2c217dcg23222227626a2121182c237336cbg26771ch88dg372d326371232cd6617221810ddbg087b2cg2b32326b8322d62c2221873cg23bg11cd232232372767dg512772178cj2c2321312c8c1dgdh72d21dj21b11c20283222ch7b18722872112b12cb2cg23212c6372b2c3622cg12c66627bgdh327786666dgchcc1dccgcgck61cl3cgd88dg212b23112571726222132c82dg3122dg123b236c12c72c1dg31732372372c2322cg37132ddj73c32122228277cc12c122ccg2217c66c117b272617ci23bh8178c883327d2cg12613b1cg1816dch32dgbidhc1cid2a383cj22dgcg23ci2671211c3223cg32183383172112112bg2621323178322327267322c67c12bh1283237c2bkb872222cdg7ag281ch2b333ci72728732c6228632bg257d1b72c2232bbd2cc1222a2b6671232332dg18281322137373233b232617bc28772cgcbh3281ci2321221cg2bi78bg71d3d1322bj12302226c22cg281636127221122327632217bhcch223cd3728623ci18222231ch18082610c1722262227cg2cg771c12cc2222cg0bi3368867722c62227222127ci27377cg7117d27812cg3d372212cgch222c212c67716cgabg3ci27611312b1220221272cg6c7dg22773712cd1221c2d216376bg232632c2182113671c21107b822ci7c7771376228b2162di76ddh32c2762dg71c2c12c6bi2b7cn2cg3ch2735726173ccg2228d7763211727177723213cg21d2333216d2dg27c163cgc7d83cl7312223121c66b0267317c765c7321212d17c2cg3bicc202d213321d236272c282dibg6a20b283761bg72112cc6238cg21bd8128228d2127218832872cg3bcd5021cj26d1dg2127dccg2cg21cg2622187837823218dg8231c23c61132272126722bci0121cgcg11bahcg2218b27c1263236b8722b8720chcg87837272833cg2228db332376b21c773c3212cgc2cg22c723ci31bhbg26bi2127712132712722362b7c82123227222bmdg33ci13231b2ccg2b8272bi2327dc2222876c22dgal132dg36172cgdg222373223ch33c62723128722271db7ch272217c2327222822bg27222867did1321322211212b1312c22617ccg6772cg2317cg7bh218c8d8137287dg3"
    test_url = "https://puzz.link/p?slither/10/10/g81cg18bgci7dg86dg878abnd888cg78dg8cidg53dg36d"

    print("=" * 70)
    print("Slitherlink Inference Engine Test")
    print("=" * 70)
    print(f"\nTest URL: {test_url}")

    # 1. Decode puzzle from puzz.link URL
    print("\n[1] Decoding puzzle from puzz.link URL...")
    converter = PuzzlinkConverter()
    instance = converter.decode(test_url)

    print(f"    Puzzle type: {instance.puzzle_type}")
    print(f"    Grid size: {instance.rows} x {instance.cols}")
    print(f"    Number of clues: {len(instance.cells)}")

    # Print the clue grid
    print("\n    Clue grid:")
    print("    " + "-" * (instance.cols * 3 - 1))
    for r in range(instance.rows):
        row_str = "    "
        for c in range(instance.cols):
            cell = instance.cells.get((r, c))
            if cell and cell.clue and isinstance(cell.clue, NumberClue):
                row_str += f"{cell.clue.value}  "
            else:
                row_str += "-  "
        print(row_str)
    print("    " + "-" * (instance.cols * 3 - 1))

    # 2. Initialize inference state
    print("\n[2] Initializing inference state...")
    initial_state = initial_state_from_instance(instance)
    print(f"    Initial state: {initial_state.num_rows} x {initial_state.num_cols}")
    print(f"    Initial cell_values: {len(initial_state.cell_values)}")
    print(f"    Initial edge_values: {len(initial_state.edge_values)}")

    # 3. Run inference engine
    print("\n[3] Running Slitherlink inference engine...")
    engine = create_engine()
    trace = engine.infer(instance, initial_state)

    print(f"    Engine: {trace.engine} v{trace.engine_version}")
    print(f"    Total steps: {len(trace.steps)}")
    print(f"    Complete: {trace.complete}")

    # 4. Print inference steps
    print("\n[4] Inference Steps (by strategy rule):")
    print("    " + "-" * 66)
    for step in trace.steps:
        print(f"    Step {step.index}: [{step.kind.value}]")
        print(f"        Rule: {step.rule_id}")
        print(f"        {step.message}")
        if step.edge_updates:
            print(f"        Edge updates: {len(step.edge_updates)} edges")
            if args.verbose:
                for key, val in sorted(step.edge_updates.items()):
                    status = "LINE" if val is True else "CROSS" if val is False else str(val)
                    print(f"            {key}: {status}")
    print("    " + "-" * 66)
    print(f"    Rule stats: {trace.metadata.get('rule_stats', {})}")

    # 5. Apply trace to get final state
    print("\n[5] Applying inference trace to state...")
    final_state = apply_trace(initial_state, trace)
    print(f"    Final cell_values: {len(final_state.cell_values)}")
    print(f"    Final edge_values: {len(final_state.edge_values)}")

    # 6. Project to PuzzleInstance for visualization
    print("\n[6] Projecting state to PuzzleInstance...")
    result_instance = project_state_to_instance(instance, final_state)
    print(f"    Result instance created with metadata: {result_instance.metadata.keys()}")

    # 7. Show edge status summary
    print("\n[7] Edge Status Summary:")
    connected_count = 0
    crossed_count = 0

    for key, val in final_state.edge_values.items():
        if isinstance(val, bool):
            if val:
                connected_count += 1
            else:
                crossed_count += 1
        elif isinstance(val, str):
            if val.strip().lower() in {"on", "true", "1", "connected"}:
                connected_count += 1
            else:
                crossed_count += 1

    # Also check metadata for edge_marks
    edge_marks_connected = 0
    edge_marks_cross = 0
    if "edge_marks" in result_instance.metadata.get("inference_overlay", {}):
        for key, mark in result_instance.metadata["inference_overlay"]["edge_marks"].items():
            if mark == 1:  # EdgeMark.LINK
                edge_marks_connected += 1
            elif mark == 2:  # EdgeMark.CROSS
                edge_marks_cross += 1

    print(f"    Connected edges (line): {connected_count}")
    print(f"    Crossed edges (×): {crossed_count}")
    print(f"    Total determined: {connected_count + crossed_count}")

    # Show sample edges
    print("\n    Sample edges (first 10):")
    for i, (key, val) in enumerate(final_state.edge_values.items()):
        if i >= 10:
            break
        if val is True:
            status = "LINE"
        elif val is False:
            status = "CROSS"
        else:
            status = f"UNKNOWN({val})"
        print(f"      {key}: {status}")

    # 8. Convert result back to puzz.link URL (optional)
    print("\n[8] Encoding result back to puzz.link URL...")

    converter_2 = PenpaConverter()
    result_url = converter_2.encode(result_instance)
    print(f"    Result URL: {result_url}")

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
