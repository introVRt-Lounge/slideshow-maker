#!/usr/bin/env python3
"""
Video processing for the VRChat Slideshow Maker
"""

import os
import random
import shutil
from .config import (
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS, DEFAULT_CRF, DEFAULT_PRESET,
    DEFAULT_MIN_DURATION, DEFAULT_MAX_DURATION, DEFAULT_TRANSITION_DURATION,
    DEFAULT_CHUNK_SIZE, VIDEO_OUTPUT
)
from .transitions import get_random_transition
from .utils import run_command, get_image_info, get_available_transitions, print_ffmpeg_capabilities


def create_slideshow(images, output_file, min_duration=DEFAULT_MIN_DURATION, 
                    max_duration=DEFAULT_MAX_DURATION, width=DEFAULT_WIDTH, 
                    height=DEFAULT_HEIGHT, fps=DEFAULT_FPS):
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


def create_slideshow_chunked(images, output_file, min_duration=DEFAULT_MIN_DURATION, 
                           max_duration=DEFAULT_MAX_DURATION, width=DEFAULT_WIDTH, 
                           height=DEFAULT_HEIGHT, fps=DEFAULT_FPS):
    """Create slideshow in very small chunks for reliability with VARIED transitions"""
    # Use much smaller chunks to avoid FFmpeg complexity limits
    chunk_size = DEFAULT_CHUNK_SIZE
    temp_dir = "temp_chunks"
    os.makedirs(temp_dir, exist_ok=True)

    # Detect FFmpeg capabilities and get available transitions
    available_transitions, capabilities = get_available_transitions()
    
    if not available_transitions:
        print("❌ No transitions available! FFmpeg xfade support not detected.")
        print("   Please install FFmpeg with xfade filter support.")
        return False

    chunk_files = []

    print(f"📦 Processing {len(images)} images in chunks of {chunk_size}")
    print(f"🎭 Using {len(available_transitions)} available FFmpeg xfade transition types!")
    
    # Print capability information
    print_ffmpeg_capabilities()
    
    if capabilities['cpu_transitions_supported'] and capabilities['gpu_transitions_supported']:
        print("✨ Both CPU and GPU transitions available - maximum variety!")
    elif capabilities['cpu_transitions_supported']:
        print("💻 Using CPU transitions only (GPU not available)")
    elif capabilities['gpu_transitions_supported']:
        print("🎮 Using GPU transitions only (CPU fallback not available)")

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

            cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration:.1f} -vf "{vf_filter}" -c:v libx264 -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET} "{temp_clip}"'
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
                    transition_type = available_transitions[(j-1) % len(available_transitions)]

                    # Use DRAMATIC transition - 1 second duration so it's UNMISSABLE
                    # ADD TEXT OVERLAY TO SHOW WHICH TRANSITION IS BEING USED!
                    cmd = f'ffmpeg -y -i "{prev_clip}" -i "{curr_clip}" -filter_complex "[0:v][1:v]xfade=transition={transition_type}:duration={DEFAULT_TRANSITION_DURATION}:offset={duration-DEFAULT_TRANSITION_DURATION:.1f}[xfaded]; [xfaded]drawtext=text=\'{transition_type.upper()}\':fontsize=72:fontcolor=white:box=1:boxcolor=black@0.7:x=(w-text_w)/2:y=h-text_h-50:enable=\'between(t,{duration-DEFAULT_TRANSITION_DURATION:.1f},{duration:.1f})\'[v]" -map "[v]" -c:v libx264 -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET} -t {duration:.1f} "{transition_file}"'

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
                cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:v libx264 -c:a aac -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET} "{chunk_file}"'
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
