import subprocess
import sys
from pathlib import Path


def build_docs():
    """Build the Sphinx HTML documentation."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    result = subprocess.run(["make", "-C", str(docs_dir), "html"])
    sys.exit(result.returncode)

