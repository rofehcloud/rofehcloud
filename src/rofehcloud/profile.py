import shutil
import os
from colorama import init, Style
import yaml
from cerberus import Validator

from rofehcloud.config import Config as config
from rofehcloud.chat import load_data
from rofehcloud.logger import log_message

init(autoreset=True)


def get_profiles():
    profiles = load_data(config.PROFILES_FILE)
    if profiles is None:
        profiles = []

    return profiles


def check_available_tools(profile):
    if config.SKIP_THE_CHECK_FOR_AVAILABLE_TOOLS:
        log_message(
            "INFO",
            "Skipping the check for available tools (SKIP_THE_CHECK_FOR_AVAILABLE_TOOLS is set to true)",
        )
        return
    copy_of_all_tools = config.ALL_TOOLS.copy()
    for tool in copy_of_all_tools:
        # check that the tool is available in the path and executable
        log_message("DEBUG", f"Checking if tool {tool} is available in the PATH")
        if not shutil.which(tool):
            log_message("DEBUG", f"Tool {tool} not found in the PATH")
            print(
                Style.BRIGHT + f'Warning: tool "{tool}" not found in the PATH. '
                "We highly recommend to install the tool and restart the app."
            )
            config.ALL_TOOLS.remove(tool)


def read_profile(profile: str) -> dict:
    profile_file = f"{config.PROFILES_DIR}/{profile}.yaml"
    log_message("DEBUG", f"Reading profile from {profile_file}")
    if not os.path.exists(profile_file):
        log_message("ERROR", f"Profile file {profile_file} not found")
        return None

    profile_data = load_data(profile_file)
    if profile_data is None:
        log_message("ERROR", f"Error while reading profile {profile}")
        return None

    if validate_profile(profile_data):
        return profile_data
    else:
        return None


def save_profile(profile: str, profile_data: dict) -> bool:
    profile_file = f"{config.PROFILES_DIR}/{profile}.yaml"
    log_message("INFO", f"Saving profile to {profile_file}")
    if not os.path.exists(config.PROFILES_DIR):
        log_message("INFO", f"Creating directory {config.PROFILES_DIR}")
        os.makedirs(config.PROFILES_DIR)

    if not validate_profile(profile_data):
        return False

    if not os.path.exists(profile_file):
        log_message("INFO", f"Creating profile file {profile_file}")
    else:
        log_message("INFO", f"Overwriting profile file {profile_file}")

    with open(profile_file, "w") as f:
        yaml.dump(profile_data, f)

    return True


def validate_profile(profile_data: str) -> bool:
    schema = {
        "name": {"type": "string", "required": True},
        "description": {"type": "string", "required": True},
        "aws_regions_with_resources": {
            "type": "list",
            "required": False,
            "schema": {"type": "string"},
        },
        "source_code_repositories": {
            "type": "list",
            "required": False,
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "type": {
                        "type": "string",
                        "required": True,
                        "allowed": ["github", "gitlab", "bitbucket"],
                    },
                    "local_directory": {"type": "string", "required": True},
                    "description": {"type": "string", "required": True},
                },
            },
        },
    }

    # Initialize the validator with the schema
    validator = Validator(schema)

    try:
        # Validate data against the schema
        if validator.validate(profile_data):
            log_message("DEBUG", "Profile's YAML content is valid.")
            return True
        else:
            print("YAML content is invalid.")
            print("Errors:", validator.errors)
            return False
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return False
