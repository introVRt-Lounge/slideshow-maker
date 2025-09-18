#!/usr/bin/env python3
"""
Tests for the config module
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.config import (
    TRANSITIONS, TRANSITION_CATEGORIES, DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS,
    DEFAULT_CRF, DEFAULT_PRESET, DEFAULT_MIN_DURATION, DEFAULT_MAX_DURATION, 
    DEFAULT_TRANSITION_DURATION, DEFAULT_CHUNK_SIZE, MAX_SLIDES_LIMIT, AUDIO_BITRATE, 
    AUDIO_CODEC, AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, AUDIO_OUTPUT, VIDEO_OUTPUT, FINAL_OUTPUT
)


@pytest.mark.unit
class TestConfig:
    """Test configuration constants and values"""
    
    def test_transitions_not_empty(self):
        """Test that transitions list is not empty"""
        assert len(TRANSITIONS) > 0
        assert isinstance(TRANSITIONS, list)
    
    def test_transitions_contains_expected_types(self):
        """Test that transitions contain expected transition types"""
        expected_transitions = ['fade', 'wipeleft', 'wiperight', 'slideleft', 'circlecrop']
        for transition in expected_transitions:
            assert transition in TRANSITIONS
    
    def test_transitions_count(self):
        """Test that we have the expected number of transitions"""
        # Should have 50+ transitions based on FFmpeg xfade documentation
        assert len(TRANSITIONS) >= 50
    
    def test_transition_categories_not_empty(self):
        """Test that transition categories are not empty"""
        assert len(TRANSITION_CATEGORIES) > 0
        assert isinstance(TRANSITION_CATEGORIES, dict)
    
    def test_transition_categories_expected_keys(self):
        """Test that transition categories contain expected keys"""
        expected_categories = [
            'basic_fades', 'wipe_effects', 'slide_effects', 'smooth_effects',
            'circle_effects', 'rectangle_effects', 'horizontal_vertical',
            'diagonal_effects', 'slice_effects', 'special_effects',
            'squeeze_effects', 'zoom_effects', 'wind_effects',
            'cover_effects', 'reveal_effects'
        ]
        for category in expected_categories:
            assert category in TRANSITION_CATEGORIES
    
    def test_transition_categories_consistency(self):
        """Test that all transitions in categories are in the main transitions list"""
        all_categorized_transitions = []
        for transitions in TRANSITION_CATEGORIES.values():
            all_categorized_transitions.extend(transitions)
        
        for transition in all_categorized_transitions:
            assert transition in TRANSITIONS
    
    def test_video_settings(self):
        """Test video configuration values"""
        assert DEFAULT_WIDTH == 1920
        assert DEFAULT_HEIGHT == 1080
        assert DEFAULT_FPS == 25
        assert DEFAULT_CRF == 23
        assert DEFAULT_PRESET == "ultrafast"
    
    def test_duration_settings(self):
        """Test duration configuration values"""
        assert DEFAULT_MIN_DURATION == 3
        assert DEFAULT_MAX_DURATION == 5
        assert DEFAULT_TRANSITION_DURATION == 1.0
        assert MAX_SLIDES_LIMIT == 2000
    
    def test_processing_settings(self):
        """Test processing configuration values"""
        assert DEFAULT_CHUNK_SIZE == 10
    
    def test_audio_settings(self):
        """Test audio configuration values"""
        assert AUDIO_BITRATE == "192k"
        assert AUDIO_CODEC == "aac"
    
    def test_file_extensions(self):
        """Test file extension lists"""
        assert isinstance(AUDIO_EXTENSIONS, list)
        assert isinstance(IMAGE_EXTENSIONS, list)
        assert len(AUDIO_EXTENSIONS) > 0
        assert len(IMAGE_EXTENSIONS) > 0
        
        # Check for expected extensions
        assert '*.mp3' in AUDIO_EXTENSIONS
        assert '*.png' in IMAGE_EXTENSIONS
    
    def test_output_files(self):
        """Test output file names"""
        assert AUDIO_OUTPUT == "audio_merged.m4a"
        assert VIDEO_OUTPUT == "slideshow_video.mp4"
        assert FINAL_OUTPUT == "slideshow_with_audio.mp4"
    
    def test_transition_categories_coverage(self):
        """Test that all transitions are covered by categories"""
        all_categorized_transitions = []
        for transitions in TRANSITION_CATEGORIES.values():
            all_categorized_transitions.extend(transitions)
        
        # Remove duplicates
        all_categorized_transitions = list(set(all_categorized_transitions))
        
        # All categorized transitions should be in the main list
        for transition in all_categorized_transitions:
            assert transition in TRANSITIONS
        
        # Most transitions should be categorized (allow some uncategorized)
        assert len(all_categorized_transitions) >= len(TRANSITIONS) * 0.8
