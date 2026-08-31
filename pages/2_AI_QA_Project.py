import os
from pathlib import Path

# Render the existing DocPilotAI application inside this named course page so
# the sidebar shows a clean course order: Learn RAG -> AI QA Project -> AI Evaluation.
os.environ["DOCPILOT_PROJECT_PAGE"] = "1"
root = Path(__file__).resolve().parent.parent
app_code = (root / "app.py").read_text(encoding="utf-8")
exec(compile(app_code, str(root / "app.py"), "exec"), globals(), globals())
