from pathlib import Path
import sys

# Ensure the repository root is importable when pytest is launched from CI.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
