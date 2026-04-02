import os
import random
from shortGPT.api_utils import set_api_key
from shortGPT.engine.facts_short_engine import FactsShortEngine

# 1. Setup API Keys from GitHub Secrets
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))
set_api_key("PEXELS", os.getenv("PEXELS_API_KEY"))

# 2. Pick a random niche for variety
niches = ["Space Facts", "Deep Sea Mysteries", "Ancient History Secrets", "Future Tech"]
selected_niche = random.choice(niches)

print(f"--- Starting Generation for: {selected_niche} ---")

# 3. Initialize the Engine
# We use 'edge_tts' because it's high quality and 100% free
content_engine = FactsShortEngine(
    facts_type=selected_niche,
    background_video_name="nature", # ShortGPT will find this on Pexels
    num_images=0, 
    watermark="MyAwesomeBot"
)

# 4. Generate the Video
for step_num, step_logs in content_engine.makeContent():
    print(f"Step {step_num}: {step_logs}")

video_path = content_engine.get_video_output_path()
print(f"Video created at: {video_path}")

# 5. TODO: Add your YouTube upload function here 
# (You'll need your token.json data for this part to work!)
