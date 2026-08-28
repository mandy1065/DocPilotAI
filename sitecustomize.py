"""Compatibility shim for Streamlit chat avatars.

Recent Streamlit versions validate custom chat avatars more strictly. The app
uses the decorative character "✦" as an assistant avatar, which is not accepted
as an image/emoji avatar by newer Streamlit releases. This shim converts that
legacy avatar to a supported emoji without changing the rest of the app.
"""

try:
    import streamlit as st

    _original_chat_message = st.chat_message

    def _safe_chat_message(name, *, avatar=None, width="stretch"):
        if avatar == "✦":
            avatar = "🤖"
        return _original_chat_message(name, avatar=avatar, width=width)

    st.chat_message = _safe_chat_message
except Exception:
    # Never block app startup if Streamlit changes its API again.
    pass
