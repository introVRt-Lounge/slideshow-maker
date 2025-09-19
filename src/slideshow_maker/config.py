#!/usr/bin/env python3
"""
Configuration and constants for the VRChat Slideshow Maker
"""

# Video settings
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_FPS = 25
DEFAULT_CRF = 23
DEFAULT_PRESET = "ultrafast"

# Duration settings
DEFAULT_MIN_DURATION = 3
DEFAULT_MAX_DURATION = 5
DEFAULT_TRANSITION_DURATION = 1.0

# Beat-alignment defaults (Phase 1)
PERIOD_MIN_DEFAULT = 5.0
PERIOD_MAX_DEFAULT = 10.0
TARGET_PERIOD_DEFAULT = 7.5
GRACE_PERIOD_DEFAULT = 0.5
MIN_CUT_GAP_DEFAULT = (2 * DEFAULT_TRANSITION_DURATION) + 0.05

# Processing settings
DEFAULT_CHUNK_SIZE = 10
MAX_SLIDES_LIMIT = 2000

# Audio settings
AUDIO_BITRATE = "192k"
AUDIO_CODEC = "aac"

# File extensions
AUDIO_EXTENSIONS = ['*.mp3', '*.m4a', '*.wav', '*.flac', '*.ogg']
IMAGE_EXTENSIONS = ['*.png', '*.jpg', '*.jpeg']

# Output files
AUDIO_OUTPUT = "audio_merged.m4a"
VIDEO_OUTPUT = "slideshow_video.mp4"
FINAL_OUTPUT = "slideshow_with_audio.mp4"

# Temp directory - configurable for better performance
import tempfile
import os

def get_temp_dir(custom_temp_dir=None):
    """Get temp directory, with option to specify custom location"""
    if custom_temp_dir:
        return custom_temp_dir
    return os.path.join(tempfile.gettempdir(), "slideshow_maker")

# Default temp directory
TEMP_DIR = get_temp_dir()

# FFMPEG XFADE TRANSITIONS - CPU COMPATIBLE (No GPU Required)
# Based on https://trac.ffmpeg.org/wiki/Xfade
# These transitions work with standard xfade filter (no OpenCL/GPU required)
CPU_TRANSITIONS = [
    # Basic fades
    'fadeblack',    # Fade through black
    'fadewhite',    # Fade through white
    'fadegrays',    # Fade through grayscale
    
    # Wipe effects (corner wipes - CPU only)
    'wipetl',       # Wipe from top-left
    'wipetr',       # Wipe from top-right
    'wipebl',       # Wipe from bottom-left
    'wipebr',       # Wipe from bottom-right
    
    # Smooth effects (CPU only)
    'smoothleft',   # Smooth wipe from left
    'smoothright',  # Smooth wipe from right
    'smoothup',     # Smooth wipe from bottom
    'smoothdown',   # Smooth wipe from top
    
    # Circle effects (CPU only)
    'circlecrop',   # Circular crop transition
    'circleclose',  # Circle closing
    'circleopen',   # Circle opening
    
    # Rectangle effects
    'rectcrop',     # Rectangular crop transition
    
    # Horizontal/Vertical effects (CPU only)
    'horzclose',    # Horizontal close
    'horzopen',     # Horizontal open
    'vertclose',    # Vertical close
    'vertopen',     # Vertical open
    
    # Diagonal effects (CPU only)
    'diagbl',       # Diagonal bottom-left
    'diagbr',       # Diagonal bottom-right
    'diagtl',       # Diagonal top-left
    'diagtr',       # Diagonal top-right
    
    # Slice effects (CPU only)
    'hlslice',      # Horizontal left slice
    'hrslice',      # Horizontal right slice
    'vuslice',      # Vertical up slice
    'vdslice',      # Vertical down slice
    
    # Special effects (CPU only)
    'dissolve',     # Dissolve effect
    'pixelize',     # Pixelize effect
    'radial',       # Radial transition
    'hblur',        # Horizontal blur
    'distance',     # Distance effect
    
    # Squeeze effects (CPU only)
    'squeezev',     # Vertical squeeze
    'squeezeh',     # Horizontal squeeze
    
    # Zoom effects (CPU only)
    'zoomin',       # Zoom in transition
    
    # Wind effects (CPU only)
    'hlwind',       # Horizontal left wind
    'hrwind',       # Horizontal right wind
    'vuwind',       # Vertical up wind
    'vdwind',       # Vertical down wind
    
    # Cover effects (CPU only)
    'coverleft',    # Cover from left
    'coverright',   # Cover from right
    'coverup',      # Cover from bottom
    'coverdown',    # Cover from top
    
    # Reveal effects (CPU only)
    'revealleft',   # Reveal from left
    'revealright',  # Reveal from right
    'revealup',     # Reveal from bottom
    'revealdown',   # Reveal from top
]

# FFMPEG XFADE TRANSITIONS - GPU ACCELERATED (OpenCL Required)
# These transitions are marked as **bold** in the FFmpeg documentation
# and are available in xfade_opencl (requires OpenCL and compatible GPU)
GPU_TRANSITIONS = [
    # Basic fades (GPU accelerated)
    'fade',         # Simple crossfade (default) - **BOLD** in docs
    
    # Wipe effects (GPU accelerated)
    'wipeleft',     # Wipe from left to right - **BOLD** in docs
    'wiperight',    # Wipe from right to left - **BOLD** in docs
    'wipeup',       # Wipe from bottom to top - **BOLD** in docs
    'wipedown',     # Wipe from top to bottom - **BOLD** in docs
    
    # Slide effects (GPU accelerated)
    'slideleft',    # Slide from left - **BOLD** in docs
    'slideright',   # Slide from right - **BOLD** in docs
    'slideup',      # Slide from bottom - **BOLD** in docs
    'slidedown',    # Slide from top - **BOLD** in docs
]

# ALL TRANSITIONS (CPU + GPU)
# This combines both CPU and GPU transitions for maximum compatibility
TRANSITIONS = CPU_TRANSITIONS + GPU_TRANSITIONS

# Transition categories for organization
TRANSITION_CATEGORIES = {
    'basic_fades': ['fade', 'fadeblack', 'fadewhite', 'fadegrays'],
    'wipe_effects': ['wipeleft', 'wiperight', 'wipeup', 'wipedown', 'wipetl', 'wipetr', 'wipebl', 'wipebr'],
    'slide_effects': ['slideleft', 'slideright', 'slideup', 'slidedown'],
    'smooth_effects': ['smoothleft', 'smoothright', 'smoothup', 'smoothdown'],
    'circle_effects': ['circlecrop', 'circleclose', 'circleopen'],
    'rectangle_effects': ['rectcrop'],
    'horizontal_vertical': ['horzclose', 'horzopen', 'vertclose', 'vertopen'],
    'diagonal_effects': ['diagbl', 'diagbr', 'diagtl', 'diagtr'],
    'slice_effects': ['hlslice', 'hrslice', 'vuslice', 'vdslice'],
    'special_effects': ['dissolve', 'pixelize', 'radial', 'hblur', 'distance'],
    'squeeze_effects': ['squeezev', 'squeezeh'],
    'zoom_effects': ['zoomin'],
    'wind_effects': ['hlwind', 'hrwind', 'vuwind', 'vdwind'],
    'cover_effects': ['coverleft', 'coverright', 'coverup', 'coverdown'],
    'reveal_effects': ['revealleft', 'revealright', 'revealup', 'revealdown'],
}
