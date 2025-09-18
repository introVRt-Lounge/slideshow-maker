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

# COMPLETE FFMPEG XFADE TRANSITIONS - ALL 50+ AVAILABLE TYPES!
# Based on https://trac.ffmpeg.org/wiki/Xfade
TRANSITIONS = [
    # Basic fades
    'fade',         # Simple crossfade (default)
    'fadeblack',    # Fade through black
    'fadewhite',    # Fade through white
    'fadegrays',    # Fade through grayscale
    
    # Wipe effects
    'wipeleft',     # Wipe from left to right
    'wiperight',    # Wipe from right to left
    'wipeup',       # Wipe from bottom to top
    'wipedown',     # Wipe from top to bottom
    'wipetl',       # Wipe from top-left
    'wipetr',       # Wipe from top-right
    'wipebl',       # Wipe from bottom-left
    'wipebr',       # Wipe from bottom-right
    
    # Slide effects
    'slideleft',    # Slide from left
    'slideright',   # Slide from right
    'slideup',      # Slide from bottom
    'slidedown',    # Slide from top
    
    # Smooth effects
    'smoothleft',   # Smooth wipe from left
    'smoothright',  # Smooth wipe from right
    'smoothup',     # Smooth wipe from bottom
    'smoothdown',   # Smooth wipe from top
    
    # Circle effects
    'circlecrop',   # Circular crop transition
    'circleclose',  # Circle closing
    'circleopen',   # Circle opening
    
    # Rectangle effects
    'rectcrop',     # Rectangular crop transition
    
    # Horizontal/Vertical effects
    'horzclose',    # Horizontal close
    'horzopen',     # Horizontal open
    'vertclose',    # Vertical close
    'vertopen',     # Vertical open
    
    # Diagonal effects
    'diagbl',       # Diagonal bottom-left
    'diagbr',       # Diagonal bottom-right
    'diagtl',       # Diagonal top-left
    'diagtr',       # Diagonal top-right
    
    # Slice effects
    'hlslice',      # Horizontal left slice
    'hrslice',      # Horizontal right slice
    'vuslice',      # Vertical up slice
    'vdslice',      # Vertical down slice
    
    # Special effects
    'dissolve',     # Dissolve effect
    'pixelize',     # Pixelize effect
    'radial',       # Radial transition
    'hblur',        # Horizontal blur
    'distance',     # Distance effect
    
    # Squeeze effects
    'squeezev',     # Vertical squeeze
    'squeezeh',     # Horizontal squeeze
    
    # Zoom effects
    'zoomin',       # Zoom in transition
    
    # Wind effects
    'hlwind',       # Horizontal left wind
    'hrwind',       # Horizontal right wind
    'vuwind',       # Vertical up wind
    'vdwind',       # Vertical down wind
    
    # Cover effects
    'coverleft',    # Cover from left
    'coverright',   # Cover from right
    'coverup',      # Cover from bottom
    'coverdown',    # Cover from top
    
    # Reveal effects
    'revealleft',   # Reveal from left
    'revealright',  # Reveal from right
    'revealup',     # Reveal from bottom
    'revealdown',   # Reveal from top
]

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
