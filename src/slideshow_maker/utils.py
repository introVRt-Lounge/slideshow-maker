#!/usr/bin/env python3
"""
Utility functions for the VRChat Slideshow Maker
"""

import os
import subprocess


def get_image_info(image_path):
    """Get basic info about an image"""
    try:
        # Use identify command (ImageMagick) if available
        cmd = f'identify -format "📏 %wx%h 📷 %[colorspace] 🎨 %[channels]" "{image_path}" 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    try:
        # Fallback to file command
        cmd = f'file "{image_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"📄 {result.stdout.strip()}"
    except:
        pass

    return f"🖼️ {os.path.basename(image_path)}"


def show_progress(current, total, image_path=None, transition=None):
    """Show progress with image info"""
    percentage = (current / total) * 100
    progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))

    status_line = f"🔄 Progress: [{progress_bar}] {percentage:.1f}% ({current}/{total})"

    if image_path and transition:
        # Show detailed info for transition processing
        image_info = get_image_info(image_path)
        print(f"\n{status_line}")
        print(f"  🎯 Processing: {image_info}")
        print(f"  ✨ Transition: {transition}")
    else:
        # Simple progress for other operations
        print(f"\r{status_line}", end="", flush=True)


def run_command(cmd, description="", show_output=False):
    """Run a command and return True if successful"""
    try:
        if show_output:
            print(f"⚡ {description}")
        else:
            print(f"⚙️  {description}", end="", flush=True)

        result = subprocess.run(cmd, shell=True, check=True, capture_output=not show_output, text=True)

        if not show_output:
            print(" ✅" if result.returncode == 0 else " ❌")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if show_output and e.output:
            print(f"Output: {e.output}")
        return False


def get_audio_duration(audio_file):
    """Get duration of an audio file in seconds"""
    try:
        cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_file}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return 0.0
