import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv(".env")


class Config:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    PROFILE_DIR = os.path.expanduser(os.environ.get("PROFILE_DIR", "~/.rofehcloud"))
    SESSION_DIR = f"{PROFILE_DIR}/sessions"
    PROFILES_FILE = f"{PROFILE_DIR}/profiles.yaml"

    OPENAI_LANGCHAIN_AGENT_MODEL_ID = os.environ.get(
        "OPENAI_LANGCHAIN_AGENT_MODEL_ID",
        # "gpt-4-turbo-2024-04-09"
        "gpt-4o"
        # "gpt-4o-mini"
        # "gpt-4-1106-preview",
    )
    OPENAI_GENERAL_MODEL_ID = os.environ.get(
        "OPENAI_GENERAL_MODEL_ID",
        # "gpt-4o"
        "gpt-4o-mini"
    )

    LANGCHAIN_AGENT_MODEL_TEMPERATURE = float(
        os.environ.get("LANGCHAIN_AGENT_MODEL_TEMPERATURE", 0.3)
    )

    BEDROCK_LANGCHAIN_AGENT_MODEL_ID = os.environ.get(
        "BEDROCK_LANGCHAIN_AGENT_MODEL_ID",
        # "anthropic.claude-3-haiku-20240307-v1:0"
        # "anthropic.claude-3-sonnet-20240229-v1:0",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        # "anthropic.claude-3-opus-20240229-v1:0",
    )

    BEDROCK_GENERAL_MODEL_ID = os.environ.get(
        "BEDROCK_GENERAL_MODEL_ID",
        "anthropic.claude-3-haiku-20240307-v1:0"
        # "anthropic.claude-3-sonnet-20240229-v1:0",
        # "anthropic.claude-3-opus-20240229-v1:0",
    )

    BEDROCK_PROFILE_NAME = os.environ.get("BEDROCK_PROFILE_NAME", "default")
    BEDROCK_AWS_REGION = os.environ.get("BEDROCK_AWS_REGION", "us-east-1")

    AGENT_MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERATIONS", 30))
    COMMAND_OUTPUT_MAX_LENGTH_CHARS = int(
        os.environ.get("COMMAND_OUTPUT_MAX_LENGTH_CHARS", 10000)
    )

    LLM_TO_USE = os.environ.get("LLM_TO_USE", "openai")

    ALLOW_POTENTIALLY_RISKY_LLM_COMMANDS = os.environ.get(
        "ALLOW_POTENTIALLY_RISKY_LLM_COMMANDS", "ask"
    ).lower()

    STANDARD_TOOLS = os.environ.get(
        "STANDARD_TOOLS",
        (
            "sed,awk,ping,wget,curl,dig,traceroute,helm,"
            "jq,yq,cut,bc,head,tail,sort,uniq,wc,grep,egrep"
        ),
    ).split(",")

    CLOUD_CLI_TOOLS = os.environ.get(
        "CLOUD_CLI_TOOLS",
        ("aws,gcloud,az,kubectl"),
    ).split(",")

    ADDITIONAL_TOOLS = os.environ.get("ADDITIONAL_TOOLS", "").split(",")

    ALL_TOOLS = STANDARD_TOOLS + CLOUD_CLI_TOOLS + ADDITIONAL_TOOLS
    if "" in ALL_TOOLS:
        ALL_TOOLS.remove("")

    SKIP_LLM_FUNCTIONALITY_VERIFICATION = os.environ.get(
        "SKIP_LLM_FUNCTIONALITY_VERIFICATION", "false") == "true"
    

def load_config():
    # Load environment variables from .env file
    load_dotenv(override=False)

    global config
    config = Config()

    required_vars = []
    # Check that all required variables are set; list missing environment variables before raising an exception
    if config.LLM_TO_USE == "openai":
        required_vars = [
            "OPENAI_API_KEY",
        ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    return config


# Load and validate the configuration when the module is imported
load_config()
