import json
import os
import re
from time import sleep, time
from pathlib import Path

import tiktoken
import yaml
import google.generativeai as genai

from shortGPT.config.api_db import ApiKeyManager


def num_tokens_from_messages(texts, model="gpt-4o-mini"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-4o-mini":
        if isinstance(texts, str):
            texts = [texts]
        return sum(4 + len(encoding.encode(text)) for text in texts)
    raise NotImplementedError(f"num_tokens_from_messages() not implemented for {model}")


def extract_biggest_json(string):
    json_regex = r"\{(?:[^{}]|(?R))*\}"
    json_objects = re.findall(json_regex, string)
    return max(json_objects, key=len) if json_objects else None


def get_first_number(string):
    match = re.search(r'\b(0|[1-9]|10)\b', string)
    return int(match.group()) if match else None


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

    # ✅ Use plain model name (no "models/" prefix)
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if gemini_key:
        genai.configure(api_key=gemini_key)
        print("DEBUG: Using Gemini client library with model =", gemini_model)
        model = genai.GenerativeModel(gemini_model)

        max_retry = 5
        error = ""
        for i in range(max_retry):
            try:
                response = model.generate_content(
                    chat_prompt,
                    generation_config={
                        "temperature": temp,
                        "max_output_tokens": max_tokens
                    }
                )
                text = response.text.strip()
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
                print("Error communicating with Gemini:", oops)
                error = str(oops)
                sleep(1)
        raise Exception(f"Gemini completion failed after retries: {error}")

    elif openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        model = openai_model
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
        return text

    else:
        raise Exception("No OpenAI or Gemini API Key found for LLM request")
