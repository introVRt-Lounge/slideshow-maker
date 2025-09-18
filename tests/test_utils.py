#!/usr/bin/env python3
"""
Tests for the utils module
"""

import pytest
import sys
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.utils import (
    get_image_info, show_progress, run_command, get_audio_duration
)


@pytest.mark.unit
class TestUtils:
    """Test utility functions"""
    
    def test_get_image_info_with_nonexistent_file(self):
        """Test get_image_info with nonexistent file"""
        info = get_image_info("nonexistent_file.png")
        assert isinstance(info, str)
        assert "nonexistent_file.png" in info
    
    def test_get_image_info_with_valid_file(self, tmp_path):
        """Test get_image_info with a valid file"""
        # Create a temporary image file
        test_image = tmp_path / "test.png"
        test_image.write_bytes(b"fake png data")
        
        with patch('subprocess.run') as mock_run:
            # Mock successful identify command
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "📏 1920x1080 📷 RGB 🎨 3"
            mock_run.return_value = mock_result
            
            info = get_image_info(str(test_image))
            assert isinstance(info, str)
            assert "1920x1080" in info
    
    def test_get_image_info_fallback_to_file(self, tmp_path):
        """Test get_image_info fallback to file command"""
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with patch('subprocess.run') as mock_run:
            # Mock failed identify command
            mock_result_identify = MagicMock()
            mock_result_identify.returncode = 1
            mock_run.side_effect = [
                mock_result_identify,  # First call (identify) fails
                MagicMock(returncode=0, stdout="test.txt: ASCII text")  # Second call (file) succeeds
            ]
            
            info = get_image_info(str(test_file))
            assert isinstance(info, str)
            assert "test.txt" in info
    
    def test_show_progress_basic(self, capsys):
        """Test show_progress basic functionality"""
        show_progress(5, 10)
        captured = capsys.readouterr()
        assert "Progress:" in captured.out
        assert "50.0%" in captured.out
        assert "5/10" in captured.out
    
    def test_show_progress_with_image_and_transition(self, capsys):
        """Test show_progress with image and transition info"""
        with patch('slideshow_maker.utils.get_image_info') as mock_get_info:
            mock_get_info.return_value = "📏 1920x1080 📷 RGB 🎨 3"
            
            show_progress(3, 10, "test.png", "fade")
            captured = capsys.readouterr()
            assert "Processing:" in captured.out
            assert "Transition:" in captured.out
            assert "fade" in captured.out
    
    def test_run_command_success(self):
        """Test run_command with successful command"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = run_command("echo test", "Test command")
            assert result is True
            mock_run.assert_called_once()
    
    def test_run_command_failure(self):
        """Test run_command with failed command"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "test")
            
            result = run_command("false", "Test command")
            assert result is False
    
    def test_run_command_with_output(self, capsys):
        """Test run_command with show_output=True"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = run_command("echo test", "Test command", show_output=True)
            captured = capsys.readouterr()
            assert "⚡ Test command" in captured.out
            assert result is True
    
    def test_get_audio_duration_success(self):
        """Test get_audio_duration with successful command"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "120.5\n"
            mock_run.return_value = mock_result
            
            duration = get_audio_duration("test.mp3")
            assert duration == 120.5
    
    def test_get_audio_duration_failure(self):
        """Test get_audio_duration with failed command"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result
            
            duration = get_audio_duration("nonexistent.mp3")
            assert duration == 0.0
    
    def test_get_audio_duration_invalid_output(self):
        """Test get_audio_duration with invalid output"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "invalid duration\n"
            mock_run.return_value = mock_result
            
            duration = get_audio_duration("test.mp3")
            assert duration == 0.0
    
    def test_show_progress_percentage_calculation(self, capsys):
        """Test show_progress percentage calculation"""
        # Test 0%
        show_progress(0, 10)
        captured = capsys.readouterr()
        assert "0.0%" in captured.out
        
        # Test 100%
        show_progress(10, 10)
        captured = capsys.readouterr()
        assert "100.0%" in captured.out
        
        # Test 50%
        show_progress(5, 10)
        captured = capsys.readouterr()
        assert "50.0%" in captured.out
    
    def test_show_progress_progress_bar(self, capsys):
        """Test show_progress progress bar visualization"""
        # Test empty progress bar
        show_progress(0, 10)
        captured = capsys.readouterr()
        assert "░░░░░░░░░░░░░░░░░░░░" in captured.out
        
        # Test full progress bar
        show_progress(10, 10)
        captured = capsys.readouterr()
        assert "████████████████████" in captured.out
        
        # Test partial progress bar
        show_progress(5, 10)
        captured = capsys.readouterr()
        assert "██████████░░░░░░░░░░" in captured.out
