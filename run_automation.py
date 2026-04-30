import os
import sys
import json
import random

# ✅ Ensure repo path is available (safe for GitHub Actions)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ✅ CORRECT IMPORTS
from shortGPT.utils import set_api_key
from shortGPT.api_utils import upload_to_youtube
from shortGPT.engine.facts_short_engine import FactsShortEngine
from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule


# ✅ SETUP API KEYS (with validation)
gemini_key = os.getenv("GEMINI_API_KEY")
pexels_key = os.getenv("PEXELS_API_KEY")
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

if not gemini_key or not pexels_key or not elevenlabs_key:
    raise ValueError("❌ Missing API keys. Check GitHub Secrets.")

set_api_key("GEMINI", gemini_key)
set_api_key("PEXELS", pexels_key)


# ✅ PICK A NICHE
niches = [
    "Space Facts",
    "Deep Sea Mysteries",
    "Ancient History Secrets",
    "Future Tech"
]

selected_niche = random.choice(niches)
print(f"--- Starting Generation for: {selected_niche} ---")


# ✅ CREATE VOICE MODULE
voice_module = ElevenLabsVoiceModule(
    api_key=elevenlabs_key,
    voiceName="Rachel",          # replace with a valid ElevenLabs voice name
    checkElevenCredits=True      # ensures you have enough credits
)


# ✅ INITIALIZE ENGINE
content_engine = FactsShortEngine(
    voiceModule=voice_module,
    facts_type=selected_niche,
    background_video_name="nature",
    background_music_name="the_mountain-background-music-159125",   # <-- matches your uploaded file
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
