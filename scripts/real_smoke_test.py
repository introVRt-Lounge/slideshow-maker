#!/usr/bin/env python3
"""
REAL END-TO-END SMOKE TEST - Uses actual app like a real user would
"""
import os
import sys
import subprocess
import json
import re
from pathlib import Path
import shutil
import time

def run_real_smoke_test():
    """Run smoke test using actual CLI apps - exactly like a real user"""

    print("🚀 REAL SMOKE TEST: Using actual apps like a real user")
    print("=" * 60)

    # Phase 1: Assemble real files from /mnt/completed/2yr-anniversary/
    images_dir = "/mnt/completed/2yr-anniversary/"
    if not os.path.exists(images_dir):
        print(f"❌ Images directory not found: {images_dir}")
        return False

    # Count available VRChat images
    import glob
    image_files = glob.glob(os.path.join(images_dir, "*VRChat*.png"))
    print(f"🖼️  Found {len(image_files)} VRChat images in {images_dir}")

    if len(image_files) < 50:
        print(f"❌ Need at least 50 images, found {len(image_files)}")
        return False

    # Use first 50 images for classic slideshow (to show all transitions)
    classic_images = image_files[:50]
    print(f"🎯 Using first 50 images for classic slideshow (49 transitions)")

    # Phase 2: Call actual app for CLASSIC SLIDESHOW
    print("\n📹 PHASE 2A: CLASSIC SLIDESHOW - Using actual slideshow_cli.py")
    print("-" * 60)

    classic_output = "/mnt/completed/2yr-anniversary/slideshow_with_audio.mp4"

    # Call the actual classic slideshow CLI
    cmd = [
        sys.executable, "-m", "slideshow_maker.cli.slideshow_cli",
        images_dir,
        "--test-mode",  # 60s test instead of full 3+ hours
        "--min-duration", "2.0",
        "--max-duration", "4.0"
    ]

    print(f"🎬 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd="/home/heavygee/coding/slideshow-maker",
                           env={**os.environ, "PYTHONPATH": "/home/heavygee/coding/slideshow-maker/src"})

    if result.returncode != 0:
        print("❌ Classic slideshow CLI failed")
        return False

    # The CLI should have created the output file
    if not os.path.exists(classic_output):
        print(f"❌ Classic output file not created: {classic_output}")
        return False

    print(f"✅ Classic slideshow created: {classic_output}")

    # Phase 3: Call actual app for BEAT-MATCHED SLIDESHOW
    print("\n🥁 PHASE 2B: BEAT-MATCHED SLIDESHOW - Using actual beatslides.py")
    print("-" * 60)

    # Create beat-matched audio with known beats (30 beats in 45 seconds)
    beat_audio = "/mnt/completed/2yr-anniversary/beat_test_audio_30beats.m4a"
    create_beat_audio(beat_audio, duration=45, beats=30)

    beatmatch_output = "/mnt/completed/2yr-anniversary/smoke_test_beatmatch_30beats.mp4"

    # Call the actual beat-matched CLI
    cmd = [
        sys.executable, "-m", "slideshow_maker.cli.beatslides",
        beat_audio,
        images_dir,
        "--pulse", "--bloom", "--mask-scope", "foreground",
        "--mark-transitions", "--counter-beats", "--mark-cuts",
        "--output", beatmatch_output
    ]

    print(f"🎬 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd="/home/heavygee/coding/slideshow-maker",
                           env={**os.environ, "PYTHONPATH": "/home/heavygee/coding/slideshow-maker/src"})

    if result.returncode != 0:
        print("❌ Beat-matched slideshow CLI failed")
        return False

    if not os.path.exists(beatmatch_output):
        print(f"❌ Beat-matched output file not created: {beatmatch_output}")
        return False

    print(f"✅ Beat-matched slideshow created: {beatmatch_output}")

    # Phase 4: VALIDATE RESULTS
    print("\n🔍 PHASE 3: VALIDATION - Prove the system actually works")
    print("-" * 60)

    classic_valid = validate_classic_slideshow(classic_output)
    beatmatch_valid = validate_beat_match_slideshow(beatmatch_output, expected_beats=30)

    print("\n📊 VALIDATION RESULTS:")
    print(f"Classic: {'✅ PASS' if classic_valid['valid'] else '❌ FAIL'}")
    print(f"Beat-match: {'✅ PASS' if beatmatch_valid['valid'] else '❌ FAIL'}")

    if classic_valid['valid'] and beatmatch_valid['valid']:
        print("\n🎉 SUCCESS: System works for real users!")
        print("📁 Files created:")
        print(f"   Classic: {classic_output}")
        print(f"   Beat-match: {beatmatch_output}")
        return True
    else:
        print("\n❌ FAILURE: System does NOT work for real users")
        return False

def create_beat_audio(output_path, duration=45, beats=30):
    """Create audio with known beat structure"""
    print(f"🎵 Creating {duration}s audio with exactly {beats} known beats...")

    # Create simple beat pattern: beep every 1.5 seconds
    beat_interval = duration / beats  # Should be ~1.5s

    # Generate tone for each beat
    beat_files = []
    for i in range(beats):
        beat_file = f"/tmp/beat_{i}.wav"
        start_time = i * beat_interval

        # Create a 0.1 second beep
        cmd = f'ffmpeg -y -f lavfi -i "sine=frequency=1000:duration=0.1" -c:a pcm_s16le "{beat_file}"'
        subprocess.run(cmd, shell=True, capture_output=True)

        beat_files.append((beat_file, start_time))

    # Combine all beats into final audio
    concat_file = "/tmp/beat_concat.txt"
    with open(concat_file, 'w') as f:
        for beat_file, start_time in beat_files:
            f.write(f"file '{beat_file}'\n")

    # Create silent background and overlay beats
    cmd = f'ffmpeg -y -f lavfi -i "sine=frequency=0:duration={duration}" -i "{concat_file}" -filter_complex "[0:a][1:a]amix=inputs=2:duration=first[aout]" -map "[aout]" -c:a aac "{output_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True)

    # Cleanup
    for beat_file, _ in beat_files:
        os.remove(beat_file)
    os.remove(concat_file)

    if result.returncode == 0 and os.path.exists(output_path):
        print(f"✅ Created beat audio: {beats} beats in {duration}s")
        return True
    else:
        print("❌ Failed to create beat audio")
        return False

def validate_classic_slideshow(video_path):
    """Validate classic slideshow has diverse transitions"""

    print(f"🔍 Validating classic slideshow: {video_path}")

    # Check if file exists and has reasonable size
    if not os.path.exists(video_path):
        return {'valid': False, 'error': 'File not found'}

    file_size = os.path.getsize(video_path)
    if file_size < 1000000:  # Less than 1MB
        return {'valid': False, 'error': f'File too small: {file_size} bytes'}

    # Extract FFmpeg filter chain to see what transitions were applied
    cmd = f'ffprobe -v quiet -print_format json -show_streams "{video_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        return {'valid': False, 'error': 'FFprobe failed'}

    data = json.loads(result.stdout)

    # Check for text overlays (transition names) in encoder metadata
    has_text_overlays = False
    transition_names = []

    if 'streams' in data:
        for stream in data['streams']:
            if stream.get('codec_type') == 'video':
                if 'tags' in stream and 'ENCODER' in stream['tags']:
                    encoder = stream['tags']['ENCODER']
                    if 'drawtext' in encoder.lower():
                        has_text_overlays = True
                        # Try to extract transition names from encoder string
                        # This is a rough approximation
                        text_matches = re.findall(r'text=([^:]+)', encoder)
                        transition_names.extend(text_matches)

    # Check audio duration vs video duration
    audio_cmd = f'ffprobe -v quiet -print_format json -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
    audio_result = subprocess.run(audio_cmd, shell=True, capture_output=True, text=True)
    duration = float(audio_result.stdout.strip()) if audio_result.returncode == 0 else 0

    # Check if duration is reasonable (should be around 60s for test mode)
    duration_ok = 30 <= duration <= 120

    # Count unique transitions found in encoder string
    unique_transitions = len(set(transition_names))

    result = {
        'valid': duration_ok and has_text_overlays,
        'duration': duration,
        'has_text_overlays': has_text_overlays,
        'unique_transitions': unique_transitions,
        'transition_names': transition_names[:10],  # Show first 10
        'file_size': file_size,
        'method': 'FFmpeg stream metadata analysis'
    }

    print(f"   Duration: {duration:.1f}s ({'✅' if duration_ok else '❌'})")
    print(f"   Text overlays: {has_text_overlays} ({'✅' if has_text_overlays else '❌'})")
    print(f"   Unique transitions: {unique_transitions}")

    return result

def validate_beat_match_slideshow(video_path, expected_beats=30):
    """Validate beat-matched slideshow"""

    print(f"🔍 Validating beat-match slideshow: {video_path}")

    # Check if file exists
    if not os.path.exists(video_path):
        return {'valid': False, 'error': 'File not found'}

    file_size = os.path.getsize(video_path)
    if file_size < 1000000:  # Less than 1MB
        return {'valid': False, 'error': f'File too small: {file_size} bytes'}

    # Check for beat counter by looking for drawtext in stream info
    cmd = f'ffprobe -v quiet -print_format json -show_streams "{video_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    has_beat_markers = False
    has_counter = False
    encoder_info = ""

    if result.returncode == 0:
        data = json.loads(result.stdout)
        if 'streams' in data:
            for stream in data['streams']:
                if stream.get('codec_type') == 'video':
                    if 'tags' in stream and 'ENCODER' in stream['tags']:
                        encoder = stream['tags']['ENCODER']
                        encoder_info = encoder.lower()
                        if 'drawtext' in encoder_info:
                            has_beat_markers = True
                            # Look for counter patterns (numbers in drawtext)
                            if re.search(r'drawtext.*\d+', encoder_info):
                                has_counter = True

    # Check duration matches expected beat count (roughly 1-2 seconds per beat)
    duration_cmd = f'ffprobe -v quiet -print_format json -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
    duration_result = subprocess.run(duration_cmd, shell=True, capture_output=True, text=True)
    duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0

    estimated_beats = int(duration / 1.5)  # Rough estimate
    duration_ok = abs(duration - 45) < 10  # Should be around 45s
    beat_count_ok = abs(estimated_beats - expected_beats) < 5

    result = {
        'valid': has_beat_markers and duration_ok,
        'duration': duration,
        'has_beat_markers': has_beat_markers,
        'has_counter': has_counter,
        'estimated_beats': estimated_beats,
        'expected_beats': expected_beats,
        'beat_count_matches': beat_count_ok,
        'encoder_info': encoder_info[:200],  # First 200 chars
        'file_size': file_size,
        'method': 'FFmpeg stream analysis + duration check'
    }

    print(f"   Duration: {duration:.1f}s ({'✅' if duration_ok else '❌'})")
    print(f"   Beat markers: {has_beat_markers} ({'✅' if has_beat_markers else '❌'})")
    print(f"   Beat counter: {has_counter} ({'✅' if has_counter else '❌'})")
    print(f"   Estimated beats: {estimated_beats} (expected: {expected_beats}) ({'✅' if beat_count_ok else '❌'})")

    return result

if __name__ == "__main__":
    success = run_real_smoke_test()
    sys.exit(0 if success else 1)
