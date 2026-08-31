import json
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI

# Compatibility wrapper: execute the original AI Evaluation implementation.
from pathlib import Path
source = Path(__file__).parent / "pages" / "AI_Evaluation.py"
exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), globals(), globals())
