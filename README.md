# DocPilot AI

DocPilot AI is a Streamlit PDF question-answering agent used in an AI QA classroom lab.

Students can:
- enter their name,
- upload a PDF,
- ask as many document-grounded questions as needed,
- write test cases separately,
- submit bugs separately,
- receive Test Case, Bug Report, Overall percentage scores, and PASS/FAIL,
- download their work as CSV/JSON.

## Deploy on Streamlit Community Cloud

Main file: `app.py`

Add this secret in Streamlit app settings:

```toml
OPENAI_API_KEY = "your-real-api-key"
```

Optional model override:

```toml
OPENAI_MODEL = "gpt-5.4-mini"
```

The real API key must never be committed to GitHub.
