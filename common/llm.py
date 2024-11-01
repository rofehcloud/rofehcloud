import tiktoken
import openai
import json
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Shared libraries
from common.config import Config as config
from common.logger import log_message

client = openai.OpenAI(api_key=config.OPENAI_API_KEY)


boto3_config = Config(read_timeout=300)
session = boto3.Session(
    profile_name=config.BEDROCK_PROFILE_NAME, region_name=config.BEDROCK_AWS_REGION
)
bedrock_client = session.client(service_name="bedrock-runtime")


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4-0613")
    num_tokens = len(encoding.encode(text))
    return num_tokens


def call_llm(prompt, llm):
    if llm == "openai":
        return call_openai(prompt, config.OPENAI_GENERAL_MODEL_ID)
    elif llm == "bedrock":
        return call_bedrock_llm(prompt, config.BEDROCK_GENERAL_MODEL_ID)
    else:
        log_message("ERROR", f"LLM {llm} not supported.")
        return False


def call_openai(prompt, model_id):
    try:
        tokens = count_tokens(prompt)
        log_message("DEBUG", f"Calling OpenAI ({tokens} tokens in the prompt)...")
        response_from_openai = client.chat.completions.create(
            model=model_id,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        response = response_from_openai.choices[0].message.content
        log_message("DEBUG", f"Response from OpenAI: {response}")
        return response

    except Exception as e:
        log_message("ERROR", f"Error while calling OpenAI: {e}")
        return False


def call_bedrock_llm(prompt, model_id):
    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "temperature": 0.0,
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

        log_message("INFO", "Bedrock Invocation details:")
        log_message("INFO", f"The input length is {input_tokens} tokens.")
        log_message("INFO", f"The output length is {output_tokens} tokens.")

        log_message(
            "INFO",
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
