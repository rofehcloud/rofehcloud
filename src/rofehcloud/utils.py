import os

from rofehcloud.logger import log_message
from rofehcloud.config import Config as config
from rofehcloud.chat import save_data


def generate_collection_name(profile: str) -> str:
    collection_name = f"c_{profile}"
    return collection_name


def fix_unclosed_quote(line):
    # Count the number of double quotes in the line
    quote_count = line.count('"')
    # If the count is odd, add a closing quote
    if quote_count % 2 != 0:
        line += '"'
        log_message("DEBUG", f"Added a closing quote to the line: {line}")
    line = line.strip("`")
    return line


def initialize_environment():
    log_message("DEBUG", "Initializing the environment...")
    # Initialize the environment here
    try:
        # check that directory exists
        if not os.path.exists(config.APP_DATA_DIR):
            log_message(
                "INFO", f"Creating RofehCloud app data directory {config.APP_DATA_DIR}"
            )
            os.makedirs(config.APP_DATA_DIR)

        if not os.path.exists(config.SESSION_DIR):
            log_message("INFO", f"Creating the directory {config.SESSION_DIR}")
            os.makedirs(config.SESSION_DIR)

        if not os.path.exists(config.PROFILES_DIR):
            log_message("INFO", f"Creating the directory {config.PROFILES_DIR}")
            os.makedirs(config.PROFILES_DIR)

        default_profile = f"{config.PROFILES_DIR}/default.yaml"

        if not os.path.exists(default_profile):
            profile = {"name": "default", "description": "Default profile"}
            result = save_data(default_profile, profile)
            if not result:
                log_message("ERROR", "Failed to save the default profile")
                return False

        return True

    except Exception as e:
        log_message("ERROR", f"Error while initializing the environment: {e}")
        return False
