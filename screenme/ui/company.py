import streamlit as st

from screenme.config import AVAILABLE_DIFFICULTIES, AVAILABLE_ROLES
from screenme.state_manager import build_interview_session, normalize_username


def render_company_dashboard(state: dict, save_state) -> None:
    st.title("Company Dashboard")
    tab1, tab2, tab3 = st.tabs(["Create Role", "Assign Candidate", "View Results"])

    with tab1:
        render_create_role(state, save_state)

    with tab2:
        render_assign_candidate(state, save_state)

    with tab3:
        render_results(state, save_state)


def render_create_role(state: dict, save_state) -> None:
    st.subheader("Create Role")
    role = st.selectbox("Role", AVAILABLE_ROLES)
    difficulty = st.selectbox("Difficulty", AVAILABLE_DIFFICULTIES)

    if st.button("Create Config", use_container_width=True):
        config = {"role": role, "difficulty": difficulty}
        if config not in state["configs"]:
            state["configs"].append(config)
            save_state(state)
            st.success("Config created.")
        else:
            st.info("That config already exists.")


def render_assign_candidate(state: dict, save_state) -> None:
    st.subheader("Assign Candidate")
    username_input = st.text_input("Candidate Username")

    if not state["configs"]:
        st.info("Create a role config before assigning candidates.")
        return

    config_options = {
        f"{config['role']} / {config['difficulty']}": config for config in state["configs"]
    }
    selected_label = st.selectbox("Select Role Config", list(config_options.keys()))
    selected_config = config_options[selected_label]

    if st.button("Assign", use_container_width=True):
        username = normalize_username(username_input)
        if not username:
            st.warning("Enter a candidate username.")
            return

        state["assignments"][username] = selected_config
        existing_result = state["results"].get(username)
        if existing_result is None:
            state["active_interviews"][username] = build_interview_session(selected_config)
        save_state(state)
        st.success(f"Assigned {username}.")


def render_results(state: dict, save_state) -> None:
    st.subheader("Candidate Results")

    if not state["results"]:
        st.info("No completed interviews yet.")
        return

    for username, result in state["results"].items():
        st.markdown(f"### {username}")
        st.caption(f"Role: {result['role']} | Difficulty: {result['difficulty']}")
        st.markdown(result["evaluation"])

        st.markdown("### Transcript")
        for entry in result["transcript"]:
            st.write(entry)

        decision = result.get("decision", "Pending")
        st.write(f"Decision: {decision}")

        col1, col2 = st.columns(2)
        if col1.button("Shortlist", key=f"shortlist_{username}", use_container_width=True):
            state["results"][username]["decision"] = "Shortlisted"
            save_state(state)
            st.rerun()
        if col2.button("Reject", key=f"reject_{username}", use_container_width=True):
            state["results"][username]["decision"] = "Rejected"
            save_state(state)
            st.rerun()
