import tiktoken
import openai

# Shared libraries
from common.config import Config as config
from common.logger import log_message

client = openai.OpenAI(api_key=config.OPENAI_API_KEY)


def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4-0613")
    num_tokens = len(encoding.encode(text))
    return num_tokens


def call_openai(prompt, model=config.OPENAI_LANGCHAIN_AGENT_MODEL_ID):
    try:
        tokens = count_tokens(prompt)
        log_message("INFO", f"Calling OpenAI ({tokens} tokens in the prompt)...")
        response_from_openai = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        response = response_from_openai.choices[0].message.content
        log_message("INFO", f"Response from OpenAI: {response}")
        return response

    except Exception as e:
        log_message("ERROR", f"Error while calling OpenAI: {e}")
        return False
