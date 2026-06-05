from shortGPT.gpt import gpt_utils

def translateContent(content, language="english"):
    # Always translate into English
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/translate_content.yaml')

    # Force language to English regardless of input
    language = "english"

    # Replace placeholders in system and chat prompts
    system = system.replace("<<LANGUAGE>>", language)
    chat = chat.replace("<<CONTENT>>", content)

    # Call Gemini/OpenAI via gpt_utils
    result = gpt_utils.llm_completion(chat_prompt=chat, system=system, temp=1)
    return result
