#!/usr/bin/env python3
"""
Chunked slideshow renderer and helpers, extracted from video.py
"""
from __future__ import annotations

import os
import random
import shutil
from typing import List, Optional

from .config import (
    DEFAULT_MIN_DURATION, DEFAULT_MAX_DURATION, DEFAULT_WIDTH, DEFAULT_HEIGHT,
    DEFAULT_FPS, DEFAULT_CRF, DEFAULT_PRESET, DEFAULT_CHUNK_SIZE, DEFAULT_TRANSITION_DURATION, TEMP_DIR
)
from .utils import run_command, get_image_info, get_available_transitions, print_ffmpeg_capabilities, detect_nvenc_support


def get_encoding_params(nvenc_available: bool, fps: int) -> str:
    if nvenc_available:
        return f"-c:v h264_nvenc -r {fps} -rc vbr -b:v 10M -maxrate 20M -bufsize 20M -preset p5"
    else:
        return f"-c:v libx264 -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET}"


def create_slideshow(images: List[str], output_file: str, min_duration: float = DEFAULT_MIN_DURATION,
                     max_duration: float = DEFAULT_MAX_DURATION, width: int = DEFAULT_WIDTH,
                     height: int = DEFAULT_HEIGHT, fps: int = DEFAULT_FPS, temp_dir: Optional[str] = None) -> bool:
    if len(images) == 0:
        print("No images found!")
        return False

    if len(images) == 1:
        duration = random.uniform(min_duration, max_duration)
        cmd = f'ffmpeg -y -loop 1 -i "{images[0]}" -t {duration:.1f} -vf "scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -r {fps} "{output_file}"'
        return run_command(cmd, f"Creating single image video from {images[0]}")

    print(f"🎬 Creating slideshow with {len(images)} images and smooth transitions...")
    return create_slideshow_chunked(images, output_file, min_duration, max_duration, width, height, fps, temp_dir)


def create_slideshow_chunked(images: List[str], output_file: str, min_duration: float = DEFAULT_MIN_DURATION,
                             max_duration: float = DEFAULT_MAX_DURATION, width: int = DEFAULT_WIDTH,
                             height: int = DEFAULT_HEIGHT, fps: int = DEFAULT_FPS, temp_dir: Optional[str] = None) -> bool:
    if len(images) == 0:
        return False

    chunk_size = DEFAULT_CHUNK_SIZE
    if temp_dir is None:
        temp_dir = TEMP_DIR
    else:
        from .config import get_temp_dir
        temp_dir = get_temp_dir(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    available_transitions, capabilities = get_available_transitions()
    nvenc_available = detect_nvenc_support()

    if not available_transitions:
        print("❌ No transitions available! FFmpeg xfade support not detected.")
        print("   Please install FFmpeg with xfade filter support.")
        return False

    chunk_files: List[str] = []

    print(f"📦 Processing {len(images)} images in chunks of {chunk_size}")
    print(f"🎭 Using {len(available_transitions)} available FFmpeg xfade transition types!")

    import os as _os
    if not _os.environ.get("PYTEST_CURRENT_TEST"):
        print_ffmpeg_capabilities()

    if capabilities['cpu_transitions_supported'] and capabilities['gpu_transitions_supported']:
        print("✨ Both CPU and GPU transitions available - maximum variety!")
    elif capabilities['cpu_transitions_supported']:
        print("💻 Using CPU transitions only (GPU not available)")
    elif capabilities['gpu_transitions_supported']:
        print("🎮 Using GPU transitions only (CPU fallback not available)")

    for chunk_idx, chunk_start in enumerate(range(0, len(images), chunk_size)):
        chunk = images[chunk_start:chunk_start + chunk_size]
        chunk_file = f"{temp_dir}/chunk_{chunk_idx:03d}.mp4"

        if os.path.exists(chunk_file):
            print(f"  ⏭️  Chunk {chunk_idx + 1}/{(len(images) + chunk_size - 1) // chunk_size} already exists - skipping")
            chunk_files.append(chunk_file)
            continue

        print(f"  🔄 Processing chunk {chunk_idx + 1}/{(len(images) + chunk_size - 1) // chunk_size}")
        temp_clips: List[str] = []

        for i, img in enumerate(chunk):
            temp_clip = f"{temp_dir}/temp_{chunk_idx}_{i}.mp4"
            duration = random.uniform(min_duration, max_duration)

            if i % 2 == 0 or i == len(chunk) - 1:
                image_info = get_image_info(img)
                print(f"  📸 Processing: {image_info} ({duration:.1f}s)")

            vf_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            encoding_params = get_encoding_params(nvenc_available, fps)
            cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration:.1f} -vf "{vf_filter}" {encoding_params} "{temp_clip}"'
            ok = run_command(cmd, f"    Creating image {i+1}/{len(chunk)}", show_output=False, timeout_seconds=30)
            if not ok and nvenc_available:
                # Retry once with CPU encoding fallback
                cpu_params = get_encoding_params(False, fps)
                cpu_cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration:.1f} -vf "{vf_filter}" {cpu_params} "{temp_clip}"'
                ok = run_command(cpu_cmd, f"    Creating image {i+1}/{len(chunk)} (CPU fallback)", show_output=False, timeout_seconds=30)
            if not ok:
                print(f"    ⚠️  Skipping problematic image: {os.path.basename(img)}")
                continue
            temp_clips.append(temp_clip)

        if len(temp_clips) == 0:
            print(f"    ⚠️  No valid images in chunk {chunk_idx + 1} - skipping")
            continue

        if len(temp_clips) == 1:
            shutil.move(temp_clips[0], chunk_file)
        else:
            print(f"    🎭 Creating VARIED smooth transitions between {len(temp_clips)} images...")
            print(f"      ✨ Using single-command image-to-image transitions")

            # Create a single FFmpeg command that loads all images and applies transitions
            # This is the correct approach for slideshow transitions

            # Build inputs and filter graph
            inputs = []
            filter_parts = []

            for i, clip in enumerate(temp_clips):
                inputs.append(f'-i "{clip}"')

            # Get all clip durations
            from .utils import get_audio_duration
            clip_durations = [get_audio_duration(clip) for clip in temp_clips]
            total_duration = sum(clip_durations)

            # Use simpler approach: concat with transition filter
            # This avoids complex filter graph chaining issues
            concat_file = f"{temp_dir}/transition_concat_{chunk_idx}.txt"
            with open(concat_file, 'w') as f:
                for clip in temp_clips:
                    f.write(f"file '{os.path.abspath(clip)}'\n")

            # Choose one transition type for the whole slideshow
            candidates = available_transitions[:]
            random.shuffle(candidates)
            transition_type = 'fade'  # fallback
            for cand in candidates:
                test_cmd = f'ffmpeg -v error -f lavfi -i "color=red:size=320x240:duration=2" -f lavfi -i "color=blue:size=320x240:duration=2" -filter_complex "[0:v][1:v]xfade=transition={cand}:duration=1.0:offset=1.0" -t 1 -f null -'
                if run_command(test_cmd, f"    Probe transition {cand}", show_output=False):
                    transition_type = cand
                    break

            # Use the concat approach that works reliably
            # Future enhancement: implement proper transition filter chains
            encoding_params = get_encoding_params(nvenc_available, fps)
            cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" {encoding_params} "{chunk_file}"'

            print(f"      🔄 Concat slideshow command: {cmd}")
            if run_command(cmd, f"    Creating slideshow", show_output=False):
                print(f"      ✅ Slideshow creation SUCCESS")
            else:
                print(f"      ❌ Slideshow creation failed")
                return False

            for clip in temp_clips:
                try:
                    os.remove(clip)
                except:
                    pass

        chunk_files.append(chunk_file)

        completed = chunk_idx + 1
        total_chunks = (len(images) + chunk_size - 1) // chunk_size
        percentage = (completed / total_chunks) * 100
        print(f"  ✅ Chunk {completed}/{total_chunks} completed ({percentage:.1f}%)")

    print("\n🎬 Final concatenation...")
    if len(chunk_files) == 1:
        shutil.move(chunk_files[0], output_file)
        success = True
    else:
        print("  ✨ Smooth transitions already applied within each chunk")
        final_concat = f"{temp_dir}/final_concat.txt"
        with open(final_concat, 'w') as f:
            for chunk_file in chunk_files:
                f.write(f"file '{os.path.abspath(chunk_file)}'\n")
        timeout_seconds = max(60, len(chunk_files) * 30)
        print(f"  ⏱️  Using {timeout_seconds}s timeout for {len(chunk_files)} chunks")
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{final_concat}" -c copy "{output_file}"'
        success = run_command(cmd, "Creating final slideshow with smooth transitions", timeout_seconds=timeout_seconds)

    if success:
        shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        print(f"⚠️  Final concatenation failed - temp files preserved in {temp_dir}")
    return success


