import random
import time

import streamlit as st

from screenme.config import QUESTION_LIMIT
from screenme.state_manager import create_result_payload, ensure_candidate_session, normalize_username


def render_candidate_portal(state: dict, save_state, interview_ai) -> None:
    st.title("Candidate Portal")
    username_input = st.text_input("Enter Username")
    username = normalize_username(username_input)

    if not username_input:
        return

    if username not in state["assignments"]:
        st.warning("No interview assigned yet.")
        return

    if username in state["results"]:
        st.warning("You have already completed this interview.")
        return

    interview = ensure_candidate_session(state, username)
    config = state["assignments"][username]

    st.subheader(f"Role: {config['role']}")
    st.caption(f"Difficulty: {config['difficulty']}")

    if not interview["started"]:
        if st.button("Start Interview", use_container_width=True):
            with st.spinner(
                random.choice(
                    [
                        "Setting up interview...",
                        "Preparing questions...",
                        "Analyzing role...",
                        "Getting ready...",
                    ]
                )
            ):
                time.sleep(1)
                try:
                    interview["current_question"] = interview_ai.generate_question(
                        config["role"], config["difficulty"]
                    )
                except Exception as exc:
                    st.error(f"Unable to start the interview: {exc}")
                    return
            interview["started"] = True
            save_state(state)
            st.rerun()
        return

    st.markdown(f"**Q:** {interview['current_question']}")
    answer = st.text_area(
        "Your Answer",
        key=f"answer_{username}_{interview['question_count']}",
    )

    is_last = interview["question_count"] == QUESTION_LIMIT - 1
    button_label = "Submit Interview" if is_last else "Next Question"

    if st.button(button_label, key=f"submit_{username}_{interview['question_count']}", use_container_width=True):
        if not answer.strip():
            st.warning("Please answer before proceeding.")
            return

        interview["chat_history"].append(f"Q: {interview['current_question']}\nA: {answer.strip()}")

        if not is_last:
            with st.spinner(
                random.choice(
                    [
                        "Interesting...",
                        "Thinking...",
                        "Analyzing response...",
                        "Generating next question...",
                    ]
                )
            ):
                time.sleep(1)
                try:
                    interview["current_question"] = interview_ai.generate_followup(answer.strip())
                except Exception as exc:
                    st.error(f"Unable to generate the next question: {exc}")
                    return

            interview["question_count"] += 1
            save_state(state)
            st.rerun()

        with st.spinner("Evaluating your interview..."):
            try:
                evaluation = interview_ai.evaluate_candidate(
                    interview["chat_history"], config["role"]
                )
            except Exception as exc:
                st.error(f"Unable to evaluate the interview: {exc}")
                return

        interview["completed"] = True
        state["results"][username] = create_result_payload(interview, evaluation)
        state["active_interviews"].pop(username, None)
        save_state(state)
        st.success("Interview completed.")
