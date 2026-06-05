from shortGPT.gpt import gpt_utils
import json

def generateScript(script_description, language):
    out = {'script': ''}
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/chat_video_script.yaml')
    chat = chat.replace("<<DESCRIPTION>>", script_description).replace("<<LANGUAGE>>", language)

    # Loop until we get a valid JSON with 'script'
    while not out.get('script'):
        try:
            result = gpt_utils.llm_completion(chat_prompt=chat, system=system, temp=1)
            out = json.loads(result)
        except Exception as e:
            print(e, "Difficulty parsing the output in gpt_chat_video.generateScript")
            out = {'script': ''}  # reset to avoid breaking loop
    return out['script']


def correctScript(script, correction):
    out = {'script': ''}
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/chat_video_edit_script.yaml')
    chat = chat.replace("<<ORIGINAL_SCRIPT>>", script).replace("<<CORRECTIONS>>", correction)

    # Loop until we get a valid JSON with 'script'
    while not out.get('script'):
        try:
            result = gpt_utils.llm_completion(chat_prompt=chat, system=system, temp=1)
            out = json.loads(result)
        except Exception as e:
            print(e, "Difficulty parsing the output in gpt_chat_video.correctScript")
            out = {'script': ''}  # reset to avoid breaking loop
    return out['script']
