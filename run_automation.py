import os
from shortGPT.api_utils import set_api_key
from shortGPT.engine.content_engine import ContentEngine

# 1. Setup Keys from GitHub Secrets
set_api_key("GEMINI", os.getenv("GEMINI_API_KEY"))

# 2. Define the video (You can change the topic here!)
topic = "Mind-blowing facts about the universe"

# 3. Run the engine (This avoids the GUI/Browser)
engine = ContentEngine(unit_id="short_video_1")
engine.create_content(
    topic=topic,
    voice="en_us_001", 
    export_path="output_video.mp4"
)

# 4. Upload to YouTube (Requires your YouTube Token)
# print("Uploading to YouTube...")
# upload_to_youtube("output_video.mp4", title=topic)
