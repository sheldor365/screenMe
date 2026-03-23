import streamlit as st
from openai import OpenAI
import random
import time

# ================== CONFIG ==================
client = OpenAI(api_key="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")
st.set_page_config(page_title="AI Interview Platform", layout="wide")

# ================== SESSION STATE ==================
if "configs" not in st.session_state:
    st.session_state.configs = []

if "assignments" not in st.session_state:
    st.session_state.assignments = {}

if "results" not in st.session_state:
    st.session_state.results = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "interview_completed" not in st.session_state:
    st.session_state.interview_completed = False

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# ================== HELPERS ==================

def generate_question(role, difficulty):
    prompt = f"""
    You are a senior interviewer.

    Role: {role}
    Difficulty: {difficulty}

    Ask ONLY ONE concise interview question.

    STRICT RULES:
    - Maximum 2 lines
    - No explanations
    - No bullet points
    - No sections like "Requirements"
    - Only ONE question

    Output only the question.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_followup(answer):
    prompt = f"""
    You are an interviewer.

    Candidate answer:
    {answer}

    Ask ONE follow-up question:
    - Be sharp and probing
    - Max 2 lines
    - No explanation
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def evaluate_candidate(chat_history, role):
    prompt = f"""
    Evaluate this candidate for role: {role}

    Conversation:
    {chat_history}

    Give STRICT structured output:

    Score: X/10
    Verdict: Hire / No Hire

    Strengths:
    - ...

    Weaknesses:
    - ...
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


# ================== SIDEBAR ==================
st.sidebar.title("Select Role")
portal = st.sidebar.selectbox("", ["Candidate", "Company"])

# ================== COMPANY PORTAL ==================
if portal == "Company":
    st.title("🏢 Company Dashboard")

    tab1, tab2, tab3 = st.tabs(["Create Role", "Assign Candidate", "View Results"])

    # -------- CREATE ROLE --------
    with tab1:
        st.subheader("Create Role")

        role = st.selectbox("Role", ["SDE", "QA", "SDET"])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Create Config"):
            st.session_state.configs.append({
                "role": role,
                "difficulty": difficulty
            })
            st.success("Config created!")

    # -------- ASSIGN --------
    with tab2:
        st.subheader("Assign Candidate")

        username = st.text_input("Candidate Username")

        if st.session_state.configs:
            config = st.selectbox("Select Role Config", st.session_state.configs)

            if st.button("Assign"):
                st.session_state.assignments[username] = config
                st.success(f"Assigned {username}")

    # -------- RESULTS --------
    with tab3:
        st.subheader("Candidate Results")

        for user, result in st.session_state.results.items():
            st.markdown(f"### 👤 {user}")

            st.markdown(result)

            st.markdown("### 💬 Transcript")
            for msg in st.session_state.chat_history:
                st.write(msg)

            col1, col2 = st.columns(2)

            with col1:
                st.button(f"Shortlist {user}", key=f"s_{user}")

            with col2:
                st.button(f"Reject {user}", key=f"r_{user}")

# ================== CANDIDATE PORTAL ==================
else:
    st.title("👨‍💻 Candidate Portal")

    username = st.text_input("Enter Username")

    if username:
        if username not in st.session_state.assignments:
            st.warning("No interview assigned yet.")
            st.stop()

        if username in st.session_state.results:
            st.warning("You have already completed this interview.")
            st.stop()

        config = st.session_state.assignments[username]

        st.subheader(f"Role: {config['role']}")  # ❌ no difficulty shown

        # -------- START --------
        if not st.session_state.interview_started:
            if st.button("Start Interview"):

                with st.spinner(random.choice([
                    "Setting up interview...",
                    "Preparing questions...",
                    "Analyzing role...",
                    "Getting ready..."
                ])):
                    time.sleep(1)
                    st.session_state.current_question = generate_question(
                        config["role"], config["difficulty"]
                    )

                st.session_state.interview_started = True

        # -------- CHAT --------
        if st.session_state.interview_started:

            st.markdown(f"**Q:** {st.session_state.current_question}")

            answer = st.text_area("Your Answer")

            is_last = st.session_state.question_count == 2
            btn_label = "Submit Interview" if is_last else "Next Question"

            if st.button(btn_label, key=f"btn_{st.session_state.question_count}"):

                if answer.strip():

                    st.session_state.chat_history.append(
                        f"Q: {st.session_state.current_question}\nA: {answer}"
                    )

                    if not is_last:
                        with st.spinner(random.choice([
                            "Interesting...",
                            "Thinking...",
                            "Analyzing response...",
                            "Generating next question..."
                        ])):
                            time.sleep(1)
                            st.session_state.current_question = generate_followup(answer)

                        st.session_state.question_count += 1
                        st.rerun()

                    else:
                        with st.spinner("Evaluating your interview..."):
                            result = evaluate_candidate(
                                st.session_state.chat_history,
                                config["role"]
                            )

                        st.session_state.results[username] = result
                        st.session_state.interview_completed = True
                        st.success("Interview Completed!")

                else:
                    st.warning("Please answer before proceeding.")