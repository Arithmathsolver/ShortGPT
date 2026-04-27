import os
import sys
import json
import random

# ✅ Ensure current repo is in Python path (works locally + GitHub Actions)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ CLEAN IMPORT (ONLY ONE — no try/except mess)
from shortGPT.utils.utils import set_api_key
from shortGPT.api_utils import upload_to_youtube
from shortGPT.engine.facts_short_engine import FactsShortEngine


# ✅ SETUP API KEYS
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))
set_api_key("PEXELS", os.getenv("PEXELS_API_KEY"))


# ✅ PICK A NICHE
niches = [
    "Space Facts",
    "Deep Sea Mysteries",
    "Ancient History Secrets",
    "Future Tech"
]

selected_niche = random.choice(niches)
print(f"--- Starting Generation for: {selected_niche} ---")


# ✅ INITIALIZE ENGINE
content_engine = FactsShortEngine(
    facts_type=selected_niche,
    background_video_name="nature",
    num_images=0,
    watermark="MyBot"
)


# ✅ GENERATE VIDEO
for step_num, step_logs in content_engine.makeContent():
    print(f"Step {step_num}: {step_logs}")

video_path = content_engine.get_video_output_path()


# ✅ UPLOAD TO YOUTUBE
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

        print("✅ Upload successful!")

    except Exception as e:
        print(f"❌ Upload failed: {e}")
else:
    print("⚠️ No YOUTUBE_TOKEN found, skipping upload.")
