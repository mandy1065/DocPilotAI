from pathlib import Path

root = Path(__file__).resolve().parent.parent
page_code = (root / "ai_evaluation_impl.py").read_text(encoding="utf-8")
exec(compile(page_code, str(root / "ai_evaluation_impl.py"), "exec"), globals(), globals())
