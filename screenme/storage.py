import json
from copy import deepcopy
from pathlib import Path

from screenme.config import STATE_FILE


DEFAULT_STATE = {
    "configs": [],
    "assignments": {},
    "results": {},
    "active_interviews": {},
}


def load_state() -> dict:
    path = Path(STATE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        save_state(deepcopy(DEFAULT_STATE))
        return deepcopy(DEFAULT_STATE)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    merged = deepcopy(DEFAULT_STATE)
    for key, value in data.items():
        if key in merged:
            merged[key] = value
    return merged


def save_state(state: dict) -> None:
    path = Path(STATE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)
