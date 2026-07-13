"""
build_paper.py — copies the static paper.html into docs/.
Called by the weekly GitHub Actions pipeline.
In a future version this could regenerate the paper dynamically from data outputs.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / "docs" / "paper.html"

if src.exists():
    print(f"paper.html already present ({src.stat().st_size:,} bytes) — nothing to do.")
else:
    print("WARNING: docs/paper.html not found. Run scripts/_write_docs.py to generate it.")
