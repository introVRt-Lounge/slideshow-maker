#!/usr/bin/env python3
"""
Simple VRChat Slideshow Creator
Creates a slideshow from PNG images with audio, much simpler than complex FFmpeg scripting.
Usage: python3 slideshow.py [image_directory]
"""

import os
import sys
import glob
import random
import subprocess
import shutil
from pathlib import Path

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

def find_audio_files(directory):
    """Find audio files in the directory"""
    audio_extensions = ['*.mp3', '*.m4a', '*.wav', '*.flac', '*.ogg']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(directory, ext)))
    return sorted(audio_files)[:2]  # Return up to 2 files

def create_slideshow(images, output_file, min_duration=3, max_duration=5, width=1920, height=1080, fps=25):
    """Create slideshow video from images with smooth transitions using FFmpeg xfade"""

    if len(images) == 0:
        print("No images found!")
        return False

    if len(images) == 1:
        # Single image - just create a video with random duration
        duration = random.uniform(min_duration, max_duration)
        cmd = f'ffmpeg -y -loop 1 -i "{images[0]}" -t {duration:.1f} -vf "scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -r {fps} "{output_file}"'
        return run_command(cmd, f"Creating single image video from {images[0]}")

    print(f"🎬 Creating slideshow with {len(images)} images and smooth transitions...")

    # Use chunked approach with crossfades between chunks
    return create_slideshow_chunked(images, output_file, min_duration, max_duration, width, height, fps)

def create_slideshow_chunked(images, output_file, min_duration=3, max_duration=5, width=1920, height=1080, fps=25):
    """Create slideshow in very small chunks for reliability with VARIED transitions"""
    # Use much smaller chunks to avoid FFmpeg complexity limits
    chunk_size = 10  # Much smaller chunks
    temp_dir = "temp_chunks"
    os.makedirs(temp_dir, exist_ok=True)

    # COMPLETE FFMPEG XFADE TRANSITIONS - ALL 50+ AVAILABLE TYPES!
    # Based on https://trac.ffmpeg.org/wiki/Xfade
    transitions = [
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

    chunk_files = []

    print(f"📦 Processing {len(images)} images in chunks of {chunk_size}")
    print(f"🎭 Using ALL {len(transitions)} FFmpeg xfade transition types for MAXIMUM variety!")
    print(f"✨ Transitions include: fades, wipes, slides, circles, diagonals, slices, wind effects, and more!")

    # Process images in very small chunks
    for chunk_idx, chunk_start in enumerate(range(0, len(images), chunk_size)):
        chunk = images[chunk_start:chunk_start + chunk_size]
        chunk_file = f"{temp_dir}/chunk_{chunk_idx:03d}.mp4"

        print(f"  🔄 Processing chunk {chunk_idx + 1}/{(len(images) + chunk_size - 1) // chunk_size}")

        # Create simple concatenation without complex transitions
        # This is much more reliable than complex xfade chains
        temp_clips = []

        for i, img in enumerate(chunk):
            temp_clip = f"{temp_dir}/temp_{chunk_idx}_{i}.mp4"
            # Use variable duration for this image
            duration = random.uniform(min_duration, max_duration)

            # Show progress with image info
            if i % 2 == 0 or i == len(chunk) - 1:  # Show every other image or last one
                image_info = get_image_info(img)
                print(f"  📸 Processing: {image_info} ({duration:.1f}s)")

            # Simple scaling and padding - crossfades will be added between clips
            vf_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"

            cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration:.1f} -vf "{vf_filter}" -c:v libx264 -r {fps} -crf 23 -preset ultrafast "{temp_clip}"'
            if not run_command(cmd, f"    Creating image {i+1}/{len(chunk)}", show_output=False):
                return False
            temp_clips.append(temp_clip)

        # Create VARIED transitions between ALL images in this chunk
        if len(temp_clips) == 1:
            # Just rename single clip
            os.rename(temp_clips[0], chunk_file)
        else:
            print(f"    🎭 Creating VARIED smooth transitions between {len(temp_clips)} images...")

            # ACTUAL TRANSITIONS: Create proper varied transitions
            print(f"      ✨ Creating REAL VARIED transitions")
            transition_clips = []

            for j in range(len(temp_clips)):
                if j == 0:
                    # First clip: just add it as-is
                    transition_clips.append(temp_clips[j])
                else:
                    # Create VARIED transition between previous and current
                    prev_clip = temp_clips[j-1]
                    curr_clip = temp_clips[j]
                    transition_file = f"{temp_dir}/transition_{chunk_idx}_{j}.mp4"

                    # CYCLE THROUGH DIFFERENT TRANSITION TYPES for variety!
                    transition_type = transitions[(j-1) % len(transitions)]

                    # Use DRAMATIC transition - 1 second duration so it's UNMISSABLE
                    # ADD TEXT OVERLAY TO SHOW WHICH TRANSITION IS BEING USED!
                    cmd = f'ffmpeg -y -i "{prev_clip}" -i "{curr_clip}" -filter_complex "[0:v][1:v]xfade=transition={transition_type}:duration=1.0:offset={duration-1.0:.1f}[xfaded]; [xfaded]drawtext=text=\'{transition_type.upper()}\':fontsize=72:fontcolor=white:box=1:boxcolor=black@0.7:x=(w-text_w)/2:y=h-text_h-50:enable=\'between(t,{duration-1.0:.1f},{duration:.1f})\'[v]" -map "[v]" -c:v libx264 -r {fps} -crf 23 -preset ultrafast -t {duration:.1f} "{transition_file}"'

                    print(f"      🔄 {transition_type.upper()} transition command: {cmd}")
                    if run_command(cmd, f"    {transition_type.upper()} transition {j}/{len(temp_clips)-1}", show_output=True):
                        transition_clips.append(transition_file)
                        print(f"      ✅ {transition_type.upper()} transition {j} SUCCESS")
                    else:
                        print(f"      ❌ {transition_type.upper()} transition {j} FAILED - using original clip")
                        transition_clips.append(curr_clip)

            # Now create the final chunk from transition clips
            if len(transition_clips) == 1:
                os.rename(transition_clips[0], chunk_file)
            else:
                concat_file = f"{temp_dir}/final_concat_{chunk_idx}.txt"
                with open(concat_file, 'w') as f:
                    for clip in transition_clips:
                        f.write(f"file '{os.path.abspath(clip)}'\n")

                # RE-ENCODE during concatenation to PRESERVE crossfade transitions
                cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:v libx264 -c:a aac -r {fps} -crf 23 -preset ultrafast "{chunk_file}"'
                if not run_command(cmd, f"    Finalizing chunk {chunk_idx + 1} (re-encoding to preserve transitions)", show_output=False):
                    return False

                # Clean up transition files
                for clip in transition_clips[1:]:  # Skip first clip (original)
                    try:
                        os.remove(clip)
                    except:
                        pass
                os.remove(concat_file)

            # Clean up original temp clips
            for clip in temp_clips:
                try:
                    os.remove(clip)
                except:
                    pass

        chunk_files.append(chunk_file)

        # Progress update
        completed = chunk_idx + 1
        total_chunks = (len(images) + chunk_size - 1) // chunk_size
        percentage = (completed / total_chunks) * 100
        print(f"  ✅ Chunk {completed}/{total_chunks} completed ({percentage:.1f}%)")

    # Final concatenation - transitions are already within chunks
    print("\n🎬 Final concatenation...")

    if len(chunk_files) == 1:
        # Just rename single chunk
        os.rename(chunk_files[0], output_file)
        success = True
    else:
        # Simple concatenation - smooth transitions are already built into each chunk
        print("  ✨ Smooth transitions already applied within each chunk")
        final_concat = f"{temp_dir}/final_concat.txt"
        with open(final_concat, 'w') as f:
            for chunk_file in chunk_files:
                f.write(f"file '{os.path.abspath(chunk_file)}'\n")

        cmd = f'ffmpeg -y -f concat -safe 0 -i "{final_concat}" -c copy "{output_file}"'
        success = run_command(cmd, "Creating final slideshow with smooth transitions")

    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)

    return success

def merge_audio(audio_files, output_file):
    """Merge multiple audio files"""
    if len(audio_files) == 0:
        print("No audio files found!")
        return False

    if len(audio_files) == 1:
        # Single audio file - just copy/convert
        cmd = f'ffmpeg -y -i "{audio_files[0]}" -c:a aac -b:a 192k "{output_file}"'
        return run_command(cmd, f"Processing single audio file: {os.path.basename(audio_files[0])}")

    # Multiple audio files - concatenate
    concat_file = "audio_concat.txt"
    with open(concat_file, 'w') as f:
        for audio in audio_files:
            f.write(f"file '{audio}'\n")

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:a aac -b:a 192k "{output_file}"'
    success = run_command(cmd, f"Merging {len(audio_files)} audio files")

    # Clean up
    os.remove(concat_file)

    return success

def combine_video_audio(video_file, audio_file, output_file):
    """Combine video and audio"""
    # Get audio duration
    cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_file}"'
    try:
        audio_duration = float(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip())
    except:
        print("Could not get audio duration")
        return False

    # Loop video to match audio duration
    cmd = f'ffmpeg -y -stream_loop -1 -i "{video_file}" -i "{audio_file}" -t {audio_duration} -c:v copy -c:a copy -shortest "{output_file}"'
    return run_command(cmd, f"Combining video and audio (duration: {audio_duration:.1f}s)")

def main():
    # Parse arguments
    args = sys.argv[1:]

    # Default values
    image_dir = "."
    test_mode = False
    min_duration = 3
    max_duration = 5

    # Parse command line arguments
    i = 0
    while i < len(args):
        if args[i] == "--test":
            test_mode = True
            i += 1
        elif args[i] == "--min-duration" and i + 1 < len(args):
            min_duration = int(args[i + 1])
            i += 2
        elif args[i] == "--max-duration" and i + 1 < len(args):
            max_duration = int(args[i + 1])
            i += 2
        elif not args[i].startswith("--"):
            image_dir = args[i]
            i += 1
        else:
            i += 1

    if not os.path.exists(image_dir):
        print(f"Directory not found: {image_dir}")
        sys.exit(1)

    print("🎬 VRChat Slideshow Creator")
    print(f"📁 Working directory: {image_dir}")
    print(f"⚙️  Test mode: {'ON (1-minute video)' if test_mode else 'OFF (full video)'}")
    print(f"⏱️  Image duration range: {min_duration}-{max_duration} seconds")

    # Find audio first (needed for duration calculation)
    audio_files = find_audio_files(image_dir)
    print(f"🎵 Found {len(audio_files)} audio files: {[os.path.basename(f) for f in audio_files]}")

    # Check if merged audio already exists
    audio_output = "audio_merged.m4a"
    if os.path.exists(audio_output):
        print(f"🎵 Using existing merged audio: {audio_output}")
        # Get duration of existing file
        try:
            cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_output}"'
            audio_duration = float(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip())
            print(f"   Duration: {audio_duration:.1f} seconds")
        except:
            print("Warning: Could not get duration of existing audio file")
            audio_duration = 0
    else:
        # Calculate audio duration from source files
        audio_duration = 0
        for audio_file in audio_files:
            try:
                cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_file}"'
                duration = float(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip())
                audio_duration += duration
            except:
                print(f"Warning: Could not get duration for {audio_file}")

    # Find images
    image_pattern = os.path.join(image_dir, "*.png")
    all_images = sorted(glob.glob(image_pattern))
    print(f"🖼️  Found {len(all_images)} total images")

    # Calculate slides based on mode
    if test_mode:
        # Test mode: 1 minute video
        test_duration = 60  # 1 minute
        slides_needed = int(test_duration / ((min_duration + max_duration) / 2))  # Use average duration
        print(f"🎵 Test mode: creating 1-minute video")
        print(f"⏱️  Slides needed for test: {slides_needed}")
    else:
        # Full mode: match audio duration
        avg_duration = (min_duration + max_duration) / 2
        slides_needed = int(audio_duration / avg_duration)
        print(f"🎵 Audio duration: {audio_duration:.1f} seconds")
        print(f"⏱️  Slides needed: {slides_needed} (avg {avg_duration:.1f}s per slide)")

        # Safety check - don't create ridiculously long videos
        if slides_needed > 2000:
            slides_needed = 2000
            print(f"⚠️  Limiting to {slides_needed} slides for practical processing time")
            print(f"   Final video will be ~{slides_needed * avg_duration / 60:.1f} minutes")

    # Select images based on mode
    if len(all_images) > 0:
        if test_mode:
            # Test mode: just use first N images
            images = all_images[:slides_needed]
            print(f"🎲 Test mode: Using first {len(images)} images")
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
                        show_progress(len(all_images) + i + 1, slides_needed, img)

            print(f"🎲 Selected {len(images)} images ({len(all_images)} unique + {remaining} repeats)")
    else:
        images = []

    print(f"🖼️  Final image count: {len(images)}")

    if len(audio_files) == 0:
        print("❌ No audio files found!")
        sys.exit(1)

    # Process audio
    audio_output = "audio_merged.m4a"

    # Process audio (skip if already exists)
    if os.path.exists(audio_output):
        print(f"\n🎵 Using existing merged audio: {audio_output}")
    else:
        print("\n🎵 Processing audio...")
        if not merge_audio(audio_files, audio_output):
            print("❌ Audio processing failed!")
            sys.exit(1)

    # Create slideshow with variable durations
    video_output = "slideshow_video.mp4"
    print("\n🎬 Creating slideshow...")

    # Use variable durations for more interesting slideshow
    if not create_slideshow(images, video_output, min_duration, max_duration, width=1920, height=1080, fps=25):
        print("❌ Slideshow creation failed!")
        sys.exit(1)

    # Combine video and audio
    final_output = "slideshow_with_audio.mp4"
    print("\n🎞️  Combining video and audio...")
    if not combine_video_audio(video_output, audio_output, final_output):
        print("❌ Final combination failed!")
        sys.exit(1)

    # Clean up intermediate files (but keep audio for reuse)
    print("\n🧹 Cleaning up intermediate files...")
    try:
        os.remove(video_output)
    except:
        pass
    # DON'T remove audio_output - keep it for reuse!

    # Show result
    file_size = os.path.getsize(final_output) / (1024 * 1024)  # MB
    print("\n✅ SUCCESS!")
    print(f"🎬 Final video: {final_output}")
    print(f"📏 File size: {file_size:.1f} MB")
if __name__ == "__main__":
    main()
