"""
Generate and inject MkDocs navigation configuration for puzzle documentation.
Automatically replaces content between BEGIN/END markers in mkdocs.yml.

# Preview the nav configuration without modifying mkdocs.yml
python scripts/gen_mkdocs_nav.py --preview

# Print the nav configuration to stdout
python scripts/gen_mkdocs_nav.py --stdout

# Inject the nav configuration into mkdocs.yml (need to confirm)
python scripts/gen_mkdocs_nav.py
"""

import sys
from pathlib import Path
import argparse
import re
from typing import List

# ==========================================
# Configuration
# ==========================================
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_PUZZLES_DIR = PROJECT_ROOT / "docs" / "puzzles"
MKDOCS_YML = PROJECT_ROOT / "mkdocs.yml"

# Navigation markers
BEGIN_MARKER = "# ==== BEGIN NAV CONFIGURATION ===="
END_MARKER = "# ==== END NAV CONFIGURATION ===="

# ==========================================
# Helper Functions
# ==========================================

def scan_puzzle_docs(docs_dir: Path) -> List[str]:
    """Scan all .md files in puzzles directory and return sorted list of filenames (without extension)."""
    if not docs_dir.exists():
        print(f"⚠️  Warning: Directory not found: {docs_dir}", file=sys.stderr)
        return []
    
    md_files = [f.stem for f in docs_dir.glob("*.md") if f.is_file()]
    return sorted(md_files, key=str.lower)

def format_puzzle_name(filename: str) -> str:
    """Convert filename to human-readable puzzle name."""
    # Replace underscores with spaces and capitalize appropriately
    name = filename.replace("_", " ").title()
    return name

def generate_nav_yaml(puzzle_names: List[str]) -> str:
    """Generate MkDocs nav configuration as YAML string."""
    lines = []
    lines.append("nav:")
    lines.append("  - Intro:")
    lines.append("      - Intro: index.md")
    lines.append("  - Puzzles:")
    
    for name in puzzle_names:
        display_name = name
        lines.append(f"      - {display_name}: puzzles/{name}.md")
    
    return "\n".join(lines)

def inject_nav_to_mkdocs(mkdocs_file: Path, nav_content: str) -> bool:
    """
    Inject nav configuration into mkdocs.yml between BEGIN/END markers.
    Returns True if successful, False otherwise.
    """
    if not mkdocs_file.exists():
        print(f"❌ Error: mkdocs.yml not found at {mkdocs_file}", file=sys.stderr)
        return False
    
    try:
        # Read the entire file
        with open(mkdocs_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if markers exist
        if BEGIN_MARKER not in content or END_MARKER not in content:
            print(f"❌ Error: Navigation markers not found in {mkdocs_file}", file=sys.stderr)
            print(f"   Please ensure the following markers exist in mkdocs.yml:")
            print(f"   {BEGIN_MARKER}")
            print(f"   ... your nav content ...")
            print(f"   {END_MARKER}")
            return False
        
        # Build replacement pattern
        # Use re.DOTALL to match across multiple lines
        pattern = re.compile(
            f"({re.escape(BEGIN_MARKER)}\n).*?(\n{re.escape(END_MARKER)})",
            re.DOTALL
        )
        
        # Replacement content (with markers preserved)
        replacement = f"\\1{nav_content}\n\\2"
        
        # Perform replacement
        new_content = pattern.sub(replacement, content)
        
        # Write back to file
        with open(mkdocs_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating {mkdocs_file}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

def preview_nav(puzzle_names: List[str], max_show: int = 10):
    """Preview the nav configuration to be injected."""
    nav_yaml = generate_nav_yaml(puzzle_names)
    
    print("\n" + "="*60)
    print("PREVIEW: MkDocs Navigation Configuration")
    print("="*60)
    print()
    
    lines = nav_yaml.split('\n')
    for i, line in enumerate(lines):
        if i < max_show or i >= len(lines) - 3:
            print(f"  {line}")
        elif i == max_show:
            print(f"  ... ({len(lines) - max_show - 3} more lines)")
    
    print()
    print("="*60)
    print(f"Total puzzles: {len(puzzle_names)}")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description="Generate and inject MkDocs navigation configuration for puzzles"
    )
    parser.add_argument(
        "--mkdocs", "-m",
        type=Path,
        default=MKDOCS_YML,
        help=f"Path to mkdocs.yml file (default: {MKDOCS_YML})"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=DOCS_PUZZLES_DIR,
        help=f"Puzzles documentation directory (default: {DOCS_PUZZLES_DIR})"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the nav configuration without modifying mkdocs.yml"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the nav configuration to stdout"
    )
    
    args = parser.parse_args()
    
    # Scan puzzle documentation files
    puzzle_files = scan_puzzle_docs(args.docs_dir)
    
    if not puzzle_files:
        print(f"❌ Error: No puzzle documentation files found in {args.docs_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Found {len(puzzle_files)} puzzle documentation files")
    
    # Generate nav configuration
    nav_yaml = generate_nav_yaml(puzzle_files)
    
    # Handle different output modes
    if args.stdout:
        print(nav_yaml)
        return
    
    if args.preview:
        preview_nav(puzzle_files)
        print("\n💡 Run without --preview to inject into mkdocs.yml")
        return
    
    # Inject into mkdocs.yml
    print(f"\n📝 Injecting navigation into: {args.mkdocs}")
    preview_nav(puzzle_files, max_show=5)
    
    confirm = input("\nType 'YES' to confirm injection: ").strip()
    if confirm != "YES":
        print("❌ Injection aborted by user.")
        sys.exit(1)
    
    success = inject_nav_to_mkdocs(args.mkdocs, nav_yaml)
    
    if success:
        print(f"\n✅ Successfully injected navigation into {args.mkdocs}")
        print(f"   Total puzzles: {len(puzzle_files)}")
    else:
        print(f"\n❌ Failed to inject navigation into {args.mkdocs}")
        sys.exit(1)

if __name__ == "__main__":
    main()