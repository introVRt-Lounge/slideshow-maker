#!/usr/bin/env python3
"""
Video processing facade for the VRChat Slideshow Maker.

Thin module that re-exports implementations from:
- video_fixed.py
- video_transitions.py
- video_chunked.py
"""
from __future__ import annotations

# Re-export all video processing functions from specialized modules
from .video_chunked import get_encoding_params, create_slideshow, create_slideshow_chunked
from .video_fixed import create_slideshow_with_durations
from .video_transitions import create_beat_aligned_with_transitions

# Public API stays the same via re-exports
__all__ = [
    'get_encoding_params',
    'create_slideshow',
    'create_slideshow_chunked',
    'create_slideshow_with_durations',
    'create_beat_aligned_with_transitions'
]
