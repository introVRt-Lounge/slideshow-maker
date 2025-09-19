#!/usr/bin/env python3
"""
Main slideshow orchestrator for the VRChat Slideshow Maker
"""

import os
import sys
import glob
import random
from .config import (
    DEFAULT_MIN_DURATION, DEFAULT_MAX_DURATION, MAX_SLIDES_LIMIT,
    AUDIO_OUTPUT, VIDEO_OUTPUT, FINAL_OUTPUT, IMAGE_EXTENSIONS
)
from .audio import find_audio_files, merge_audio, combine_video_audio, get_total_audio_duration
from .video import create_slideshow
from .utils import show_progress, print_ffmpeg_capabilities, detect_nvenc_support


def find_images(directory):
    """Find image files in the directory"""
    all_images = []
    for ext in IMAGE_EXTENSIONS:
        pattern = os.path.join(directory, ext)
        all_images.extend(glob.glob(pattern))
    return sorted(all_images)


def calculate_slides_needed(audio_duration, min_duration, max_duration, test_mode=False):
    """Calculate how many slides are needed based on audio duration or test mode"""
    if test_mode:
        # Test mode: 1 minute video
        test_duration = 60  # 1 minute
        slides_needed = int(test_duration / ((min_duration + max_duration) / 2))  # Use average duration
        print(f"🎵 Test mode: creating 1-minute video")
        print(f"⏱️  Slides needed for test: {slides_needed}")
        return slides_needed
    else:
        # Full mode: match audio duration
        avg_duration = (min_duration + max_duration) / 2
        slides_needed = int(audio_duration / avg_duration)
        print(f"🎵 Audio duration: {audio_duration:.1f} seconds")
        print(f"⏱️  Slides needed: {slides_needed} (avg {avg_duration:.1f}s per slide)")

        # No limits - process all slides for full duration!
        print(f"🚀 Processing ALL {slides_needed} slides for maximum content!")
        print(f"   Final video will be ~{slides_needed * avg_duration / 60:.1f} minutes")

        return slides_needed


def select_images(all_images, slides_needed, test_mode=False):
    """Select images for the slideshow based on mode and requirements"""
    if len(all_images) == 0:
        return []

    if test_mode:
        # Test mode: just use first N images
        images = all_images[:slides_needed]
        print(f"🎲 Test mode: Using first {len(images)} images")
        return images
    else:
        # Full mode: Use ALL images, then add random repeats to fill duration
        images = all_images.copy()
        remaining = slides_needed - len(images)
        if remaining > 0:
            print(f"🎲 Adding {remaining} random repeats to reach target duration...")
            for i in range(remaining):
                img = random.choice(all_images)
                images.append(img)

                # Show progress for the repeats
                if i % 100 == 0 or i == remaining - 1:
                    current_total = len(all_images) + i + 1
                    show_progress(current_total, slides_needed, img)

        print(f"🎲 Selected {len(images)} images ({len(all_images)} unique + {remaining} repeats)")
        return images


def create_slideshow_with_audio(image_dir, test_mode=False, dry_run=False, min_duration=DEFAULT_MIN_DURATION, 
                               max_duration=DEFAULT_MAX_DURATION, temp_dir=None):
    """Main function to create a complete slideshow with audio"""
    
    if not os.path.exists(image_dir):
        print(f"Directory not found: {image_dir}")
        return False

    print("🎬 VRChat Slideshow Creator")
    print(f"📁 Working directory: {image_dir}")
    print(f"⚙️  Test mode: {'ON (1-minute video)' if test_mode else 'OFF (full video)'}")
    print(f"⏱️  Image duration range: {min_duration}-{max_duration} seconds")
    
    # Early dry run check - before any heavy processing
    if dry_run:
        print("\n🔍 DRY RUN MODE - No processing will be performed")
        print("="*60)
        
        # Find audio files for duration calculation
        audio_files = find_audio_files(image_dir)
        print(f"🎵 Found {len(audio_files)} audio files: {[os.path.basename(f) for f in audio_files]}")
        
        if len(audio_files) == 0:
            print("❌ No audio files found!")
            return False
        
        # Calculate audio duration
        audio_output_path = os.path.join(image_dir, AUDIO_OUTPUT)
        if os.path.exists(audio_output_path):
            from .utils import get_audio_duration
            audio_duration = get_audio_duration(audio_output_path)
            print(f"🎵 Using existing merged audio: {AUDIO_OUTPUT}")
            print(f"   Duration: {audio_duration:.1f} seconds")
        else:
            audio_duration = get_total_audio_duration(audio_files)
            print(f"🎵 Audio duration: {audio_duration:.1f} seconds")
        
        # Find images
        all_images = find_images(image_dir)
        print(f"🖼️  Found {len(all_images)} total images")
        
        # Calculate slides needed
        slides_needed = calculate_slides_needed(audio_duration, min_duration, max_duration, test_mode)
        
        # Calculate estimated total duration
        avg_duration = (min_duration + max_duration) / 2
        estimated_duration = slides_needed * avg_duration
        
        print(f"\n📊 SUMMARY:")
        print(f"  📁 Directory: {image_dir}")
        print(f"  ⏱️  Image duration range: {min_duration}-{max_duration} seconds")
        print(f"  🎬 Total slides needed: {slides_needed}")
        print(f"  ⏱️  Estimated video duration: {estimated_duration/60:.1f} minutes ({estimated_duration:.1f} seconds)")
        print(f"  🎭 Transitions: All available transition types will be used randomly")
        print(f"  🚀 Encoding: Will detect GPU/CPU encoding capabilities")
        print(f"  📁 Output: {FINAL_OUTPUT}")
        print("="*60)
        print("✅ Dry run complete - use without --dry-run to process")
        return True
    
    # Check FFmpeg capabilities
    print("\n" + "="*50)
    print_ffmpeg_capabilities()
    print("="*50)

    # Find audio first (needed for duration calculation)
    audio_files = find_audio_files(image_dir)
    print(f"🎵 Found {len(audio_files)} audio files: {[os.path.basename(f) for f in audio_files]}")

    if len(audio_files) == 0:
        print("❌ No audio files found!")
        return False

    # Check if merged audio already exists
    if os.path.exists(AUDIO_OUTPUT):
        print(f"🎵 Using existing merged audio: {AUDIO_OUTPUT}")
        from .utils import get_audio_duration
        audio_duration = get_audio_duration(AUDIO_OUTPUT)
        print(f"   Duration: {audio_duration:.1f} seconds")
    else:
        # Calculate audio duration from source files
        audio_duration = get_total_audio_duration(audio_files)

    # Find images
    all_images = find_images(image_dir)
    print(f"🖼️  Found {len(all_images)} total images")

    # Calculate slides based on mode
    slides_needed = calculate_slides_needed(audio_duration, min_duration, max_duration, test_mode)

    # Select images based on mode
    images = select_images(all_images, slides_needed, test_mode)
    print(f"🖼️  Final image count: {len(images)}")


    # Process audio
    if not os.path.exists(AUDIO_OUTPUT):
        print("\n🎵 Processing audio...")
        if not merge_audio(audio_files, AUDIO_OUTPUT):
            print("❌ Audio processing failed!")
            return False
    else:
        print(f"\n🎵 Using existing merged audio: {AUDIO_OUTPUT}")

    # Create slideshow with variable durations
    print("\n🎬 Creating slideshow...")
    if not create_slideshow(images, VIDEO_OUTPUT, min_duration, max_duration, temp_dir=temp_dir):
        print("❌ Slideshow creation failed!")
        return False

    # Combine video and audio
    if test_mode:
        print("\n🎞️  Test mode: Combining with short audio clip...")
        # Create a short audio clip for testing (60 seconds) in the current directory
        test_audio = "test_audio_temp.m4a"
        cmd = f'ffmpeg -y -i "{AUDIO_OUTPUT}" -t 60 -c copy "{test_audio}"'
        from .utils import run_command
        if run_command(cmd, "Creating 60-second test audio clip"):
            if not combine_video_audio(VIDEO_OUTPUT, test_audio, FINAL_OUTPUT):
                print("❌ Test audio combination failed!")
                return False
            # Clean up test audio
            try:
                os.remove(test_audio)
            except:
                pass
        else:
            print("⚠️  Test audio creation failed, using video only")
            import shutil
            shutil.copy2(VIDEO_OUTPUT, FINAL_OUTPUT)
    else:
        print("\n🎞️  Combining video and audio...")
        if not combine_video_audio(VIDEO_OUTPUT, AUDIO_OUTPUT, FINAL_OUTPUT):
            print("❌ Final combination failed!")
            return False

    # Clean up intermediate files (but keep audio for reuse)
    print("\n🧹 Cleaning up intermediate files...")
    try:
        os.remove(VIDEO_OUTPUT)
    except:
        pass
    # DON'T remove AUDIO_OUTPUT - keep it for reuse!

    # Show result
    file_size = os.path.getsize(FINAL_OUTPUT) / (1024 * 1024)  # MB
    print("\n✅ SUCCESS!")
    print(f"🎬 Final video: {FINAL_OUTPUT}")
    print(f"📏 File size: {file_size:.1f} MB")
    
    return True
