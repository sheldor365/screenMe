import streamlit as st

from screenme.config import APP_TITLE
from screenme.openai_service import InterviewAI
from screenme.storage import load_state, save_state
from screenme.ui.candidate import render_candidate_portal
from screenme.ui.company import render_company_dashboard


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.sidebar.title("Select Role")
    portal = st.sidebar.selectbox("", ["Candidate", "Company"])

    state = load_state()

    try:
        interview_ai = InterviewAI()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if portal == "Company":
        render_company_dashboard(state, save_state)
    else:
        render_candidate_portal(state, save_state, interview_ai)
