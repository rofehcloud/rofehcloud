import os
import yaml

from rofehcloud.llm import call_llm
from rofehcloud.logger import log_message
from rofehcloud.config import Config as config


def get_conversation_label(profile, user_input):
    convo_label = call_llm(
        f"For the provided below user prompt, suggest a short (20-30 characters) description "
        "of the conversation. Do not add any comments - just reply with the "
        f"description string.\n\n{user_input}",
        config.LLM_TO_USE,
    )

    if convo_label is None or convo_label == "":
        convo_label = "Unknown"
    convo_label = convo_label.strip("\"`'")
    log_message("DEBUG", f"Conversation label: {convo_label}")
    return convo_label


def get_conversations_list(profile):
    try:
        session_files = os.listdir(config.SESSION_DIR)
        conversations_list = []

        for session_file in session_files:
            session = load_data(f"{config.SESSION_DIR}/{session_file}")
            if session and session["profile"] == profile:
                conversation = {
                    "session_id": session["session_id"],
                    "label": session["conversation_label"],
                    "date": session["date"],
                }
                conversations_list.append(conversation)

        # sort conversations by date
        conversations_list = sorted(
            conversations_list, key=lambda x: x["date"], reverse=True
        )

        # log_message("INFO", f"Conversations list: {conversations_list}")
        return conversations_list

    except Exception as e:
        log_message("ERROR", f"Error while getting conversations list: {e}")
        return None


def load_data(filename):
    log_message("DEBUG", f"Loading data from {filename}")
    try:
        with open(filename, "r") as file:
            return yaml.safe_load(file)
        return True

    except Exception as e:
        log_message("ERROR", f"Error while loading data from {filename}: {e}")
        return None


def save_data(filename, data, plain=False):
    log_message("DEBUG", f"Saving data to {filename}")
    try:
        with open(filename, "w") as file:
            if plain:
                file.write(data)
            else:
                yaml.safe_dump(data, file, sort_keys=False)
        return True

    except Exception as e:
        log_message("ERROR", f"Error while saving data to {filename}: {e}")
        return False
