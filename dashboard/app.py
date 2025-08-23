# dashboard/app.py

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Make sure we can import audit_service
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from audit_service.core import run_audit_input, run_audit_output
from audit_service.services.gemini_adapter import GeminiAdapter


# Initialize Gemini adapter
gemini = GeminiAdapter()

st.set_page_config(page_title="AI Auditor Dashboard", layout="wide")

st.title("🛡️ AI Auditor Dashboard")

tabs = st.tabs(["👤 User Prompt Audit", "🤖 AI Output Audit"])


# ===============================
# TAB 1: USER PROMPT
# ===============================
with tabs[0]:
    st.header("Audit User Prompt")

    user_prompt = st.text_area("Enter user prompt:", height=150)

    if st.button("Run User Prompt Audit", key="audit_input"):
        if not user_prompt.strip():
            st.warning("Please enter a user prompt first.")
        else:
            with st.spinner("Running input audit..."):
                results = run_audit_input(user_prompt)

            st.subheader("📋 Audit Results")
            st.json(results)


# ===============================
# TAB 2: AI OUTPUT
# ===============================
with tabs[1]:
    st.header("Audit AI Output")

    ai_output = st.text_area("Enter AI output:", height=150)

    if st.button("Run AI Output Audit", key="audit_output"):
        if not ai_output.strip():
            st.warning("Please enter AI output first.")
        else:
            with st.spinner("Running output audit..."):
                results = run_audit_output(ai_output)

            st.subheader("📋 Audit Results")
            st.json(results)

            # If flagged, rewrite with Gemini
            flagged_issues = [flag for flag, val in results["flags"].items() if val > 0]
            if flagged_issues:
                with st.spinner("Rewriting with Gemini..."):
                    rewritten = gemini.sanitize(ai_output, results["flags"], results)

                st.subheader("📝 Rewrite (Gemini)")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Before**")
                    st.code(ai_output, language="markdown")

                with col2:
                    st.markdown("**After**")
                    st.code(rewritten, language="markdown")
