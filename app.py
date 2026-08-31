from pathlib import Path
import re
import streamlit as st

st.set_page_config(page_title="DocPilot AI QA Course", page_icon="🧠", layout="wide")

# One stable entry point with exactly three course sections.
if "course_page" not in st.session_state:
    st.session_state.course_page = "Learn RAG"

with st.sidebar:
    st.markdown("### AI QA Course")
    choice = st.radio(
        "Course navigation",
        ["Learn RAG", "APP", "AI Evaluation"],
        index=["Learn RAG", "APP", "AI Evaluation"].index(st.session_state.course_page),
        label_visibility="collapsed",
    )
    st.session_state.course_page = choice

ROOT = Path(__file__).resolve().parent


def run_streamlit_content(path: Path, *, strip_project_redirects: bool = False):
    source = path.read_text(encoding="utf-8")

    # Child modules must not call set_page_config because the root app already did.
    source = re.sub(
        r'^st\.set_page_config\([^\n]*\)\s*\n',
        '',
        source,
        flags=re.MULTILINE,
    )

    if strip_project_redirects:
        # Remove legacy routing from the preserved APP implementation.
        source = re.sub(
            r'# --- COURSE LANDING ROUTE ---.*?(?=MODEL\s*=)',
            '',
            source,
            flags=re.DOTALL,
        )
        source = re.sub(
            r'# The root app stays hidden.*?(?=MODEL\s*=)',
            '',
            source,
            flags=re.DOTALL,
        )
        source = re.sub(r'^.*st\.switch_page\([^\n]*\).*\n?', '', source, flags=re.MULTILINE)

    # Learn RAG used to switch directly to app.py. In this single-page course,
    # the sidebar owns navigation, so remove any stale switch_page calls.
    source = re.sub(r'^.*st\.switch_page\([^\n]*\).*\n?', '', source, flags=re.MULTILINE)

    exec(compile(source, str(path), "exec"), globals(), globals())


if choice == "Learn RAG":
    run_streamlit_content(ROOT / "learn_rag.py")
elif choice == "APP":
    run_streamlit_content(ROOT / "agent_app_impl.py", strip_project_redirects=True)
else:
    run_streamlit_content(ROOT / "ai_evaluation.py")
