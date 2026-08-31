import streamlit as st

# Fixed three-step course navigation.
# Using st.navigation disables Streamlit's automatic pages/ discovery, so the
# sidebar no longer changes order or shows duplicate/legacy entries.
open_project = bool(st.session_state.get("open_ai_qa_project", False))

learn_page = st.Page(
    "pages/1_Learn_RAG.py",
    title="Learn RAG",
    icon="🧠",
    default=not open_project,
)
app_page = st.Page(
    "pages/2_APP.py",
    title="APP",
    icon="🤖",
    default=open_project,
)
evaluation_page = st.Page(
    "pages/3_AI_Evaluation.py",
    title="AI Evaluation",
    icon="🎓",
)

navigation = st.navigation([learn_page, app_page, evaluation_page])
navigation.run()
