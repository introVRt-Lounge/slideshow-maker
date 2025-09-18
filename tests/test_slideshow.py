#!/usr/bin/env python3
"""
Tests for the main slideshow module
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.slideshow import (
    find_images, calculate_slides_needed, select_images, create_slideshow_with_audio
)


@pytest.mark.unit
class TestSlideshow:
    """Test main slideshow functionality"""
    
    def test_find_images_empty_directory(self, tmp_path):
        """Test find_images with empty directory"""
        images = find_images(str(tmp_path))
        assert images == []
    
    def test_find_images_with_image_files(self, tmp_path):
        """Test find_images with image files"""
        # Create test image files
        (tmp_path / "test1.png").write_bytes(b"fake png data")
        (tmp_path / "test2.jpg").write_bytes(b"fake jpg data")
        (tmp_path / "test3.jpeg").write_bytes(b"fake jpeg data")
        (tmp_path / "test4.txt").write_text("not image")
        
        images = find_images(str(tmp_path))
        assert len(images) == 3
        assert any("test1.png" in img for img in images)
        assert any("test2.jpg" in img for img in images)
        assert any("test3.jpeg" in img for img in images)
    
    def test_find_images_sorted(self, tmp_path):
        """Test that find_images returns sorted files"""
        # Create test image files with different names
        (tmp_path / "z_test.png").write_bytes(b"fake png data")
        (tmp_path / "a_test.png").write_bytes(b"fake png data")
        
        images = find_images(str(tmp_path))
        assert len(images) == 2
        assert images[0] < images[1]  # Should be sorted
    
    def test_calculate_slides_needed_test_mode(self):
        """Test calculate_slides_needed in test mode"""
        with patch('builtins.print') as mock_print:
            slides = calculate_slides_needed(120.0, 3, 5, test_mode=True)
            assert slides == 15  # 60 seconds / 4 seconds average = 15 slides
            mock_print.assert_called()
    
    def test_calculate_slides_needed_full_mode(self):
        """Test calculate_slides_needed in full mode"""
        with patch('builtins.print') as mock_print:
            slides = calculate_slides_needed(120.0, 3, 5, test_mode=False)
            assert slides == 30  # 120 seconds / 4 seconds average = 30 slides
            mock_print.assert_called()
    
    def test_calculate_slides_needed_max_limit(self):
        """Test calculate_slides_needed respects max limit"""
        with patch('builtins.print') as mock_print:
            # Very long audio duration should be limited
            slides = calculate_slides_needed(10000.0, 3, 5, test_mode=False)
            assert slides == 2000  # Should be limited to MAX_SLIDES_LIMIT
            mock_print.assert_called()
    
    def test_select_images_empty_list(self):
        """Test select_images with empty list"""
        images = select_images([], 10, test_mode=False)
        assert images == []
    
    def test_select_images_test_mode(self, tmp_path):
        """Test select_images in test mode"""
        test_images = []
        for i in range(10):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        selected = select_images(test_images, 5, test_mode=True)
        assert len(selected) == 5
        assert selected == test_images[:5]  # Should take first 5
    
    def test_select_images_full_mode_no_repeats(self, tmp_path):
        """Test select_images in full mode with no repeats needed"""
        test_images = []
        for i in range(10):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        selected = select_images(test_images, 10, test_mode=False)
        assert len(selected) == 10
        assert selected == test_images  # Should use all images
    
    def test_select_images_full_mode_with_repeats(self, tmp_path):
        """Test select_images in full mode with repeats needed"""
        test_images = []
        for i in range(3):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        with patch('slideshow_maker.utils.show_progress'):
            selected = select_images(test_images, 10, test_mode=False)
            assert len(selected) == 10
            assert len(set(selected)) == 3  # Should have 3 unique images
            # All original images should be present
            for img in test_images:
                assert img in selected
    
    def test_create_slideshow_with_audio_nonexistent_directory(self):
        """Test create_slideshow_with_audio with nonexistent directory"""
        with patch('builtins.print') as mock_print:
            result = create_slideshow_with_audio("/nonexistent/directory")
            assert result is False
            mock_print.assert_called_with("Directory not found: /nonexistent/directory")
    
    def test_create_slideshow_with_audio_no_audio_files(self, tmp_path):
        """Test create_slideshow_with_audio with no audio files"""
        # Create image files but no audio
        (tmp_path / "test.png").write_bytes(b"fake png data")
        
        with patch('slideshow_maker.audio.find_audio_files') as mock_find_audio:
            mock_find_audio.return_value = []
            
            with patch('builtins.print') as mock_print:
                result = create_slideshow_with_audio(str(tmp_path))
                assert result is False
                mock_print.assert_called_with("❌ No audio files found!")
    
    def test_create_slideshow_with_audio_success(self, tmp_path):
        """Test create_slideshow_with_audio successful execution"""
        # Create test files
        (tmp_path / "test.png").write_bytes(b"fake png data")
        (tmp_path / "test.mp3").write_bytes(b"fake mp3 data")
        
        with patch('slideshow_maker.audio.find_audio_files') as mock_find_audio:
            mock_find_audio.return_value = [str(tmp_path / "test.mp3")]
            
            with patch('slideshow_maker.audio.get_total_audio_duration') as mock_duration:
                mock_duration.return_value = 120.0
                
                with patch('slideshow_maker.slideshow.find_images') as mock_find_images:
                    mock_find_images.return_value = [str(tmp_path / "test.png")]
                    
                    with patch('slideshow_maker.audio.merge_audio') as mock_merge:
                        mock_merge.return_value = True
                        
                        with patch('slideshow_maker.video.create_slideshow') as mock_create:
                            mock_create.return_value = True
                            
                            with patch('slideshow_maker.audio.combine_video_audio') as mock_combine:
                                mock_combine.return_value = True
                                
                                with patch('builtins.print'):
                                    with patch('os.path.exists') as mock_exists:
                                        mock_exists.return_value = False  # No existing files
                                        
                                        result = create_slideshow_with_audio(str(tmp_path))
                                        assert result is True
    
    def test_create_slideshow_with_audio_audio_processing_failure(self, tmp_path):
        """Test create_slideshow_with_audio when audio processing fails"""
        # Create test files
        (tmp_path / "test.png").write_bytes(b"fake png data")
        (tmp_path / "test.mp3").write_bytes(b"fake mp3 data")
        
        with patch('slideshow_maker.audio.find_audio_files') as mock_find_audio:
            mock_find_audio.return_value = [str(tmp_path / "test.mp3")]
            
            with patch('slideshow_maker.audio.get_total_audio_duration') as mock_duration:
                mock_duration.return_value = 120.0
                
                with patch('slideshow_maker.slideshow.find_images') as mock_find_images:
                    mock_find_images.return_value = [str(tmp_path / "test.png")]
                    
                    with patch('slideshow_maker.audio.merge_audio') as mock_merge:
                        mock_merge.return_value = False  # Audio processing fails
                        
                        with patch('builtins.print') as mock_print:
                            with patch('os.path.exists') as mock_exists:
                                mock_exists.return_value = False
                                
                                result = create_slideshow_with_audio(str(tmp_path))
                                assert result is False
                                mock_print.assert_called_with("❌ Audio processing failed!")
    
    def test_create_slideshow_with_audio_video_creation_failure(self, tmp_path):
        """Test create_slideshow_with_audio when video creation fails"""
        # Create test files
        (tmp_path / "test.png").write_bytes(b"fake png data")
        (tmp_path / "test.mp3").write_bytes(b"fake mp3 data")
        
        with patch('slideshow_maker.audio.find_audio_files') as mock_find_audio:
            mock_find_audio.return_value = [str(tmp_path / "test.mp3")]
            
            with patch('slideshow_maker.audio.get_total_audio_duration') as mock_duration:
                mock_duration.return_value = 120.0
                
                with patch('slideshow_maker.slideshow.find_images') as mock_find_images:
                    mock_find_images.return_value = [str(tmp_path / "test.png")]
                    
                    with patch('slideshow_maker.audio.merge_audio') as mock_merge:
                        mock_merge.return_value = True
                        
                        with patch('slideshow_maker.video.create_slideshow') as mock_create:
                            mock_create.return_value = False  # Video creation fails
                            
                            with patch('builtins.print') as mock_print:
                                with patch('os.path.exists') as mock_exists:
                                    mock_exists.return_value = False
                                    
                                    result = create_slideshow_with_audio(str(tmp_path))
                                    assert result is False
                                    mock_print.assert_called_with("❌ Slideshow creation failed!")
    
    def test_create_slideshow_with_audio_existing_audio_file(self, tmp_path):
        """Test create_slideshow_with_audio with existing audio file"""
        # Create test files
        (tmp_path / "test.png").write_bytes(b"fake png data")
        (tmp_path / "test.mp3").write_bytes(b"fake mp3 data")
        (tmp_path / "audio_merged.m4a").write_bytes(b"existing audio")
        
        with patch('slideshow_maker.audio.find_audio_files') as mock_find_audio:
            mock_find_audio.return_value = [str(tmp_path / "test.mp3")]
            
            with patch('slideshow_maker.utils.get_audio_duration') as mock_duration:
                mock_duration.return_value = 120.0
                
                with patch('slideshow_maker.slideshow.find_images') as mock_find_images:
                    mock_find_images.return_value = [str(tmp_path / "test.png")]
                    
                    with patch('slideshow_maker.video.create_slideshow') as mock_create:
                        mock_create.return_value = True
                        
                        with patch('slideshow_maker.audio.combine_video_audio') as mock_combine:
                            mock_combine.return_value = True
                            
                            with patch('builtins.print'):
                                with patch('os.path.exists') as mock_exists:
                                    def exists_side_effect(path):
                                        return path == str(tmp_path / "audio_merged.m4a")
                                    mock_exists.side_effect = exists_side_effect
                                    
                                    result = create_slideshow_with_audio(str(tmp_path))
                                    assert result is True
                                    
                                    # Should not call merge_audio since file exists
                                    # (This is tested indirectly through the successful result)
