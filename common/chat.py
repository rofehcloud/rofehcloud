import yaml

from common.llm import call_openai
from common.logger import log_message


def get_conversation_label(profile, user_input):
    convo_label = call_openai(
        f"For the provided below user prompt, suggest a short (20-30 characters) description "
        "of the conversation. Do not add any comments - just reply with the "
        f"description string.\n\n{user_input}"
    )

    if convo_label is None or convo_label == "":
        convo_label = "Unknown"
    convo_label = convo_label.strip("\"`'")
    log_message("INFO", f"Conversation label: {convo_label}")
    return convo_label


def load_data(filename):
    try:
        with open(filename, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        log_message("ERROR", f"Error while loading data from {filename}: {e}")
        return None


def save_data(filename, data):
    try:
        with open(filename, "w") as file:
            yaml.safe_dump(data, file, sort_keys=False)

    except Exception as e:
        log_message("ERROR", f"Error while saving data to {filename}: {e}")
        return False
