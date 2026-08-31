from pathlib import Path

# Reuse the existing DocPilotAI agent implementation without duplicating its code.
# The root app.py is now only the course navigation router.
root = Path(__file__).resolve().parent.parent
agent_code = (root / "agent_app.py").read_text(encoding="utf-8")
exec(compile(agent_code, str(root / "agent_app.py"), "exec"), globals(), globals())
