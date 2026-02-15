#!/usr/bin/env python3
"""
Debug beat audio creation
"""
import subprocess
import os

def create_simple_beat_audio(output_path, beats=5, duration=10):
    """Create simple beat audio for testing"""

    print(f"🎵 Creating {beats} beats over {duration}s...")

    # Create a simple audio file with beeps at regular intervals
    interval = duration / beats

    # Create a tone file
    tone_file = "/tmp/tone.wav"
    cmd = f'ffmpeg -y -f lavfi -i "sine=frequency=800:duration=0.2" -c:a pcm_s16le "{tone_file}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Tone creation: {result.returncode}")

    if result.returncode != 0:
        print(f"❌ Tone creation failed: {result.stderr}")
        return False

    # Create silent background
    silent_file = "/tmp/silent.wav"
    cmd = f'ffmpeg -y -f lavfi -i "sine=frequency=0:duration={duration}" -c:a pcm_s16le "{silent_file}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Silent creation: {result.returncode}")

    if result.returncode != 0:
        print(f"❌ Silent creation failed: {result.stderr}")
        return False

    # Mix them
    cmd = f'ffmpeg -y -i "{silent_file}" -i "{tone_file}" -filter_complex "[0:a][1:a]amix=inputs=2:duration=first[aout]" -map "[aout]" -c:a aac "{output_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Mix result: {result.returncode}")

    if result.returncode != 0:
        print(f"❌ Mix failed: {result.stderr}")
        return False

    # Check output
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"✅ Created {output_path} ({size} bytes)")
        return True
    else:
        print("❌ Output file not created")
        return False

if __name__ == "__main__":
    success = create_simple_beat_audio("/tmp/test_beats.m4a", beats=5, duration=10)
    print(f"Overall: {'✅ SUCCESS' if success else '❌ FAILED'}")
