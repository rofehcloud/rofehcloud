import tiktoken
import openai
from openai import AzureOpenAI
import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from ollama import Client

from rofehcloud.config import Config as config
from rofehcloud.logger import log_message


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4-0613")
    num_tokens = len(encoding.encode(text))
    return num_tokens


def call_llm(prompt, llm):
    if llm == "openai":
        return call_openai(prompt, config.OPENAI_GENERAL_MODEL_ID)
    elif llm == "bedrock":
        return call_bedrock_llm(prompt, config.BEDROCK_GENERAL_MODEL_ID)
    elif llm == "azure-openai":
        return call_azure_openai_llm(prompt, config.AZURE_OPENAI_MODEL_ID)
    elif llm == "ollama":
        return call_ollama(prompt, config.OLLAMA_MODEL_ID)
    else:
        log_message("ERROR", f"LLM {llm} not supported.")
        return False


def call_openai(prompt, model_id):
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    try:
        tokens = count_tokens(prompt)
        log_message("DEBUG", f"Calling OpenAI ({tokens} tokens in the prompt)...")
        response_from_openai = client.chat.completions.create(
            model=model_id,
            temperature=config.OPENAI_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        response = response_from_openai.choices[0].message.content
        log_message("DEBUG", f"Response from OpenAI: {response}")
        return response

    except Exception as e:
        log_message("ERROR", f"Error while calling OpenAI: {e}")
        return False


def call_azure_openai_llm(prompt, model_id):
    client = AzureOpenAI(
        api_key=config.AZURE_OPENAI_API_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
    )

    try:
        tokens = count_tokens(prompt)
        log_message("DEBUG", f"Calling Azure OpenAI ({tokens} tokens in the prompt)...")
        response_from_openai = client.chat.completions.create(
            model=model_id,
            temperature=config.AZURE_OPENAI_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )
        response = response_from_openai.choices[0].message.content
        log_message("DEBUG", f"Response from Azure OpenAI: {response}")
        return response

    except Exception as e:
        log_message("ERROR", f"Error while calling Azure OpenAI: {e}")
        return False


def call_ollama(prompt, model_id):
    client = Client(
        host=config.OLLAMA_ENDPOINT_URL,
    )
    try:
        response_from_ollama = client.chat(
            model=config.OLLAMA_MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            stream=False,
        )
        response = response_from_ollama.message.content
        log_message("DEBUG", f"Response from Ollama: {response}")
        return response
    except Exception as e:
        log_message("ERROR", f"Error while calling Ollama: {e}")
        return False


def call_bedrock_llm(prompt, model_id):
    Config(read_timeout=300)
    session = boto3.Session(
        profile_name=config.BEDROCK_PROFILE_NAME,
        region_name=config.BEDROCK_AWS_REGION,
    )
    bedrock_client = session.client(service_name="bedrock-runtime")

    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": config.BEDROCK_MAX_RESPONSE_TOKENS,
                    "temperature": config.BEDROCK_TEMPERATURE,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                }
            ),
        )

        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        log_message("DEBUG", "Bedrock Invocation details:")
        log_message("DEBUG", f"The input length is {input_tokens} tokens.")
        log_message("DEBUG", f"The output length is {output_tokens} tokens.")

        log_message(
            "DEBUG",
            f"The model returned {len(output_list)} response(s):",
        )
        for output in output_list:
            log_message("INFO", output["text"])

        return output_list[0]["text"]

    except ClientError as err:
        log_message(
            "ERROR",
            "Couldn't invoke Bedrock LLM. Here's why: "
            + f'{err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}',
        )
        return None


def verify_llm_functionality():
    try:
        if config.SKIP_LLM_FUNCTIONALITY_VERIFICATION:
            log_message("INFO", "Skipping LLM functionality verification.")
            return True

        log_message("INFO", f"Verifying LLM functionality ({config.LLM_TO_USE})...")
        response = call_llm("Hello, world!", config.LLM_TO_USE)

        if isinstance(response, str) and len(response) > 0:
            log_message("DEBUG", "LLM functionality verified.")
            return True
        else:
            raise Exception("LLM functionality verification failed.")
            return False

    except Exception as e:
        log_message("ERROR", f"Error while verifying LLM functionality: {e}")
        return False
