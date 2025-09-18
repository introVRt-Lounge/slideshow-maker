#!/usr/bin/env python3
"""
Audio processing for the VRChat Slideshow Maker
"""

import os
import glob
from .config import AUDIO_EXTENSIONS, AUDIO_OUTPUT, AUDIO_BITRATE, AUDIO_CODEC
from .utils import run_command, get_audio_duration


def find_audio_files(directory):
    """Find audio files in the directory, prioritizing Avicii files"""
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(glob.glob(os.path.join(directory, ext)))
    
    # Sort to prioritize Avicii files first
    audio_files = sorted(audio_files)
    avicii_files = [f for f in audio_files if 'avicii' in f.lower()]
    other_files = [f for f in audio_files if 'avicii' not in f.lower()]
    
    # Return Avicii files first, then others, up to 2 files total
    prioritized_files = avicii_files + other_files
    return prioritized_files[:2]


def merge_audio(audio_files, output_file):
    """Merge multiple audio files"""
    if len(audio_files) == 0:
        print("No audio files found!")
        return False

    if len(audio_files) == 1:
        # Single audio file - just copy/convert
        cmd = f'ffmpeg -y -i "{audio_files[0]}" -c:a {AUDIO_CODEC} -b:a {AUDIO_BITRATE} "{output_file}"'
        return run_command(cmd, f"Processing single audio file: {os.path.basename(audio_files[0])}")

    # Multiple audio files - concatenate
    concat_file = "audio_concat.txt"
    with open(concat_file, 'w') as f:
        for audio in audio_files:
            f.write(f"file '{audio}'\n")

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:a {AUDIO_CODEC} -b:a {AUDIO_BITRATE} "{output_file}"'
    success = run_command(cmd, f"Merging {len(audio_files)} audio files")

    # Clean up
    os.remove(concat_file)

    return success


def combine_video_audio(video_file, audio_file, output_file):
    """Combine video and audio"""
    # Get audio duration
    audio_duration = get_audio_duration(audio_file)
    if audio_duration == 0:
        print("Could not get audio duration")
        return False

    # Loop video to match audio duration
    cmd = f'ffmpeg -y -stream_loop -1 -i "{video_file}" -i "{audio_file}" -t {audio_duration} -c:v copy -c:a copy -shortest "{output_file}"'
    return run_command(cmd, f"Combining video and audio (duration: {audio_duration:.1f}s)")


def get_total_audio_duration(audio_files):
    """Calculate total duration from multiple audio files"""
    total_duration = 0
    for audio_file in audio_files:
        duration = get_audio_duration(audio_file)
        total_duration += duration
    return total_duration
