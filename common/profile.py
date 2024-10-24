


from common.config import Config as config
from common.chat import load_data, save_data


def get_profiles():
    profiles = load_data(config.PROFILES_FILE)
    if profiles is None:
        profiles = []

    return profiles