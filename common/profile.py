import shutil
from colorama import init, Style

from common.config import Config as config
from common.chat import load_data
from common.logger import log_message

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
