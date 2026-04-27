import os
import json
import random
import subprocess
import sys

# --- FORCE INSTALLATION SECTION ---
def install_package(package):
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from shortgpt.utils.utils import set_api_key
    from shortgpt.api_utils import upload_to_youtube
    from shortgpt.engine.facts_short_engine import FactsShortEngine
except ImportError:
    # If the module is missing, we install it directly from the source
    install_package("git+https://github.com/RayVentura/ShortGPT.git")
    # Now try importing again
    from shortgpt.utils.utils import set_api_key
    from shortgpt.api_utils import upload_to_youtube
    from shortgpt.engine.facts_short_engine import FactsShortEngine

# 1. Setup API Keys
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))
set_api_key("PEXELS", os.getenv("PEXELS_API_KEY"))

# 2. Pick a niche
niches = ["Space Facts", "Deep Sea Mysteries", "Ancient History Secrets", "Future Tech"]
selected_niche = random.choice(niches)
print(f"--- Starting Generation for: {selected_niche} ---")

# 3. Initialize Engine
content_engine = FactsShortEngine(
    facts_type=selected_niche,
    background_video_name="nature",
    num_images=0,
    watermark="MyBot"
)

# 4. Generate Video
for step_num, step_logs in content_engine.makeContent():
    print(f"Step {step_num}: {step_logs}")

video_path = content_engine.get_video_output_path()

# 5. Upload to YouTube
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
else:
    print("Error: YOUTUBE_TOKEN secret not found!")
