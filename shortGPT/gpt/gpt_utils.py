import json
import os
import re
from time import sleep, time

import openai
import tiktoken
import yaml

from shortGPT.config.api_db import ApiKeyManager
from pathlib import Path
from openai import OpenAI

def num_tokens_from_messages(texts, model="gpt-4o-mini"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-4o-mini":
        if isinstance(texts, str):
            texts = [texts]
        score = 0
        for text in texts:
            score += 4 + len(encoding.encode(text))
        return score
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not presently implemented for model {model}."
        )

def extract_biggest_json(string):
    json_regex = r"\{(?:[^{}]|(?R))*\}"
    json_objects = re.findall(json_regex, string)
    if json_objects:
        return max(json_objects, key=len)
    return None

def get_first_number(string):
    pattern = r'\b(0|[1-9]|10)\b'
    match = re.search(pattern, string)
    if match:
        return int(match.group())
    else:
        return None

def load_yaml_file(file_path: str) -> dict:
    return yaml.safe_load(open_file(file_path))

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_local_yaml_prompt(file_path):
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    json_template = load_yaml_file(str(_absolute_path))
    return json_template['chat_prompt'], json_template['system_prompt']

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def llm_completion(chat_prompt="", system="", temp=0.7, max_tokens=2000, remove_nl=True, conversation=None):
    openai_key = ApiKeyManager.get_api_key("OPENAI_API_KEY")
    gemini_key = ApiKeyManager.get_api_key("GEMINI_API_KEY")

    # ✅ Use environment variables for model selection
    gemini_model = os.getenv("GEMINI_MODEL", "models/gemini-1.0-pro")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = gemini_model
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = openai_model
    else:
        raise Exception("No OpenAI or Gemini API Key found for LLM request")

    max_retry = 5
    error = ""
    for i in range(max_retry):
        try:
            messages = conversation if conversation else [
                {"role": "system", "content": system},
                {"role": "user", "content": chat_prompt}
            ]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temp,
                timeout=30
            )
            text = response.choices[0].message.content.strip()
            if remove_nl:
                text = re.sub(r'\s+', ' ', text)
            filename = f"{time()}_llm_completion.txt"
            os.makedirs('.logs/gpt_logs', exist_ok=True)
            with open(f'.logs/gpt_logs/{filename}', 'w', encoding='utf-8') as outfile:
                outfile.write(
                    f"System prompt: ===\n{system}\n===\n"
                    f"Chat prompt: ===\n{chat_prompt}\n===\n"
                    f"RESPONSE:\n====\n{text}\n===\n"
                )
            return text
        except Exception as oops:
            print('Error communicating with LLM:', oops)
            error = str(oops)
            sleep(1)
    raise Exception(f"Error communicating with LLM Endpoint Completion errored more than error: {error}")
