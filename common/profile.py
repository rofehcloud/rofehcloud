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
    for tool in config.ALL_TOOLS:
        # check that the tool is available in the path and executable
        if not shutil.which(tool):
            print(
                Style.BRIGHT + f'Warning: tool "{tool}" not found in the PATH. '
                "We highly recommend to install the tool and restart the app."
            )
            config.ALL_TOOLS.remove(tool)

