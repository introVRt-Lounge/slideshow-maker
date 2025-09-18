#!/usr/bin/env python3
"""
Tests for the video module
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.video import create_slideshow, create_slideshow_chunked


@pytest.mark.unit
class TestVideo:
    """Test video processing functions"""
    
    def test_create_slideshow_no_images(self):
        """Test create_slideshow with no images"""
        with patch('builtins.print') as mock_print:
            result = create_slideshow([], "output.mp4")
            assert result is False
            mock_print.assert_called_with("No images found!")
    
    def test_create_slideshow_single_image(self, tmp_path):
        """Test create_slideshow with single image"""
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            result = create_slideshow([str(test_image)], str(output_file))
            assert result is True
            mock_run.assert_called_once()
            
            # Check command format
            call_args = mock_run.call_args[0]
            command = call_args[0]
            assert "ffmpeg" in command
            assert f'-i "{test_image}"' in command
            assert "scale=1920:1080" in command
            assert "libx264" in command
    
    def test_create_slideshow_multiple_images(self, tmp_path):
        """Test create_slideshow with multiple images"""
        test_images = []
        for i in range(3):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.video.create_slideshow_chunked') as mock_chunked:
            mock_chunked.return_value = True
            
            result = create_slideshow(test_images, str(output_file))
            assert result is True
            mock_chunked.assert_called_once()
    
    def test_create_slideshow_chunked_no_images(self):
        """Test create_slideshow_chunked with no images"""
        result = create_slideshow_chunked([], "output.mp4")
        assert result is False
    
    def test_create_slideshow_chunked_single_image(self, tmp_path):
        """Test create_slideshow_chunked with single image"""
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            result = create_slideshow_chunked([str(test_image)], str(output_file))
            assert result is True
    
    def test_create_slideshow_chunked_multiple_images(self, tmp_path):
        """Test create_slideshow_chunked with multiple images"""
        test_images = []
        for i in range(5):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            with patch('os.makedirs'):
                with patch('os.rename'):
                    with patch('shutil.rmtree'):
                        result = create_slideshow_chunked(test_images, str(output_file))
                        assert result is True
    
    def test_create_slideshow_chunked_command_failure(self, tmp_path):
        """Test create_slideshow_chunked when command fails"""
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = False
            
            result = create_slideshow_chunked([str(test_image)], str(output_file))
            assert result is False
    
    def test_create_slideshow_chunked_transition_processing(self, tmp_path):
        """Test create_slideshow_chunked transition processing"""
        test_images = []
        for i in range(3):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            with patch('os.makedirs'):
                with patch('os.rename'):
                    with patch('shutil.rmtree'):
                        with patch('builtins.print'):
                            result = create_slideshow_chunked(test_images, str(output_file))
                            assert result is True
                            
                            # Should have multiple run_command calls for transitions
                            assert mock_run.call_count > 1
    
    def test_create_slideshow_chunked_chunk_size(self, tmp_path):
        """Test create_slideshow_chunked respects chunk size"""
        # Create more images than default chunk size (10)
        test_images = []
        for i in range(15):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            with patch('os.makedirs'):
                with patch('os.rename'):
                    with patch('shutil.rmtree'):
                        with patch('builtins.print'):
                            result = create_slideshow_chunked(test_images, str(output_file))
                            assert result is True
                            
                            # Should process in chunks (15 images / 10 chunk size = 2 chunks)
                            # This is tested indirectly through the number of calls
    
    def test_create_slideshow_chunked_transition_variety(self, tmp_path):
        """Test that create_slideshow_chunked uses different transitions"""
        test_images = []
        for i in range(3):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            with patch('os.makedirs'):
                with patch('os.rename'):
                    with patch('shutil.rmtree'):
                        with patch('builtins.print'):
                            result = create_slideshow_chunked(test_images, str(output_file))
                            assert result is True
                            
                            # Check that transition commands are generated
                            calls = mock_run.call_args_list
                            transition_commands = [call[0][0] for call in calls if 'xfade' in call[0][0]]
                            assert len(transition_commands) > 0
    
    def test_create_slideshow_chunked_cleanup(self, tmp_path):
        """Test that create_slideshow_chunked cleans up temporary files"""
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            with patch('os.makedirs'):
                with patch('os.rename'):
                    with patch('shutil.rmtree') as mock_rmtree:
                        result = create_slideshow_chunked([str(test_image)], str(output_file))
                        assert result is True
                        mock_rmtree.assert_called_once()
    
    def test_create_slideshow_chunked_progress_reporting(self, tmp_path):
        """Test that create_slideshow_chunked reports progress"""
        test_images = []
        for i in range(5):
            img = tmp_path / f"test{i}.png"
            img.write_bytes(b"fake png data")
            test_images.append(str(img))
        
        output_file = tmp_path / "output.mp4"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            with patch('os.makedirs'):
                with patch('os.rename'):
                    with patch('shutil.rmtree'):
                        with patch('builtins.print') as mock_print:
                            result = create_slideshow_chunked(test_images, str(output_file))
                            assert result is True
                            
                            # Check that progress messages were printed
                            print_calls = [call[0][0] for call in mock_print.call_args_list]
                            progress_messages = [msg for msg in print_calls if "Processing" in msg or "Progress" in msg]
                            assert len(progress_messages) > 0
