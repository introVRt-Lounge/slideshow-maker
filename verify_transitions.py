#!/usr/bin/env python3
"""
Visual verification system for slideshow transitions.
Creates test videos with clearly different colors and analyzes frames using SSIM
to detect smooth transitions vs hard cuts.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import cv2
import numpy as np

def create_color_test_videos():
    """Create test videos with solid colors for transition verification."""
    temp_dir = tempfile.mkdtemp(prefix="transition_test_")

    # Create solid color images
    colors = [
        ("red", "FF0000"),
        ("blue", "0000FF"),
        ("green", "00FF00"),
        ("yellow", "FFFF00")
    ]

    images = []
    for color_name, color_hex in colors:
        img_path = os.path.join(temp_dir, f"{color_name}.png")
        # Create 320x240 solid color image
        cmd = f'ffmpeg -y -f lavfi -i "color=0x{color_hex}:size=320x240:duration=1" -frames:v 1 "{img_path}"'
        subprocess.run(cmd, shell=True, capture_output=True)
        images.append(img_path)

    return temp_dir, images

def classify_transition(video_path, t0_seconds, window_seconds=1.0, fps=30.0,
                        ssim_jump=0.25, smooth_run_frames=4):
    """
    Returns ('cut'|'smooth'|'unknown', details)
    Logic: sample frames around t0 at constant fps, compute 1-SSIM for consecutive frames,
    then measure how many consecutive frames exceed ssim_jump around the peak near t0.
    Short run (<=2) => hard cut. Longer run (>= smooth_run_frames) => smooth transition.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 'unknown', 'cannot open video'

    # Helper: SSIM for grayscale frames
    def ssim01(a, b):
        a = a.astype(np.float32); b = b.astype(np.float32)
        C1, C2 = (0.01*255)**2, (0.03*255)**2
        mu_a = cv2.GaussianBlur(a, (11,11), 1.5)
        mu_b = cv2.GaussianBlur(b, (11,11), 1.5)
        mu_a2, mu_b2, mu_ab = mu_a*mu_a, mu_b*mu_b, mu_a*mu_b
        sigma_a2 = cv2.GaussianBlur(a*a, (11,11), 1.5) - mu_a2
        sigma_b2 = cv2.GaussianBlur(b*b, (11,11), 1.5) - mu_b2
        sigma_ab = cv2.GaussianBlur(a*b, (11,11), 1.5) - mu_ab
        ssim = ((2*mu_ab + C1)*(2*sigma_ab + C2)) / ((mu_a2 + mu_b2 + C1)*(sigma_a2 + sigma_b2 + C2) + 1e-9)
        return float(ssim.mean())

    # Build timestamps to sample
    half = window_seconds / 2.0
    start = max(0.0, t0_seconds - half)
    n = int(window_seconds * fps) + 2
    times = [start + i/fps for i in range(n)]

    frames = []
    for ts in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, ts*1000.0)
        ok, frame = cap.read()
        if not ok:
            continue
        # Downscale and grayscale for robustness/speed
        frame = cv2.resize(frame, (160, int(160*frame.shape[0]/frame.shape[1])), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append((ts, gray))
    cap.release()

    if len(frames) < 3:
        return 'unknown', 'insufficient frames'

    # 1-SSIM between consecutive frames
    diffs = []
    for i in range(len(frames)-1):
        s = ssim01(frames[i][1], frames[i+1][1])
        diffs.append((frames[i+1][0], 1.0 - s))

    if not diffs:
        return 'unknown', 'no diffs'

    # Find the local peak nearest t0
    peak_idx = min(range(len(diffs)), key=lambda i: abs(diffs[i][0] - t0_seconds))
    # Count contiguous frames above threshold around that peak
    def run_length(center):
        rl = 1
        # left
        j = center - 1
        while j >= 0 and diffs[j][1] > ssim_jump: rl += 1; j -= 1
        # right
        j = center + 1
        while j < len(diffs) and diffs[j][1] > ssim_jump: rl += 1; j += 1
        return rl

    rl = run_length(peak_idx)
    peak_val = diffs[peak_idx][1]

    if rl <= 2:
        return 'cut', f'peak 1-SSIM={peak_val:.3f}, run={rl} frames'
    elif rl >= smooth_run_frames:
        return 'smooth', f'peak 1-SSIM={peak_val:.3f}, run={rl} frames'
    else:
        return 'unknown', f'borderline: peak 1-SSIM={peak_val:.3f}, run={rl} frames'

def test_transitions_have_smooth_changes(video_path, expected_transitions=3):
    """
    Analyze video frames to detect if transitions are smooth (gradual color changes)
    rather than hard cuts (sudden color changes).
    """
    if not os.path.exists(video_path):
        return False, "Video file does not exist"

    # Get video duration
    probe_result = subprocess.run(f'ffprobe -v quiet -print_format json -show_format "{video_path}"',
                                shell=True, capture_output=True, text=True)

    if probe_result.returncode != 0:
        return False, "Could not get video duration"

    import json
    data = json.loads(probe_result.stdout)
    duration = float(data['format']['duration'])

    # Check for transitions at expected intervals
    transition_times = []
    segment_duration = duration / (expected_transitions + 1)
    for i in range(expected_transitions):
        transition_times.append(segment_duration * (i + 1))

    smooth_count = 0
    cut_count = 0

    for t0 in transition_times:
        transition_type, details = classify_transition(video_path, t0)
        print(f"  Transition at {t0:.1f}s: {transition_type.upper()} - {details}")

        if transition_type == 'smooth':
            smooth_count += 1
        elif transition_type == 'cut':
            cut_count += 1

    # If we have more smooth transitions than cuts, consider it working
    if smooth_count > cut_count:
        return True, f"{smooth_count}/{expected_transitions} smooth transitions detected"
    else:
        return False, f"Only {smooth_count}/{expected_transitions} smooth transitions, {cut_count} hard cuts"

if __name__ == "__main__":
    print("🎯 Transition Visual Verification System")
    print("This will create test videos and verify transitions are actually smooth")

    # Test our transition system
    temp_dir, images = create_color_test_videos()

    try:
        # Import and test our slideshow creator
        import sys
        sys.path.insert(0, '/home/heavygee/coding/slideshow-maker/src')
        from slideshow_maker.video import create_slideshow

        output = os.path.join(temp_dir, "transition_test.mp4")
        success = create_slideshow(images[:3], output, min_duration=1.0, max_duration=1.5)

        if success and os.path.exists(output):
            print(f"✅ Video created: {output}")

            # Analyze the result
            has_transitions, message = test_transitions_have_smooth_changes(output)
            print(f"🎭 Transition analysis: {'PASS' if has_transitions else 'FAIL'} - {message}")

            if not has_transitions:
                print("❌ VERIFICATION FAILED: Transitions appear to be hard cuts!")
                print("   The system is falling back to hard cuts when transitions fail.")
                print("   This means our 'smooth transition' claims are misleading.")
                print(f"   Keeping video for manual inspection: {output}")

                # Don't cleanup so we can inspect the video
                temp_dir = None
            else:
                print("✅ VERIFICATION PASSED: Smooth transitions detected!")
        else:
            print("❌ Video creation failed")

    finally:
        if temp_dir:
            # Cleanup
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up {temp_dir}")
