import json
import os
import re
from time import sleep
from pathlib import Path

import tiktoken
import yaml
import google.generativeai as genai

from shortGPT.config.api_db import ApiKeyManager


def num_tokens_from_messages(texts, model="gpt-4o-mini"):
    """Calculates the number of tokens used by a string or a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
        
    if isinstance(texts, str):
        texts = [texts]
        
    return sum(4 + len(encoding.encode(text)) for text in texts)


def extract_biggest_json(string):
    """
    Extracts the largest valid JSON object from a string using balanced brace matching.
    Avoids native regex recursive execution errors (?R) in standard re module.
    """
    best_json = None
    max_length = 0
    
    # Locate all potential starting points for a JSON object
    for match in re.finditer(r'\{', string):
        start_idx = match.start()
        brace_count = 0
        
        for end_idx in range(start_idx, len(string)):
            char = string[end_idx]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                
            if brace_count == 0:
                substring = string[start_idx:end_idx + 1]
                try:
                    # Validate that it is actually parsable JSON
                    json.loads(substring)
                    if len(substring) > max_length:
                        max_length = len(substring)
                        best_json = substring
                except json.JSONDecodeError:
                    pass
                break  # Break inner loop once the outer-most matching brace is found
                
    return best_json


def get_first_number(string):
    """Searches for the first occurrence of a number 0-10 in a string."""
    match = re.search(r'\b(0|[1-9]|10)\b', string)
    return int(match.group()) if match else None


def load_yaml_file(file_path: str) -> dict:
    """Reads and returns the contents of a YAML file as a dictionary."""
    return yaml.safe_load(open_file(file_path))


def load_json_file(file_path):
    """Reads and returns the contents of a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_local_yaml_prompt(file_path):
    """Loads a YAML template containing chat and system prompts."""
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    json_template = load_yaml_file(str(_absolute_path))
    return json_template['chat_prompt'], json_template['system_prompt']


def open_file(filepath):
    """Opens and reads a file and returns its contents as a string."""
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def llm_completion(chat_prompt="", system="", temp=0.7, max_tokens=2000, remove_nl=True, conversation=None):
    """
    Performs LLM completion using an ordered Gemini rotation pool with 
    automatic fallback to OpenAI or Groq endpoint architectures.
    """
    openai_key = ApiKeyManager.get_api_key("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
    gemini_key = ApiKeyManager.get_api_key("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    # Check if we should force skip Gemini and go directly to Groq
    force_groq = os.getenv("FORCE_GROQ", "false").lower() == "true"

    # Ordered pool of Gemini models to switch between when hitting tier quotas
    gemini_models_pool = ["gemini-2.5-flash", "gemini-1.5-flash"]
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Auto-adjust model targeted to a Groq endpoint base URL
    if os.getenv("OPENAI_API_BASE") and "groq" in os.getenv("OPENAI_API_BASE").lower():
        openai_model = "llama-3.1-8b-instant"

    force_openai_fallback = False
    last_gemini_error = ""

    # ✅ Tier 1: Gemini Engine Execution & Model Rotation
    # Skip Gemini entirely if FORCE_GROQ is enabled
    if gemini_key and not force_groq:
        try:
            genai.configure(api_key=gemini_key)
            
            for current_model in gemini_models_pool:
                print(f"DEBUG: Initializing Gemini client with model = {current_model}")
                
                model = genai.GenerativeModel(
                    model_name=current_model,
                    system_instruction=system if system else None
                )

                max_retry = 3
                quota_hit_for_current_model = False
                
                for i in range(max_retry):
                    try:
                        response = model.generate_content(
                            chat_prompt,
                            generation_config={
                                "temperature": float(temp),
                                "max_output_tokens": max_tokens
                            }
                        )
                        text = response.text.strip()
                        if remove_nl:
                            text = re.sub(r'\s+', ' ', text)
                        return text
                        
                    except Exception as oops:
                        last_gemini_error = str(oops)
                        print(f"Error communicating with Gemini ({current_model}) [Attempt {i+1}/{max_retry}]: {last_gemini_error}")

                        # Check for free tier quota or rate limit errors
                        if any(kw in last_gemini_error for kw in ["Quota exceeded", "ResourceExhausted", "limit", "429"]):
                            print(f"🛑 Free tier quota exhausted for {current_model}. Rotating strategy...")
                            quota_hit_for_current_model = True
                            break  # Break retry loop to attempt the next model in pool or trigger fallback
                        
                        # Soft backoff for standard temporary unexpected connectivity drops
                        sleep(5)
                
                # If execution failed but it wasn't quota-related, do not continue rotating models
                if not quota_hit_for_current_model:
                    break

            # If the rotation loop finishes without returning a valid output, handoff execution
            force_openai_fallback = True

        except Exception as gemini_block_err:
            last_gemini_error = str(gemini_block_err)
            force_openai_fallback = True
    else:
        # Skip Gemini entirely - either no key or FORCE_GROQ is set
        if force_groq:
            print("🔄 [GROQ FORCED]: Skipping Gemini and using Groq directly.")
        force_openai_fallback = True

    # 🚀 Tier 2: OpenAI / Groq Endpoint Fallback Layer
    if force_openai_fallback or (not gemini_key and openai_key):
        if not openai_key:
            raise Exception(f"All Gemini models exhausted ({last_gemini_error}), and no fallback OpenAI/Groq API Key was found.")
            
        from openai import OpenAI
        target_key = openai_key
        target_base = os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1")

        print(f"🎙️ [EXECUTION TRANSFER]: Querying backup engine: Base='{target_base}', Model='{openai_model}'")

        client = OpenAI(api_key=target_key, base_url=target_base)
        messages = conversation if conversation else [
            {"role": "system", "content": system},
            {"role": "user", "content": chat_prompt}
        ]

        response = client.chat.completions.create(
            model=openai_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=float(temp),
            timeout=30
        )
        text = response.choices[0].message.content.strip()
        if remove_nl:
            text = re.sub(r'\s+', ' ', text)
        return text

    raise Exception("No active API keys found (Gemini, OpenAI, or Groq) to fulfill the completion request.") 
