import json
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="DocPilot AI", page_icon="🤖", layout="wide")

MODEL = st.secrets.get("OPENAI_MODEL", "gpt-5.4-nano")
TOP_K = 4
MAX_ANSWER_CHARS = int(st.secrets.get("MAX_ANSWER_CHARS", 180))
TEACHING_BUG_MODE = str(st.secrets.get("TEACHING_BUG_MODE", "true")).strip().lower() in {"1", "true", "yes", "on"}
TARGET_TESTS = 15
TARGET_BUGS = 3
PASS_THRESHOLD = 70

# Reuse the original APP implementation currently stored in git history.
# This file is replaced by a compatibility loader so the navigation root can
# stay clean while the student-facing APP remains a dedicated page.
# The actual implementation is loaded from the preserved source module below.
from pathlib import Path
_saved = Path(__file__).with_name("agent_app_impl.py")
if not _saved.exists():
    st.error("Agent implementation file is missing.")
    st.stop()
exec(compile(_saved.read_text(encoding="utf-8"), str(_saved), "exec"), globals(), globals())
