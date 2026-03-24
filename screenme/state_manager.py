from copy import deepcopy


def normalize_username(username: str) -> str:
    return username.strip().lower()


def build_interview_session(config: dict) -> dict:
    return {
        "role": config["role"],
        "difficulty": config["difficulty"],
        "started": False,
        "completed": False,
        "question_count": 0,
        "current_question": None,
        "chat_history": [],
    }


def ensure_candidate_session(state: dict, username: str) -> dict:
    config = state["assignments"][username]
    interview = state["active_interviews"].get(username)
    if interview is None:
        interview = build_interview_session(config)
        state["active_interviews"][username] = interview
        return interview

    if (
        interview.get("role") != config["role"]
        or interview.get("difficulty") != config["difficulty"]
    ) and not interview.get("started"):
        interview = build_interview_session(config)
        state["active_interviews"][username] = interview
    return interview


def create_result_payload(interview: dict, evaluation: str) -> dict:
    return {
        "role": interview["role"],
        "difficulty": interview["difficulty"],
        "evaluation": evaluation,
        "transcript": deepcopy(interview["chat_history"]),
        "decision": "Pending",
    }
