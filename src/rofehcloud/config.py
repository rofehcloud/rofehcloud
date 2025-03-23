import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv(".env")


class Config:
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    APP_DATA_DIR = os.path.expanduser(os.environ.get("APP_DATA_DIR", "~/.rofehcloud"))
    SESSION_DIR = f"{APP_DATA_DIR}/sessions"
    PROFILES_DIR = f"{APP_DATA_DIR}/profiles"

    # OpenAI-related settings
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    OPENAI_LANGCHAIN_AGENT_MODEL_ID = os.environ.get(
        "OPENAI_LANGCHAIN_AGENT_MODEL_ID",
        "gpt-4-turbo",
        # "gpt-4o"
        # "gpt-4o-mini"
        # "gpt-4-1106-preview",
    )
    OPENAI_GENERAL_MODEL_ID = os.environ.get(
        "OPENAI_GENERAL_MODEL_ID",
        # "gpt-4o"
        "gpt-4o-mini",
    )
    OPENAI_TEMPERATURE = float(os.environ.get("OPENAI_TEMPERATURE", 0.3))
    OPENAI_MAX_RESPONSE_TOKENS = int(os.environ.get("OPENAI_MAX_RESPONSE_TOKENS", 4096))

    # Azure OpenAI-related settings
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_ID = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID")

    AZURE_OPENAI_API_VERSION = os.environ.get(
        "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"
    )

    AZURE_OPENAI_MODEL_ID = os.environ.get(
        "AZURE_OPENAI_MODEL_ID",
        # "gpt-4-turbo-2024-04-09"
        "gpt-4o-mini",
        # "gpt-4o-mini"
        # "gpt-4-1106-preview",
    )

    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_TEMPERATURE = float(os.environ.get("AZURE_OPENAI_TEMPERATURE", 0.3))
    AZURE_OPENAI_MAX_RESPONSE_TOKENS = int(
        os.environ.get("AZURE_OPENAI_MAX_RESPONSE_TOKENS", 4096)
    )

    LANGCHAIN_AGENT_MODEL_TEMPERATURE = float(
        os.environ.get("LANGCHAIN_AGENT_MODEL_TEMPERATURE", 0.3)
    )

    # AWS Bedrock-related settings
    BEDROCK_LANGCHAIN_AGENT_MODEL_ID = os.environ.get(
        "BEDROCK_LANGCHAIN_AGENT_MODEL_ID",
        # "anthropic.claude-3-haiku-20240307-v1:0"
        # "anthropic.claude-3-sonnet-20240229-v1:0",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        # "anthropic.claude-3-opus-20240229-v1:0",
    )

    BEDROCK_GENERAL_MODEL_ID = os.environ.get(
        "BEDROCK_GENERAL_MODEL_ID",
        "anthropic.claude-3-haiku-20240307-v1:0",
        # "anthropic.claude-3-sonnet-20240229-v1:0",
        # "anthropic.claude-3-opus-20240229-v1:0",
    )
    BEDROCK_TEMPERATURE = float(os.environ.get("BEDROCK_TEMPERATURE", 0.3))

    BEDROCK_PROFILE_NAME = os.environ.get("BEDROCK_PROFILE_NAME", "default")
    BEDROCK_AWS_REGION = os.environ.get("BEDROCK_AWS_REGION", "us-east-1")
    BEDROCK_MAX_RESPONSE_TOKENS = int(
        os.environ.get("BEDROCK_MAX_RESPONSE_TOKENS", 4096)
    )

    AGENT_MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERATIONS", 30))
    COMMAND_OUTPUT_MAX_LENGTH_CHARS = int(
        os.environ.get("COMMAND_OUTPUT_MAX_LENGTH_CHARS", 10000)
    )

    OLLAMA_ENDPOINT_URL = os.environ.get(
        "OLLAMA_ENDPOINT_URL", "http://localhost:11434"
    )
    OLLAMA_MODEL_ID = os.environ.get("OLLAMA_MODEL_ID", "llama3.2")
    OLLAMA_MAX_TOKENS = int(os.environ.get("OLLAMA_MAX_TOKENS", "4096"))
    OLLAMA_TEMPERATURE = float(os.environ.get("OLLAMA_TEMPERATURE", "0.3"))

    # Gemini-related settings
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GEMINI_MODEL_ID = os.environ.get("GEMINI_MODEL_ID", "gemini-2.0-flash")
    GEMINI_TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", 0.3))
    GEMINI_MAX_OUTPUT_TOKENS = int(os.environ.get("GEMINI_MAX_OUTPUT_TOKENS", 4096))

    LLM_TO_USE = os.environ.get("LLM_TO_USE", "openai")

    ALLOW_POTENTIALLY_RISKY_LLM_COMMANDS = os.environ.get(
        "ALLOW_POTENTIALLY_RISKY_LLM_COMMANDS", "ask"
    ).lower()

    ASK_FOR_USER_CONFIRMATION_BEFORE_EXECUTING_EACH_COMMAND = (
        os.environ.get(
            "ASK_FOR_USER_CONFIRMATION_BEFORE_EXECUTING_EACH_COMMAND", "false"
        ).lower()
        == "true"
    )

    STANDARD_TOOLS = os.environ.get(
        "STANDARD_TOOLS",
        (
            "git,cat,find,sed,awk,xargs,ping,wget,curl,dig,traceroute,helm,"
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

    SKIP_LLM_FUNCTIONALITY_VERIFICATION = (
        os.environ.get("SKIP_LLM_FUNCTIONALITY_VERIFICATION", "false") == "true"
    )

    SKIP_THE_CHECK_FOR_AVAILABLE_TOOLS = (
        os.environ.get("SKIP_THE_CHECK_FOR_AVAILABLE_TOOLS", "false") == "true"
    )

    @classmethod
    def validate(self):
        load_dotenv(override=False)

        required_vars = []

        if self.LLM_TO_USE not in [
            "openai",
            "azure-openai",
            "bedrock",
            "ollama",
            "gemini",
        ]:
            print(
                f"ERROR: Invalid value for LLM_TO_USE: {self.LLM_TO_USE}. Must be one "
                "of 'openai', 'azure-openai', 'ollama', or 'bedrock'."
            )
            exit(1)

        # Check that all required variables are set; list missing environment variables before raising an exception
        if self.LLM_TO_USE == "openai":
            required_vars = [
                "OPENAI_API_KEY",
            ]

        if self.LLM_TO_USE == "azure-openai":
            required_vars = [
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_DEPLOYMENT_ID",
                "AZURE_OPENAI_ENDPOINT",
            ]

        # Add Gemini validation
        if self.LLM_TO_USE == "gemini":
            required_vars.append("GOOGLE_API_KEY")

        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            print(f"Missing required environment variables: {missing_vars}")
            exit(1)


config = Config()
