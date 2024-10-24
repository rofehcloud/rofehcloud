# config.py

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv(".env")


class Config:
    ENV_NAME = str(os.environ.get("ENV_NAME")).lower()
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    SIMILARITY_TOP_K = int(os.environ.get("SIMILARITY_TOP_K", 15))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    PROFILE_DIR = os.path.expanduser(os.environ.get("PROFILE_DIR", "~/.rofehcloud"))
    SESSION_DIR = f"{PROFILE_DIR}/sessions"
    PROFILES_FILE = f"{PROFILE_DIR}/profiles.yaml"


    OPENAI_LANGCHAIN_AGENT_MODEL_ID = os.environ.get(
        "OPENAI_LANGCHAIN_AGENT_MODEL_ID",
        # "gpt-4o-mini-2024-07-18"
        # "gpt-4-turbo-2024-04-09"
        "gpt-4o-mini"
        # "gpt-4-1106-preview",
        # "gpt-4o-2024-05-13"
    )
    LANGCHAIN_AGENT_MODEL_TEMPERATURE = float(
        os.environ.get("LANGCHAIN_AGENT_MODEL_TEMPERATURE", 0.3)
    )
    # Bedrock models for different functions

    BEDROCK_LANGCHAIN_AGENT_MODEL_ID = os.environ.get(
        "BEDROCK_LANGCHAIN_AGENT_MODEL_ID",
        # "anthropic.claude-3-haiku-20240307-v1:0"
        "anthropic.claude-3-sonnet-20240229-v1:0",
        # "anthropic.claude-3-opus-20240229-v1:0",
    )

    AGENT_MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERATIONS", 20))


def load_config():
    # Load environment variables from .env file
    load_dotenv(override=False)

    global config
    config = Config()

    # Check that all required variables are set; list missing environment variables before raising an exception
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    return config


# Load and validate the configuration when the module is imported
load_config()
