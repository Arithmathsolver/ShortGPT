import os
import sys
import json
import random

# --- 1. AUTO-LOCATION DISCOVERY ---
# This looks for the folder containing 'shortgpt' and 'engine'
repo_root = os.getcwd()
sys.path.append(repo_root)

# Check for the common 'shortgpt' subfolder structure
possible_paths = [
    repo_root,
    os.path.join(repo_root, 'shortgpt'),
    os.path.join(repo_root, 'ShortGPT'),
]

for path in possible_paths:
    if path not in sys.path:
        sys.path.append(path)

# Try every possible import combination
try:
    from shortgpt.utils.utils import set_api_key
    from shortgpt.api_utils import upload_to_youtube
    from shortgpt.engine.facts_short_engine import FactsShortEngine
except ImportError:
    try:
        from shortGPT.utils.utils import set_api_key
        from shortGPT.api_utils import upload_to_youtube
        from shortGPT.engine.facts_short_engine import FactsShortEngine
    except ImportError:
        try:
            # Relative imports if the folder is right there
            from utils.utils import set_api_key
            from api_utils import upload_to_youtube
            from engine.facts_short_engine import FactsShortEngine
        except ImportError:
            # Last ditch effort: search the whole repo for 'set_api_key'
            import importlib.util
            print("Searching for internal modules...")
            set_api_key = None
            for root, dirs, files in os.walk(repo_root):
                if 'utils.py' in files or 'set_api_key.py' in files:
                    sys.path.append(root)
                    print(f"Found tools in: {root}")
            # If we still can't find it, the repo might be empty or corrupted
            from shortgpt.utils.utils import set_api_key
            from shortgpt.api_utils import upload_to_youtube
            from shortgpt.engine.facts_short_engine import FactsShortEngine

# --- 2. SETUP API KEYS ---
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))
set_api_key("PEXELS", os.getenv("PEXELS_API_KEY"))

# --- 3. PICK A NICHE ---
niches = ["Space Facts", "Deep Sea Mysteries", "Ancient History Secrets", "Future Tech"]
selected_niche = random.choice(niches)
print(f"--- Starting Generation for: {selected_niche} ---")

# --- 4. INITIALIZE ENGINE ---
content_engine = FactsShortEngine(
    facts_type=selected_niche,
    background_video_name="nature",
    num_images=0,
    watermark="MyBot"
)

# --- 5. GENERATE VIDEO ---
for step_num, step_logs in content_engine.makeContent():
    print(f"Step {step_num}: {step_logs}")

video_path = content_engine.get_video_output_path()
print(f"Video created at: {video_path}")

# --- 6. UPLOAD TO YOUTUBE ---
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
