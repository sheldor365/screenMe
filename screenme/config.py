import os
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


APP_TITLE = "AI Interview Platform"
STATE_FILE = "data/app_state.json"
QUESTION_LIMIT = 3
MODEL_NAME = "gpt-4o-mini"
AVAILABLE_ROLES = ["SDE", "QA", "SDET"]
AVAILABLE_DIFFICULTIES = ["Easy", "Medium", "Hard"]


def get_env_file_key() -> str | None:
    env_paths = [Path(".env"), Path(__file__).resolve().parent / ".env"]

    for env_path in env_paths:
        if not env_path.exists():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key.strip() != "OPENAI_API_KEY":
                continue

            cleaned = value.strip().strip("'").strip('"')
            if cleaned:
                return cleaned

    return None


def get_api_key() -> str:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except StreamlitSecretNotFoundError:
        api_key = None

    api_key = api_key or os.getenv("OPENAI_API_KEY") or get_env_file_key()
    if not api_key:
        raise RuntimeError(
            "Missing OpenAI API key. Set OPENAI_API_KEY in Streamlit secrets, the environment, or a local .env file."
        )
    return api_key
