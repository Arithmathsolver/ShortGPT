from shortGPT.audio.voice_module import VoiceModule
from shortGPT.gpt import facts_gpt
from shortGPT.config.languages import Language
from shortGPT.engine.content_short_engine import ContentShortEngine

class FactsShortEngine(ContentShortEngine):

    def __init__(self, voiceModule: VoiceModule, facts_type: str, background_video_name: str = "", background_music_name: str = "", short_id="",
                 num_images=None, watermark=None, language: Language = Language.ENGLISH):
        
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

    def _timeCaptions(self):
        """
        Overriding caption timing to ensure float types are forced before rendering steps.
        """
        super()._timeCaptions()
        if hasattr(self, '_db_timed_captions') and self._db_timed_captions:
            try:
                self._db_timed_captions = [
                    [[float(t1), float(t2)], text] for (t1, t2), text in self._db_timed_captions
                ]
            except Exception as e:
                print(f"⚠️ Notice sanitizing typed captions: {e}")

    def _generateVideoUrls(self):
        """
        Overriding URL generation to ensure video block timestamps use native float wrappers.
        """
        super()._generateVideoUrls()
        if hasattr(self, '_db_timed_video_urls') and self._db_timed_video_urls:
            try:
                self._db_timed_video_urls = [
                    [[float(t1), float(t2)], url] for (t1, t2), url in self._db_timed_video_urls
                ]
            except Exception as e:
                print(f"⚠️ Notice sanitizing video tracking arrays: {e}")
