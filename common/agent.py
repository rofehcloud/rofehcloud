import openai
import platform

import time
import subprocess
import questionary
from colorama import init, Style

from langchain import hub
from langchain_community.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI as OpenAILangChain
from langchain_openai import AzureChatOpenAI


from common.config import Config as config
from common.logger import log_message

from common.utils import fix_unclosed_quote
from common.constants import (
    error_response,
    agent_prompt_with_history,
    data_modification_command_denied,
)
from common.llm import call_llm

init(autoreset=True)

chat_history_store = {}

prompt_with_chat_history = hub.pull("hwchase17/react-chat")

prompt_with_chat_history.template = agent_prompt_with_history


def get_session_history(conversation_history) -> BaseChatMessageHistory:
    chat_history_store = ChatMessageHistory()
    for chat_entry in conversation_history:
        chat_history_store.add_user_message(chat_entry["question"])
        chat_history_store.add_ai_message(chat_entry["answer"])

    result = chat_history_store
    log_message("DEBUG", f"Chat history records: {result}")
    return result


def check_that_command_is_safe(command):
    prompt = (
        "Review the following command and reply with Yes if the command is making any "
        "changes to the system. Reply with No if the command is not making any changes and is safe to"
        f"execute. Do not add any comments. Command to review: \n\n{command}"
    )
    response = call_llm(prompt, config.LLM_TO_USE)

    if response is None or response == "":
        log_message(
            "ERROR", "Failed to validate that the command is not making any changes"
        )
        return (
            False,
            "ERROR: Failed to validate that the command is not making any changes",
        )

    if response.lower() == "yes":
        return False, "ERROR: The command is making changes to the system"

    if response.lower() == "no":
        return True, "The command is not making any changes to the system"

    return (
        False,
        f"ERROR: Failed to validate that the command is not making any changes (received response: {response})",
    )


def api_command_executor(command):
    command = fix_unclosed_quote(command)

    if config.ASK_FOR_USER_CONFIRMATION_BEFORE_EXECUTING_EACH_COMMAND:
        print(
            Style.BRIGHT
            + "\nThe system would like to execute the following command:\n"
            + Style.RESET_ALL
            + command
        )
        print("\n\n")
        response = questionary.confirm(
            "Would you like the command to be executed?"
        ).ask()
        if not response:
            return data_modification_command_denied

    elif config.ALLOW_POTENTIALLY_RISKY_LLM_COMMANDS in ["ask", "no"]:
        safe_command, safe_command_message = check_that_command_is_safe(command)
        if not safe_command:
            if config.ALLOW_POTENTIALLY_RISKY_LLM_COMMANDS == "ask":
                print(
                    Style.BRIGHT
                    + "\nAttention! The system would like to execute a command that may change some data.\n"
                    "The command that is planned to be executed:\n"
                    + Style.RESET_ALL
                    + command
                )
                print("\n\n")
                response = questionary.confirm(
                    "Would you like the command to be executed?"
                ).ask()
                if not response:
                    return data_modification_command_denied

            else:
                return data_modification_command_denied

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    stdout = result.stdout
    stderr = result.stderr
    error_code = result.returncode
    if len(stdout) == 0 and len(stderr) == 0:
        return f"Empty Response (command exit code: {error_code})"

    output = stdout + stderr

    if len(output) > config.COMMAND_OUTPUT_MAX_LENGTH_CHARS:
        log_message(
            "DEBUG",
            f"Output is too long: {len(output)} characters; "
            f"truncating to {config.COMMAND_OUTPUT_MAX_LENGTH_CHARS} characters",
        )
        output = output[: config.COMMAND_OUTPUT_MAX_LENGTH_CHARS] + "\n... (truncated)"
    else:
        log_message("DEBUG", f"Output length: {len(output)} characters")

    return output


def return_current_date_time(string):
    return (
        f'Current UTC date/time is {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}'
    )


def before_generating_the_final_answer(prompt: str) -> str:
    return "Please generate the final answer to the original input question."


agent_with_chat_history = None


def setup_services(profile: str):
    global agent_with_chat_history

    try:
        log_message(
            "DEBUG",
            "Initializing the client configuration...",
        )
        start_time = time.time()
        tools = {}

        if config.LLM_TO_USE == "openai":
            print(
                f"Using OpenAI LLM, model ID for the agent: {config.OPENAI_LANGCHAIN_AGENT_MODEL_ID}"
                f" with temperature: {config.LANGCHAIN_AGENT_MODEL_TEMPERATURE}; "
                f"model ID for general calls: {config.OPENAI_GENERAL_MODEL_ID}"
            )
            openai.api_key = config.OPENAI_API_KEY
            llm_langchain = OpenAILangChain(
                temperature=config.OPENAI_TEMPERATURE,
                model=config.OPENAI_LANGCHAIN_AGENT_MODEL_ID,
                openai_api_key=config.OPENAI_API_KEY,
                request_timeout=240,
                max_tokens=4096,
                streaming=False,
            )
        elif config.LLM_TO_USE == "bedrock":
            print(
                f"Using Bedrock LLM, model ID for the agent: {config.BEDROCK_LANGCHAIN_AGENT_MODEL_ID}"
                f" with profile name: {config.BEDROCK_PROFILE_NAME} in region: {config.BEDROCK_AWS_REGION}, "
                f"model ID for general calls: {config.BEDROCK_GENERAL_MODEL_ID}"
            )

            llm_langchain = ChatBedrock(
                credentials_profile_name=config.BEDROCK_PROFILE_NAME,
                region_name=config.BEDROCK_AWS_REGION,
                model_id=config.BEDROCK_LANGCHAIN_AGENT_MODEL_ID,
                model_kwargs={
                    "temperature": config.BEDROCK_TEMPERATURE,
                    "max_tokens": 4096,
                },
            )

        elif config.LLM_TO_USE == "azure-openai":
            print(
                f"Using Azure OpenAI LLM, model ID for the agent: {config.AZURE_OPENAI_MODEL_ID}"
                f" with temperature: {config.AZURE_OPENAI_TEMPERATURE}, "
                f"deployment ID: {config.AZURE_OPENAI_DEPLOYMENT_ID}, "
                f"API version: {config.AZURE_OPENAI_API_VERSION}"
            )

            llm_langchain = AzureChatOpenAI(
                azure_deployment=config.AZURE_OPENAI_DEPLOYMENT_ID,
                api_version=config.AZURE_OPENAI_API_VERSION,
                temperature=config.AZURE_OPENAI_TEMPERATURE,
                max_tokens=4096,
                timeout=240,
                max_retries=2,
            )
        else:
            raise ValueError(f"LLM {config.LLM_TO_USE} is not supported.")

        tools = []
        tool_names = []

        tools.extend(
            [
                Tool.from_function(
                    func=return_current_date_time,
                    name="Get current date/time",
                    description=(
                        "Call the tool if you need to get the current date and time in UTC."
                    ),
                ),
            ]
        )

        cli_tool_description = (
            f"Run a shell command on this machine (OS {platform.system()} {platform.version()}). "
            "macOS/Darwin does not support -d flag for 'date' command. "
        )

        if "aws" in config.ALL_TOOLS:
            log_message("DEBUG", "Adding AWS CLI tool...")
            tool_names.append("aws")

            cli_tool_description += (
                "Can be used to get the current state of AWS "
                "resources using 'aws' commands. "
                "When requesting "
                "AWS CloudWatch metrics, pull the data for no more the past 7 days. "
            )

        if "gcloud" in config.ALL_TOOLS:
            log_message("DEBUG", "Adding gcloud CLI tool...")
            tool_names.append("gcloud")

            cli_tool_description += (
                "Can be used to get the current state of Google Cloud (GCP) "
                "resources using 'gcloud' commands. "
            )

        if "kubectl" in config.ALL_TOOLS:
            log_message("DEBUG", "Adding kubectl CLI tool...")
            tool_names.append("kubectl")

            cli_tool_description += (
                "Can be used to get the current state of Kubernetes "
                "resources using 'kubectl' commands. "
                "When requesting K8s resources, pull the data for no more the past 7 days. "
            )

        if "az" in config.ALL_TOOLS:
            log_message("DEBUG", "Adding Azure az CLI tool...")
            tool_names.append("az")

            cli_tool_description += (
                "Can be used to get the current state of Azure "
                "resources using 'az' commands. "
            )

        if "esxcli" in config.ALL_TOOLS:
            log_message("DEBUG", "Adding esxcli tool...")
            tool_names.append("esxcli")

            cli_tool_description += (
                "Can be used to get the current state of VMware ESXi "
                "resources using 'esxcli' commands. "
            )

        if "ncli" in config.ALL_TOOLS:
            log_message("DEBUG", "Adding ncli tool...")
            tool_names.append("ncli")

            cli_tool_description += (
                "Can be used to get the current state of Nutanix "
                "resources using 'ncli' commands. "
            )

        if len(tool_names) == 0:
            raise ValueError("No public cloud or K8s tools are available to work with.")

        cli_tool_description += (
            f"Other supported commands are {config.ALL_TOOLS}. "
            "The tool accepts one argument - the command to run "
            "(no comments, no redirects). "
            "In general, try to limit the "
            "amount of data returned by the shell command to no more than 100 lines. "
            "If the tool returns 'Empty Response' or '[]' string then do not use it again "
            "for the same query. "
            "If a command returns an error, then analyze the error message "
            "and try to fix the command."
        )

        tools.append(
            Tool.from_function(
                func=api_command_executor,
                name="Run a shell command or access CLI tools",
                description=cli_tool_description,
            )
        )

        print(
            Style.BRIGHT
            + "Registered langchain tools: "
            + Style.RESET_ALL
            + ", ".join(tool_names)
            + "\n"
        )

        log_message(
            "DEBUG",
            f"Finished setting up tools, "
            f"number of registered tools: {len(tools)}...",
        )

        log_message("DEBUG", "Initializing the LangChain agent...")

        agents_with_history = create_react_agent(
            llm_langchain,
            tools,
            # langchain_prompt,
            prompt_with_chat_history,
        )

        agent_executors_with_history = AgentExecutor(
            agent=agents_with_history,
            tools=tools,
            verbose=True,
            max_iterations=config.AGENT_MAX_ITERATIONS,
            handle_parsing_errors=(
                "Check you output and make sure it conforms! Do not output an action and a final "
                "answer at the same time."
            ),
        )

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executors_with_history,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        log_message(
            "DEBUG",
            f"Client initialization was successful (elapsed time: {str(elapsed_time)} seconds)",
        )

    except Exception as e:
        log_message("ERROR", f"Client initialization failed: {str(e)}")
        raise e


def agent_chat(user_input, conversation_history):
    try:
        full_agent_response = agent_with_chat_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": conversation_history}},
        )

        agent_response = full_agent_response["output"]
        log_message(
            "DEBUG",
            "Received response from the LangChain agent: " + agent_response,
        )
        return str(agent_response)

    except Exception as e:
        log_message("ERROR", f"An error occurred while handling user prompt: {str(e)}")
        return error_response


def handle_user_prompt(profile, user_input, conversation_history=[]):
    try:
        start_time = time.time()
        bot_response = agent_chat(user_input, conversation_history)

        final_response_time = time.time()
        seconds_lapsed = final_response_time - start_time
        log_message("DEBUG", "Time elapsed: %s seconds" % seconds_lapsed)

        return bot_response

    except Exception as e:
        log_message("ERROR", f"An error occurred: {str(e)}")
        return error_response
