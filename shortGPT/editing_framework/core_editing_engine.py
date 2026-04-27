import os
import sys
import json
import random
import numpy as np
from typing import Any, Dict, List, Union

from urllib.error import HTTPError
from shortGPT.config.path_utils import get_program_path, handle_path

# ✅ Correct MoviePy imports
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    AudioClip
)
from moviepy.video.VideoClip import Clip
from moviepy.video import fx as vfx
from moviepy.audio import fx as afx

from shortGPT.editing_framework.rendering_logger import MoviepyProgressLogger
