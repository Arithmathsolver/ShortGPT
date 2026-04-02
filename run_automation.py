import os
import json
import random

# Flexible import to handle different ShortGPT versions
try:
    from shortGPT.utils.utils import set_api_key
except ImportError:
    try:
        from shortGPT.api_utils import set_api_key
    except ImportError:
        from shortgpt.utils.utils import set_api_key

from shortGPT.api_utils import upload_to_youtube
from shortGPT.engine.facts_short_engine import FactsShortEngine

# 1. Setup API Keys
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))
set_api_key("PEXELS", os.getenv("PEXELS_API_KEY")

# 2. Pick a niche
niches = ["Space Facts", "Deep Sea Mysteries", "Ancient History Secrets", "Future Tech"]
selected_niche = random.choice(niches)
print(f"--- Starting Generation for: {selected_niche} ---")

# 3. Initialize the Engine
content_engine = FactsShortEngine(
    facts_type=selected_niche,
    background_video_name="nature",
    num_images=0,
    watermark="MyAwesomeBot"
)

# 4. Generate the Video
for step_num, step_logs in content_engine.makeContent():
    print(f"Step {step_num}: {step_logs}")

video_path = content_engine.get_video_output_path()
print(f"Video created at: {video_path}")

# 5. Upload to YouTube (with safety check)
token_raw = os.getenv("YOUTUBE_TOKEN")
if token_raw:
    try:
        youtube_token_data = json.loads(token_raw)
        upload_to_youtube(
            video_path=video_path,
            title=f"{selected_niche} | Mind-Blowing Facts",
            description=f"Amazing facts about {selected_niche}! #shorts #facts #ai",
            keywords=f"{selected_niche}, facts, ai",
            privacy_status="public",
            token_data=youtube_token_data
        )
        print("Video successfully uploaded!")
    except Exception as e:
        print(f"Upload failed: {e}")
else:
    print("Error: YOUTUBE_TOKEN secret not found in GitHub!")
