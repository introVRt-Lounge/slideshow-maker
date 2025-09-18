#!/usr/bin/env python3
"""
Tests for the audio module
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.audio import (
    find_audio_files, merge_audio, combine_video_audio, get_total_audio_duration
)


@pytest.mark.unit
class TestAudio:
    """Test audio processing functions"""
    
    def test_find_audio_files_empty_directory(self, tmp_path):
        """Test find_audio_files with empty directory"""
        audio_files = find_audio_files(str(tmp_path))
        assert audio_files == []
    
    def test_find_audio_files_with_audio_files(self, tmp_path):
        """Test find_audio_files with audio files"""
        # Create test audio files
        (tmp_path / "test1.mp3").write_bytes(b"fake mp3 data")
        (tmp_path / "test2.m4a").write_bytes(b"fake m4a data")
        (tmp_path / "test3.wav").write_bytes(b"fake wav data")
        (tmp_path / "test4.txt").write_text("not audio")
        
        audio_files = find_audio_files(str(tmp_path))
        assert len(audio_files) == 2  # Should return max 2 files
        assert any("test1.mp3" in f for f in audio_files)
        assert any("test2.m4a" in f for f in audio_files)
    
    def test_find_audio_files_sorted(self, tmp_path):
        """Test that find_audio_files returns sorted files"""
        # Create test audio files with different names
        (tmp_path / "z_test.mp3").write_bytes(b"fake mp3 data")
        (tmp_path / "a_test.mp3").write_bytes(b"fake mp3 data")
        
        audio_files = find_audio_files(str(tmp_path))
        assert len(audio_files) == 2
        assert audio_files[0] < audio_files[1]  # Should be sorted
    
    def test_merge_audio_no_files(self):
        """Test merge_audio with no audio files"""
        with patch('builtins.print') as mock_print:
            result = merge_audio([], "output.m4a")
            assert result is False
            mock_print.assert_called_with("No audio files found!")
    
    def test_merge_audio_single_file(self, tmp_path):
        """Test merge_audio with single audio file"""
        test_audio = tmp_path / "test.mp3"
        test_audio.write_bytes(b"fake mp3 data")
        output_file = tmp_path / "output.m4a"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            result = merge_audio([str(test_audio)], str(output_file))
            assert result is True
            mock_run.assert_called_once()
            # Check that the command contains the expected elements
            call_args = mock_run.call_args[0]
            assert "ffmpeg" in call_args[0]
            assert "test.mp3" in call_args[0]
            assert "output.m4a" in call_args[0]
    
    def test_merge_audio_multiple_files(self, tmp_path):
        """Test merge_audio with multiple audio files"""
        test_audio1 = tmp_path / "test1.mp3"
        test_audio2 = tmp_path / "test2.mp3"
        test_audio1.write_bytes(b"fake mp3 data")
        test_audio2.write_bytes(b"fake mp3 data")
        output_file = tmp_path / "output.m4a"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            result = merge_audio([str(test_audio1), str(test_audio2)], str(output_file))
            assert result is True
            # Should be called twice: once for the concat file creation, once for ffmpeg
            assert mock_run.call_count == 1
    
    def test_merge_audio_command_failure(self, tmp_path):
        """Test merge_audio when command fails"""
        test_audio = tmp_path / "test.mp3"
        test_audio.write_bytes(b"fake mp3 data")
        output_file = tmp_path / "output.m4a"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = False
            
            result = merge_audio([str(test_audio)], str(output_file))
            assert result is False
    
    def test_combine_video_audio_success(self, tmp_path):
        """Test combine_video_audio with successful operation"""
        video_file = tmp_path / "video.mp4"
        audio_file = tmp_path / "audio.m4a"
        output_file = tmp_path / "output.mp4"
        
        video_file.write_bytes(b"fake video data")
        audio_file.write_bytes(b"fake audio data")
        
        with patch('slideshow_maker.utils.get_audio_duration') as mock_duration:
            mock_duration.return_value = 120.5
            
            with patch('slideshow_maker.utils.run_command') as mock_run:
                mock_run.return_value = True
                
                result = combine_video_audio(str(video_file), str(audio_file), str(output_file))
                assert result is True
                mock_run.assert_called_once()
                # Check that the command contains expected elements
                call_args = mock_run.call_args[0]
                assert "ffmpeg" in call_args[0]
                assert "120.5" in call_args[0]
    
    def test_combine_video_audio_no_duration(self, tmp_path):
        """Test combine_video_audio when audio duration cannot be determined"""
        video_file = tmp_path / "video.mp4"
        audio_file = tmp_path / "audio.m4a"
        output_file = tmp_path / "output.mp4"
        
        video_file.write_bytes(b"fake video data")
        audio_file.write_bytes(b"fake audio data")
        
        with patch('slideshow_maker.utils.get_audio_duration') as mock_duration:
            mock_duration.return_value = 0.0
            
            with patch('builtins.print') as mock_print:
                result = combine_video_audio(str(video_file), str(audio_file), str(output_file))
                assert result is False
                mock_print.assert_called_with("Could not get audio duration")
    
    def test_get_total_audio_duration(self, tmp_path):
        """Test get_total_audio_duration"""
        audio1 = tmp_path / "audio1.mp3"
        audio2 = tmp_path / "audio2.mp3"
        audio1.write_bytes(b"fake audio data")
        audio2.write_bytes(b"fake audio data")
        
        with patch('slideshow_maker.utils.get_audio_duration') as mock_duration:
            mock_duration.side_effect = [60.0, 30.5]  # Different durations for each file
            
            total_duration = get_total_audio_duration([str(audio1), str(audio2)])
            assert total_duration == 90.5
            assert mock_duration.call_count == 2
    
    def test_get_total_audio_duration_empty_list(self):
        """Test get_total_audio_duration with empty list"""
        total_duration = get_total_audio_duration([])
        assert total_duration == 0.0
    
    def test_merge_audio_creates_concat_file(self, tmp_path):
        """Test that merge_audio creates and cleans up concat file"""
        test_audio1 = tmp_path / "test1.mp3"
        test_audio2 = tmp_path / "test2.mp3"
        test_audio1.write_bytes(b"fake mp3 data")
        test_audio2.write_bytes(b"fake mp3 data")
        output_file = tmp_path / "output.m4a"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            result = merge_audio([str(test_audio1), str(test_audio2)], str(output_file))
            assert result is True
            
            # Check that concat file was created and contains the right content
            concat_file = tmp_path / "audio_concat.txt"
            assert not concat_file.exists()  # Should be cleaned up
    
    def test_merge_audio_single_file_command_format(self, tmp_path):
        """Test that merge_audio formats single file command correctly"""
        test_audio = tmp_path / "test.mp3"
        test_audio.write_bytes(b"fake mp3 data")
        output_file = tmp_path / "output.m4a"
        
        with patch('slideshow_maker.utils.run_command') as mock_run:
            mock_run.return_value = True
            
            result = merge_audio([str(test_audio)], str(output_file))
            assert result is True
            
            # Check command format
            call_args = mock_run.call_args[0]
            command = call_args[0]
            assert "ffmpeg" in command
            assert "-y" in command
            assert f'-i "{test_audio}"' in command
            assert f'-c:a aac' in command
            assert f'-b:a 192k' in command
            assert f'"{output_file}"' in command
