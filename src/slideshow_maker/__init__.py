#!/usr/bin/env python3
"""
VRChat Slideshow Maker

A powerful Python package that creates stunning slideshow videos from PNG images 
with smooth transitions, perfect for VRChat worlds and presentations.

Features:
- 50+ different transition types using FFmpeg xfade
- Audio processing and synchronization
- Variable image durations
- Chunked processing for reliability
- Text overlays showing transition names
"""

from .slideshow import create_slideshow_with_audio
from .transitions import (
    get_random_transition, get_transitions_by_category, get_transition_categories,
    get_transition_info, get_transition_description, get_all_transitions, get_transition_count
)
from .audio import find_audio_files, merge_audio, combine_video_audio, get_total_audio_duration
from .video import create_slideshow
from .beat_detection import detect_beats
from .beat_selection import select_beats
from .utils import get_image_info, show_progress, run_command, get_audio_duration
from .config import (
    TRANSITIONS, TRANSITION_CATEGORIES, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS,
    DEFAULT_MIN_DURATION, DEFAULT_MAX_DURATION, DEFAULT_TRANSITION_DURATION
)

__version__ = "2.0.0"
__author__ = "IntroVRt Lounge"
__description__ = "VRChat Slideshow Maker with 50+ transition effects"

__all__ = [
    'create_slideshow_with_audio',
    'get_random_transition', 'get_transitions_by_category', 'get_transition_categories',
    'get_transition_info', 'get_transition_description', 'get_all_transitions', 'get_transition_count',
    'find_audio_files', 'merge_audio', 'combine_video_audio', 'get_total_audio_duration',
    'create_slideshow', 'detect_beats', 'select_beats',
    'get_image_info', 'show_progress', 'run_command', 'get_audio_duration',
    'TRANSITIONS', 'TRANSITION_CATEGORIES', 'DEFAULT_WIDTH', 'DEFAULT_HEIGHT', 'DEFAULT_FPS',
    'DEFAULT_MIN_DURATION', 'DEFAULT_MAX_DURATION', 'DEFAULT_TRANSITION_DURATION'
]
