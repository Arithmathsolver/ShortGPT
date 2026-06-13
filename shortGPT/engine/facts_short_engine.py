from shortGPT.audio.voice_module import VoiceModule
from shortGPT.gpt import facts_gpt
from shortGPT.config.languages import Language
from shortGPT.engine.content_short_engine import ContentShortEngine

class FactsShortEngine(ContentShortEngine):

    def __init__(self, voiceModule: VoiceModule, facts_type: str, background_video_name: str = "", background_music_name: str = "", short_id="",
                 num_images=None, watermark=None, language:Language = Language.ENGLISH):
        
        # Force background music fields to None right from the initialization step
        super().__init__(short_id=short_id, short_type="facts_shorts", background_video_name=background_video_name, background_music_name=None,
                         num_images=num_images, watermark=watermark, language=language, voiceModule=voiceModule)
        
        self._db_facts_type = facts_type
        self._db_background_music_name = None
        self._db_background_music_url = None

    def _generateScript(self):
        """
        Implements Abstract parent method to generate the script for the Facts short.
        """
        self._db_script = facts_gpt.generateFacts(self._db_facts_type)

    def _chooseBackgroundMusic(self):
        """
        Hard-coded framework bypass to ensure Step 7 notice skips the SQLite check completely.
        """
        print("⏩ Custom File Notice: Background music lookup skipped explicitly.")
        self._db_background_music_url = None
        self._db_background_music_name = None
