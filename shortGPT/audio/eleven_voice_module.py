import os
from shortGPT.audio.voice_module import VoiceModule
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule

class ElevenLabsVoiceModule(VoiceModule):
    def __init__(self, api_key=None, voiceName=None, checkElevenCredits=False):
        # 🎯 FORCE THE EDGETTS BACKEND INSTANTLY
        self.voiceName = os.getenv("SHORTGPT_VOICE", "en-US-ChristopherNeural")
        print(f"\n🛡️ [ROOT OVERRIDE]: Bypassing ElevenLabs credit walls completely.")
        print(f"🔄 ROUTING TO FREE EDGETTS LAYER: Using voice profile '{self.voiceName}'")
        
        # Initialize the free EdgeTTS module internally
        self.edge_backend = EdgeTTSVoiceModule(voiceName=self.voiceName)
        
        # Fake standard properties to keep the engine from raising errors
        self.api_key = "bypassed_free_tier"
        self.remaining_credits = 999999
        super().__init__()

    def update_usage(self):
        self.remaining_credits = 999999
        return self.remaining_credits

    def get_remaining_characters(self):
        return 999999

    def generate_voice(self, text, outputfile):
        # Pass the task over to the free EdgeTTS engine
        print(f"🎙️ Generating voice via EdgeTTS module for text chunk length: {len(text)}")
        return self.edge_backend.generate_voice(text, outputfile)
