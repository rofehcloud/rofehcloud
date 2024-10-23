from langchain import hub
from langchain_community.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI as OpenAILangChain


# from llama_index.llms.bedrock import Bedrock as BedrockLlamaIndex

# from botocore.config import Config
# from botocore.exceptions import ClientError

# import boto3
import openai

# import json
import time
import subprocess

from common.config import Config as config
from common.logger import log_message

from common.utils import fix_unclosed_quote
from common.constants import error_response, agent_prompt_with_history


chat_history_store = {}


def get_session_history(conversation_history) -> BaseChatMessageHistory:
    chat_history_store = ChatMessageHistory()
    # log_message("INFO", f"Retrieved {len(conversation_history)} chat entries")
    # log_message("INFO", f"Chat history: {conversation_history}")
    for chat_entry in conversation_history:
        chat_history_store.add_user_message(chat_entry["question"])
        chat_history_store.add_ai_message(chat_entry["answer"])

    result = chat_history_store
    # log_message("INFO", f"Chat history: {result}")
    return result


client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
openai.api_key = config.OPENAI_API_KEY

# llm_llamaindex = OpenAILlamaIndex(temperature=0, api_key=config.openai_api_key)
# llm_llamaindex = BedrockLlamaIndex(model=config.BEDROCK_VECTORDB_RESPONSE_MODEL_ID)

prompt_with_chat_history = hub.pull("hwchase17/react-chat")

prompt_with_chat_history.template = agent_prompt_with_history


def api_command_executor(command):
    command = fix_unclosed_quote(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout + "\n" + result.stderr


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

        # collection_name_prefix = generate_collection_name(profile)

        llm_langchain = OpenAILangChain(
            temperature=config.LANGCHAIN_AGENT_MODEL_TEMPERATURE,
            model=config.OPENAI_LANGCHAIN_AGENT_MODEL_ID,
            openai_api_key=config.OPENAI_API_KEY,
            request_timeout=240,
            max_tokens=4096,
            streaming=False,
        )

        tools = []

        """
        tools.extend(
            [
                Tool.from_function(
                    func=before_generating_the_final_answer,
                    name="Before final answer",
                    description=(
                        "Call the tool right before generating the final answer to the original user "
                        "question. Specify 'N/A' as the action input for the tool. Ignore the "
                        "output of the tool."
                    ),
                ),
            ]
        )
        """

        if True:
            log_message("DEBUG", "Adding API tool...")

            cli_tool_description = (
                "Run a shell command on this machine. "
                "Can be used to get the current state of AWS "
                "resources using 'aws' commands. Can run 'dig' "
                "command to check DNS records, or 'ping' command to check network "
                "connectivity. "
                "Other supported commands are cat, find, awk, sed, xargs, cut, sort, uniq, wc, "
                "tail, head, grep and egrep. The tool does not support kubectl or helm commands. "
                "The shell accepts one argument - the command to run "
                "(no comments, no redirects). "
                "When requesting "
                "AWS CloudWatch metrics, pull the data for no more the past 7 days. "
                "In general, try to limit the "
                "amount of data returned by the shell command to no more than 100 lines. "
                "If the tool returns 'Empty Response' string then do not use it again "
                "for the same query. "
                "If a command returns an error, then analyze the error message "
                "and try to fix the command."
            )

            tools.append(
                Tool.from_function(
                    func=api_command_executor,
                    name="Run a shell command or access AWS/GCP CLI tools",
                    description=cli_tool_description,
                ),
            )

        log_message(
            "DEBUG",
            f"Finished setting up tools, "
            f"number of registered tools: {len(tools)}...",
        )

        log_message("DEBUG", "Initializing the LangChain agent...")

        agents_with_history = create_react_agent(
            # llm_bedrock_langchain,
            # llm_anthropic_langchain,
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
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
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
