# ==========================================
# Generate Markdown documentation for all puzzles in docs/puzzles
# Usage: python scripts/gen_docs.py
# ==========================================

import os
import sys
import inspect
import textwrap
import importlib.util
from pathlib import Path
from typing import Dict, Any, List

# ==========================================
# Configuration
# ==========================================
PROJECT_ROOT = Path(__file__).parent.parent
SOLVERS_DIR = PROJECT_ROOT / "src" / "puzzlekit" / "solvers"
DOCS_OUTPUT_DIR = PROJECT_ROOT / "docs" / "puzzles"

# Add src to path for importing modules
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from puzzlekit.core.solver import PuzzleSolver

# ==========================================
# Helper Functions
# ==========================================

def clean_doc_string(text: str) -> str:
    """Remove indentation and trim leading/trailing whitespace from multi-line strings"""
    if not text:
        return ""
    return textwrap.dedent(text).strip()

def render_badges(tags: List[str]) -> str:
    """Generate beautiful tag badges (using Shields.io style or simple Markdown code blocks)"""
    if not tags or tags == [""]:
        return ""
    # Here we use simple Markdown Code style, which is the most compatible.
    # If using MkDocs Material, you can use :octicons-tag-24: etc. icons
    return " ".join([f"`{tag}`" for tag in tags if tag])

def format_difficulty(diff: str) -> str:
    """Format difficulty display"""
    if not diff:
        return "Not Rated"
    # Add some Emojis
    if str(diff) in ["1", "2", "Easy"]:
        return f"🟢 {diff}"
    if str(diff) in ["3", "Medium"]:
        return f"🟡 {diff}"
    if str(diff) in ["4", "5", "Hard"]:
        return f"🔴 {diff}"
    return diff

def generate_markdown_content(filename: str, meta: Dict[str, Any]) -> str:
    """Core logic: convert metadata dictionary to Markdown text"""
    
    # 1. Prepare data
    name = meta.get("name") or filename.replace("_", " ").title()
    aliases = [a for a in meta.get("aliases", []) if a]
    rule_url = meta.get("rule_url", "")
    tags = [t for t in meta.get("tags", []) if t]
    difficulty = meta.get("difficulty", "")
    
    external_links = meta.get("external_links", [])
    
    input_desc = clean_doc_string(meta.get("input_desc", ""))
    output_desc = clean_doc_string(meta.get("output_desc", ""))
    input_example = clean_doc_string(meta.get("input_example", ""))
    output_example = clean_doc_string(meta.get("output_example", ""))

    # 2. Start building Markdown
    lines = []
    
    # --- Title ---
    lines.append(f"# {name}")
    lines.append("")
    
    # --- Meta Info Block (Badges & Rules) ---
    meta_lines = []
    if difficulty:
        meta_lines.append(f"**Difficulty**: {format_difficulty(difficulty)}")
    if tags:
        meta_lines.append(f"**Tags**: {render_badges(tags)}")
    if aliases:
        meta_lines.append(f"**Aliases**: {', '.join(aliases)}")
    
    if meta_lines:
        lines.append(" | ".join(meta_lines))
        lines.append("")

    # --- Introduction / Rules ---
    if rule_url:
        lines.append(f"> 📖 **Rule Reference**: [Read full rules on external site]({rule_url})")
        lines.append("")

    # --- External Play Links ---
    if external_links:
        links_md = []
        for link_obj in external_links:
            # Compatible with {"Name": "URL"} format
            for label, url in link_obj.items():
                links_md.append(f"[{label}]({url})")
        if links_md:
            lines.append(f"🎮 **Play Online**: " + " • ".join(links_md))
            lines.append("")
    
    lines.append("---")
    lines.append("")

    # --- Input Format ---
    lines.append("## Input Format")
    if input_desc:
        lines.append(input_desc)
    else:
        lines.append("*No input description provided.*")
    lines.append("")

    # --- Output Format ---
    lines.append("## Output Format")
    if output_desc:
        lines.append(output_desc)
    else:
        lines.append("*No output description provided.*")
    lines.append("")

    # --- Examples (Side by Side if possible, or sequential) ---
    lines.append("## Examples")
    lines.append("")
    
    if input_example:
        
        formatted_problem_str = textwrap.indent(input_example, '    ')
        
        puzzle_key = filename 

        code_block = f"""
### Python Quick Start
Use the following code to solve this puzzle directly:

```python
import puzzlekit

# Raw input data
problem_str = \"\"\"
{input_example}
\"\"\"

# Solve
res = puzzlekit.solve(problem_str, puzzle_type="{puzzle_key}")

# Print solution grid
print(res.solution_data.get('solution_grid', []))

# Visualize (optional)
res.show()
```
        """
        lines.append(code_block)
        lines.append("")
    # ==========================================

    # (Keep the original Output Example display)
    if output_example:
        lines.append("### Solution Output")
        lines.append("```text")
        lines.append(output_example)
        lines.append("```")
    
    return "\n".join(lines)

    # if input_example:
    #     lines.append("### Input String")
    #     lines.append("Copy this string to test the solver:")
    #     lines.append("```text")
    #     lines.append(input_example)
    #     lines.append("```")
    #     lines.append("")
    
    # if output_example:
    #     lines.append("### Output Solution")
    #     lines.append("```text")
    #     lines.append(output_example)
    #     lines.append("```")

# ==========================================
# Main flow
# ==========================================

def main():
    if not DOCS_OUTPUT_DIR.exists():
        DOCS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {DOCS_OUTPUT_DIR}")

    print(f"Scanning modules in: {SOLVERS_DIR}")
    
    count = 0
    # Iterate over all .py files in puzzles/solvers
    for py_file in sorted(SOLVERS_DIR.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
            
        module_name = py_file.stem
        
        # Dynamically load modules
        spec = importlib.util.spec_from_file_location(f"puzzlekit.solvers.{module_name}", py_file)
        if not spec or not spec.loader:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"puzzlekit.solvers.{module_name}"] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"⚠️  Error importing {module_name}: {e}")
            continue

        # Find classes inheriting from PuzzleSolver in the module
        solver_class = None
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, PuzzleSolver) and obj is not PuzzleSolver:
                # Exclude other Solver classes that may be imported, only take the classes defined in the current module
                if obj.__module__ == module.__name__:
                    solver_class = obj
                    break
        
        if solver_class:
            # Get metadata (here we will automatically get the default values of the base class, if the subclass doesn't write it)
            meta = getattr(solver_class, "metadata", {})
            
            # Generate Markdown
            md_content = generate_markdown_content(module_name, meta)
            
            output_file = DOCS_OUTPUT_DIR / f"{module_name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"✅ Generated: {output_file.name} ({meta.get('name', module_name)})")
            count += 1
        else:
            print(f"⏭️  Skipped {module_name}: No Solver class found.")

    print(f"\n🎉 Done! Generated {count} markdown files in {DOCS_OUTPUT_DIR}")

if __name__ == "__main__":
    main()