#!/usr/bin/env python3
"""
Tests for FFmpeg capability detection
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.utils import (
    detect_ffmpeg_capabilities, get_available_transitions, print_ffmpeg_capabilities
)
from slideshow_maker.transitions import get_cpu_transitions, get_gpu_transitions


@pytest.mark.unit
class TestCapabilities:
    """Test FFmpeg capability detection"""
    
    def test_detect_ffmpeg_capabilities_structure(self):
        """Test that detect_ffmpeg_capabilities returns expected structure"""
        capabilities = detect_ffmpeg_capabilities()
        
        expected_keys = [
            'xfade_available', 'xfade_opencl_available', 'opencl_available',
            'gpu_transitions_supported', 'cpu_transitions_supported'
        ]
        
        for key in expected_keys:
            assert key in capabilities
            assert isinstance(capabilities[key], bool)
    
    def test_detect_ffmpeg_capabilities_cpu_success(self):
        """Test detect_ffmpeg_capabilities when CPU xfade is available"""
        with patch('subprocess.run') as mock_run:
            # Mock successful CPU xfade test
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            capabilities = detect_ffmpeg_capabilities()
            
            assert capabilities['xfade_available'] is True
            assert capabilities['cpu_transitions_supported'] is True
    
    def test_detect_ffmpeg_capabilities_gpu_success(self):
        """Test detect_ffmpeg_capabilities when GPU xfade is available"""
        with patch('subprocess.run') as mock_run:
            # Mock successful GPU xfade test
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            capabilities = detect_ffmpeg_capabilities()
            
            assert capabilities['xfade_opencl_available'] is True
            assert capabilities['gpu_transitions_supported'] is True
    
    def test_detect_ffmpeg_capabilities_opencl_success(self):
        """Test detect_ffmpeg_capabilities when OpenCL is available"""
        with patch('subprocess.run') as mock_run:
            # Mock successful OpenCL test
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            capabilities = detect_ffmpeg_capabilities()
            
            assert capabilities['opencl_available'] is True
    
    def test_detect_ffmpeg_capabilities_failure(self):
        """Test detect_ffmpeg_capabilities when FFmpeg is not available"""
        with patch('subprocess.run') as mock_run:
            # Mock failed commands
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result
            
            capabilities = detect_ffmpeg_capabilities()
            
            assert capabilities['xfade_available'] is False
            assert capabilities['xfade_opencl_available'] is False
            assert capabilities['opencl_available'] is False
            assert capabilities['gpu_transitions_supported'] is False
            assert capabilities['cpu_transitions_supported'] is False
    
    def test_get_available_transitions_cpu_only(self):
        """Test get_available_transitions when only CPU transitions are available"""
        with patch('slideshow_maker.utils.detect_ffmpeg_capabilities') as mock_detect:
            mock_detect.return_value = {
                'xfade_available': True,
                'xfade_opencl_available': False,
                'opencl_available': False,
                'gpu_transitions_supported': False,
                'cpu_transitions_supported': True
            }
            
            transitions, capabilities = get_available_transitions()
            
            assert capabilities['cpu_transitions_supported'] is True
            assert capabilities['gpu_transitions_supported'] is False
            assert len(transitions) > 0
            # Should only contain CPU transitions
            cpu_transitions = get_cpu_transitions()
            assert all(t in cpu_transitions for t in transitions)
    
    def test_get_available_transitions_gpu_only(self):
        """Test get_available_transitions when only GPU transitions are available"""
        with patch('slideshow_maker.utils.detect_ffmpeg_capabilities') as mock_detect:
            mock_detect.return_value = {
                'xfade_available': False,
                'xfade_opencl_available': True,
                'opencl_available': True,
                'gpu_transitions_supported': True,
                'cpu_transitions_supported': False
            }
            
            transitions, capabilities = get_available_transitions()
            
            assert capabilities['cpu_transitions_supported'] is False
            assert capabilities['gpu_transitions_supported'] is True
            assert len(transitions) > 0
            # Should only contain GPU transitions
            gpu_transitions = get_gpu_transitions()
            assert all(t in gpu_transitions for t in transitions)
    
    def test_get_available_transitions_both(self):
        """Test get_available_transitions when both CPU and GPU are available"""
        with patch('slideshow_maker.utils.detect_ffmpeg_capabilities') as mock_detect:
            mock_detect.return_value = {
                'xfade_available': True,
                'xfade_opencl_available': True,
                'opencl_available': True,
                'gpu_transitions_supported': True,
                'cpu_transitions_supported': True
            }
            
            transitions, capabilities = get_available_transitions()
            
            assert capabilities['cpu_transitions_supported'] is True
            assert capabilities['gpu_transitions_supported'] is True
            assert len(transitions) > 0
            
            # Should contain both CPU and GPU transitions
            cpu_transitions = get_cpu_transitions()
            gpu_transitions = get_gpu_transitions()
            expected_count = len(cpu_transitions) + len(gpu_transitions)
            assert len(transitions) == expected_count
    
    def test_get_available_transitions_none(self):
        """Test get_available_transitions when no transitions are available"""
        with patch('slideshow_maker.utils.detect_ffmpeg_capabilities') as mock_detect:
            mock_detect.return_value = {
                'xfade_available': False,
                'xfade_opencl_available': False,
                'opencl_available': False,
                'gpu_transitions_supported': False,
                'cpu_transitions_supported': False
            }
            
            transitions, capabilities = get_available_transitions()
            
            assert capabilities['cpu_transitions_supported'] is False
            assert capabilities['gpu_transitions_supported'] is False
            assert len(transitions) == 0
    
    def test_print_ffmpeg_capabilities(self, capsys):
        """Test print_ffmpeg_capabilities output"""
        with patch('slideshow_maker.utils.detect_ffmpeg_capabilities') as mock_detect:
            mock_detect.return_value = {
                'xfade_available': True,
                'xfade_opencl_available': False,
                'opencl_available': False,
                'gpu_transitions_supported': False,
                'cpu_transitions_supported': True
            }
            
            capabilities = print_ffmpeg_capabilities()
            captured = capsys.readouterr()
            
            assert "FFmpeg Capability Detection:" in captured.out
            assert "xfade filter (CPU)" in captured.out
            assert "xfade_opencl (GPU)" in captured.out
            assert "OpenCL support" in captured.out
            assert "CPU transitions" in captured.out
            assert "GPU transitions" in captured.out
            assert "Total transitions" in captured.out
            
            # Should return the capabilities dict
            assert capabilities['cpu_transitions_supported'] is True
    
    def test_print_ffmpeg_capabilities_warning(self, capsys):
        """Test print_ffmpeg_capabilities warning when no xfade support"""
        with patch('slideshow_maker.utils.detect_ffmpeg_capabilities') as mock_detect:
            mock_detect.return_value = {
                'xfade_available': False,
                'xfade_opencl_available': False,
                'opencl_available': False,
                'gpu_transitions_supported': False,
                'cpu_transitions_supported': False
            }
            
            print_ffmpeg_capabilities()
            captured = capsys.readouterr()
            
            assert "WARNING" in captured.out
            assert "No xfade support detected" in captured.out
            assert "Install FFmpeg" in captured.out
    
    def test_cpu_transitions_list(self):
        """Test that CPU transitions list is valid"""
        cpu_transitions = get_cpu_transitions()
        
        assert isinstance(cpu_transitions, list)
        assert len(cpu_transitions) > 0
        
        # Check for expected CPU transitions
        expected_cpu = ['fadeblack', 'fadewhite', 'circlecrop', 'dissolve', 'pixelize']
        for transition in expected_cpu:
            assert transition in cpu_transitions
    
    def test_gpu_transitions_list(self):
        """Test that GPU transitions list is valid"""
        gpu_transitions = get_gpu_transitions()
        
        assert isinstance(gpu_transitions, list)
        assert len(gpu_transitions) > 0
        
        # Check for expected GPU transitions
        expected_gpu = ['fade', 'wipeleft', 'wiperight', 'slideleft', 'slideright']
        for transition in expected_gpu:
            assert transition in gpu_transitions
    
    def test_transition_lists_no_overlap(self):
        """Test that CPU and GPU transition lists don't overlap"""
        cpu_transitions = get_cpu_transitions()
        gpu_transitions = get_gpu_transitions()
        
        # Should not have any overlapping transitions
        overlap = set(cpu_transitions) & set(gpu_transitions)
        assert len(overlap) == 0, f"Overlapping transitions found: {overlap}"
    
    def test_capability_detection_error_handling(self):
        """Test that capability detection handles errors gracefully"""
        with patch('subprocess.run') as mock_run:
            # Mock subprocess errors
            mock_run.side_effect = Exception("Test error")
            
            capabilities = detect_ffmpeg_capabilities()
            
            # Should return False for all capabilities when errors occur
            assert capabilities['xfade_available'] is False
            assert capabilities['xfade_opencl_available'] is False
            assert capabilities['opencl_available'] is False
            assert capabilities['gpu_transitions_supported'] is False
            assert capabilities['cpu_transitions_supported'] is False
