from shortGPT.gpt import gpt_utils
import json

def generateFacts(facts_type):
    # Load prompt templates
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/facts_generator.yaml')
    chat = chat.replace("<<FACTS_TYPE>>", facts_type)

    # Call Gemini/OpenAI via gpt_utils
    result = gpt_utils.llm_completion(chat_prompt=chat, system=system, temp=1.3)
    return result


def generateFactSubjects(n):
    out = []
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/facts_subjects_generation.yaml')
    chat = chat.replace("<<N>>", f"{n}")

    maxAttempts = int(1.5 * n)
    attempts = 0

    # ✅ Use logical 'and' instead of bitwise '&'
    while len(out) != n and attempts <= maxAttempts:
        result = gpt_utils.llm_completion(chat_prompt=chat, system=system, temp=1.69)
        attempts += 1
        try:
            out = json.loads(result.replace("'", '"'))
        except Exception as e:
            print(f"INFO - Failed generating {n} fact subjects after {attempts} trials", e)
            pass

    if len(out) != n:
        raise Exception(f"Failed to generate {n} subjects in {attempts} attempts")

    return out
