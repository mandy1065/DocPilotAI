from pathlib import Path

# Dedicated loader for the student-facing DocPilotAI APP page.
_saved = Path(__file__).with_name("agent_app_impl.py")
exec(compile(_saved.read_text(encoding="utf-8"), str(_saved), "exec"), globals(), globals())
