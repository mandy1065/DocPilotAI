from pathlib import Path
import re
import streamlit as st

st.set_page_config(page_title="DocPilot AI QA Course", page_icon="🧠", layout="wide")

# Hide Streamlit's automatic multipage navigation. We use one stable custom
# course menu instead so students always see exactly three choices.
st.markdown(
    """
    <style>
    div[data-testid="stSidebarNav"] {display:none !important;}
    section[data-testid="stSidebar"] > div {padding-top:1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

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
    """Execute an existing Streamlit lesson/app inside this single entry point."""
    source = path.read_text(encoding="utf-8")

    # set_page_config may only be called once and must stay in this root app.
    source = re.sub(
        r'^st\.set_page_config\([^\n]*\)\s*\n',
        '',
        source,
        flags=re.MULTILINE,
    )

    if strip_project_redirects:
        # Remove old course-routing code that referenced the previous pages/
        # navigation design. The custom radio above now owns navigation.
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
        # Defensive removal for any remaining direct page switches.
        source = re.sub(r'^.*st\.switch_page\([^\n]*\).*\n?', '', source, flags=re.MULTILINE)

    exec(compile(source, str(path), "exec"), globals(), globals())


if choice == "Learn RAG":
    run_streamlit_content(ROOT / "pages" / "1_Learn_RAG.py")
elif choice == "APP":
    run_streamlit_content(ROOT / "agent_app_impl.py", strip_project_redirects=True)
else:
    run_streamlit_content(ROOT / "pages" / "AI_Evaluation.py")
