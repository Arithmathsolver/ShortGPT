import os
import sys
import json
import random
import subprocess

# 1. FIND THE HIDDEN INSTALLATION
# This part finds where 'pip' actually put ShortGPT
def get_pip_install_path():
    try:
        result = subprocess.check_output([sys.executable, '-m', 'pip', 'show', 'shortgpt'], text=True)
        for line in result.split('\n'):
            if line.startswith('Location:'):
                return line.split(': ')[1].strip()
    except:
        return None

install_path = get_pip_install_path()
if install_path and install_path not in sys.path:
    sys.path.append(install_path)

# 2. ATTEMPT IMPORTS WITH CLEAN NAMES
try:
    from shortgpt.utils.utils import set_api_key
    from shortgpt.api_utils import upload_to_youtube
    from shortgpt.engine.facts_short_engine import FactsShortEngine
except ImportError:
    # If lowercase fails, try the casing from the repo
    try:
        from shortGPT.utils.utils import set_api_key
        from shortGPT.api_utils import upload_to_youtube
        from shortGPT.engine.facts_short_engine import FactsShortEngine
    except ImportError as e:
        print(f"CRITICAL ERROR: Could not find ShortGPT in {sys.path}")
        raise e

# 3. SETUP API KEYS
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))
set_api_key("PEXELS", os.getenv("PEXELS_API_KEY"))

# 4. PICK A NICHE
niches = ["Space Facts", "Deep Sea Mysteries", "Ancient History Secrets", "Future Tech"]
selected_niche = random.choice(niches)
print(f"--- Starting Generation for: {selected_niche} ---")

# 5. INITIALIZE ENGINE
content_engine = FactsShortEngine(
    facts_type=selected_niche,
    background_video_name="nature",
    num_images=0,
    watermark="MyBot"
)

# 6. GENERATE VIDEO
for step_num, step_logs in content_engine.makeContent():
    print(f"Step {step_num}: {step_logs}")

video_path = content_engine.get_video_output_path()

# 7. UPLOAD TO YOUTUBE
token_raw = os.getenv("YOUTUBE_TOKEN")
if token_raw:
    try:
        youtube_token_data = json.loads(token_raw)
        upload_to_youtube(
            video_path=video_path,
            title=f"{selected_niche} | AI Facts",
            description=f"Amazing facts about {selected_niche}! #shorts #ai",
            keywords=f"{selected_niche}, facts",
            privacy_status="public",
            token_data=youtube_token_data
        )
        print("Upload successful!")
    except Exception as e:
        print(f"Upload failed: {e}")
