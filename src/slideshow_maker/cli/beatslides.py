#!/usr/bin/env python3
"""
Minimal CLI entry to exercise Phase 1: detect beats and select cut times.

Usage examples:
  python3 -m slideshow_maker.cli.beatslides input.mp3 --period 5 10 --target 7.5 \
      --grace 0.5 --min-gap 2.05 --duration 1.0 --audio-end 180
"""
from __future__ import annotations

import argparse
import sys
from typing import List

from ..beat_detection import detect_beats
from ..beat_selection import select_beats
from ..video import create_slideshow_with_durations
from .. import audio as audio_mod
from ..config import AUDIO_OUTPUT
from ..utils import get_audio_duration


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description="Beat-aligned planning (Phase 2 minimal)")
    p.add_argument("audio", help="Path to audio file")
    p.add_argument("images_dir", help="Directory of images")
    p.add_argument("--period", nargs=2, type=float, metavar=("MIN", "MAX"), default=[5.0, 10.0])
    p.add_argument("--target", type=float, default=7.5)
    p.add_argument("--grace", type=float, default=0.5)
    p.add_argument("--min-gap", type=float, default=2.05, help="Min cut gap safety (>= 2*xfade+0.05)")
    p.add_argument("--phase", type=float, default=-0.03)
    p.add_argument("--strict", action="store_true", default=False)
    p.add_argument("--audio-end", type=float, default=None, help="Audio length in seconds (optional)")
    p.add_argument("--transition", type=str, default="fade", help="xfade transition type (CPU)")
    p.add_argument("--xfade", type=float, default=0.6, help="Transition duration seconds")
    p.add_argument("--align", type=str, choices=["end","midpoint"], default="midpoint", help="Align transition end or midpoint to beat")
    p.add_argument("--hardcuts", action="store_true", default=False, help="Render without transitions (durations only)")
    p.add_argument("--no-audio", action="store_true", default=False, help="Skip muxing audio into the output")
    p.add_argument("--debug", action="store_true", default=False, help="Print detected beats and selected cuts; visualize cut markers")
    p.add_argument("--mark-beats", action="store_true", default=False, help="Render markers on every detected beat (hardcuts only)")
    p.add_argument("--all-beats", action="store_true", default=False, help="Use every detected beat as a transition boundary")
    p.add_argument("--max-seconds", type=float, default=None, help="Limit output plan to first N seconds of audio")
    p.add_argument("--pulse", action="store_true", default=False, help="Apply subtle saturation/brightness pulse on each beat")
    p.add_argument("--pulse-sat", type=float, default=1.25, help="Pulse saturation multiplier (>1 = boost)")
    p.add_argument("--pulse-bright", type=float, default=0.00, help="Pulse brightness delta (-1..1)")
    p.add_argument("--pulse-dur", type=float, default=0.08, help="Pulse duration seconds per beat")
    p.add_argument("--bloom", action="store_true", default=False, help="Add subtle gaussian bloom pulse on each beat")
    p.add_argument("--bloom-sigma", type=float, default=8.0, help="Bloom blur sigma (higher is softer)" )
    p.add_argument("--bloom-dur", type=float, default=0.08, help="Bloom pulse duration seconds per beat")
    p.add_argument("--counter", action="store_true", default=False, help="Show numeric counter at each beat")
    p.add_argument("--counter-size", type=int, default=36, help="Beat counter font size")
    p.add_argument("--counter-pos", type=str, choices=["tr","tl","br","bl"], default="tr", help="Beat counter position")
    p.add_argument("--preset", type=str, choices=["music-video"], help="Preset of sensible defaults")
    p.add_argument("--beat-mult", type=int, default=1, help="Overlay beat multiplier (1=every beat, 2=every other, etc.)")
    p.add_argument("--overlay-phase", type=float, default=0.0, help="Overlay phase offset seconds (advance/retard overlays)")
    p.add_argument("--cut-markers", action="store_true", default=False, help="Draw red tick marks at transition landings")
    p.add_argument("--overlay-guard", type=float, default=0.0, help="Do not pulse/tick within N seconds of a transition")
    args = p.parse_args(argv)

    # Apply preset defaults early
    if args.preset == "music-video":
        # Only override if user left defaults
        if args.align == "midpoint":
            pass
        else:
            args.align = "midpoint"
        if args.xfade == 0.6:
            pass
        else:
            args.xfade = float(args.xfade)
        if args.phase == -0.03:
            pass
        else:
            args.phase = float(args.phase)
        if args.period == [5.0, 10.0]:
            args.period = [5.0, 10.0]
        if args.target == 7.5:
            args.target = 7.5

    beats = detect_beats(args.audio)
    if not beats:
        print("No beats detected", file=sys.stderr)
        return 1

    if args.debug:
        print(f"Detected beats ({len(beats)}):")
        print(", ".join(f"{b:.3f}" for b in beats[:50]) + ("..." if len(beats) > 50 else ""))

    if args.audio_end is None:
        # Use true audio duration when available; fallback to last beat + target
        audio_end = get_audio_duration(args.audio) or (beats[-1] + args.target)
    else:
        audio_end = float(args.audio_end)
    # If you want a short preview, use --max-seconds. Omit it for full video
    if args.max_seconds is not None:
        audio_end = min(audio_end, float(args.max_seconds))

    period_min, period_max = float(args.period[0]), float(args.period[1])
    if args.all_beats:
        # Use every beat from the first beat onward up to audio_end
        cuts = [b for b in beats if b <= audio_end]
    else:
        cuts = select_beats(
            beats,
            audio_end=audio_end,
            period_min=period_min,
            period_max=period_max,
            target_period=args.target,
            strict=bool(args.strict),
            grace=float(args.grace),
            min_cut_gap=float(args.min_gap),
            phase=float(args.phase),
            strategy="nearest",
        )

    # Compute durations from cuts relative to start
    if not cuts:
        print("No cuts selected", file=sys.stderr)
        return 2

    if args.debug:
        print(f"Selected cuts ({len(cuts)}):")
        print(", ".join(f"{c:.3f}" for c in cuts[:50]) + ("..." if len(cuts) > 50 else ""))

    # Build absolute segment durations from t=0 to each cut
    durations = []
    if cuts:
        last = 0.0
        for c in cuts:
            if c <= last:
                continue
            durations.append(max(0.05, c - last))
            last = c
        # Add a short tail (half target) to close the video
        durations.append(max(0.2, args.target * 0.5))

    # Map images
    import os, glob
    exts = ["*.png", "*.jpg", "*.jpeg"]
    images = []
    for e in exts:
        images.extend(glob.glob(os.path.join(args.images_dir, e)))
    images = sorted(images)
    if not images:
        print("No images found", file=sys.stderr)
        return 3

    # Loop images if fewer than segments
    if len(images) < len(durations):
        reps = (len(durations) + len(images) - 1) // len(images)
        images = (images * reps)[: len(durations)]
    else:
        images = images[: len(durations)]

    out_file = "beat_aligned.mp4"
    if args.hardcuts:
        beat_markers = beats if args.mark_beats else None
        pulse_beats = beats if args.pulse else None
        ok = create_slideshow_with_durations(
            images,
            durations,
            out_file,
            visualize_cuts=args.debug,
            beat_markers=beat_markers,
            pulse_beats=pulse_beats,
            pulse_duration=float(args.pulse_dur),
            pulse_saturation=float(args.pulse_sat),
            pulse_brightness=float(args.pulse_bright),
            pulse_bloom=bool(args.bloom),
            pulse_bloom_sigma=float(args.bloom_sigma),
            pulse_bloom_duration=float(args.bloom_dur),
            counter_beats=beats if args.counter else None,
            counter_fontsize=int(args.counter_size),
            counter_position=str(args.counter_pos),
        )
    else:
        try:
            from ..video import create_beat_aligned_with_transitions
        except Exception as e:
            print(f"Transitions renderer unavailable: {e}", file=sys.stderr)
            return 4
        ok = create_beat_aligned_with_transitions(
            images,
            durations,
            out_file,
            transition_type=args.transition,
            transition_duration=float(args.xfade),
            align=args.align,
            mark_transitions=bool(args.debug or args.mark_beats),
            marker_duration=0.12,
            pulse=bool(args.pulse),
            pulse_duration=float(args.pulse_dur),
            pulse_saturation=float(args.pulse_sat),
            pulse_brightness=float(args.pulse_bright),
            bloom=bool(args.bloom),
            bloom_sigma=float(args.bloom_sigma),
            bloom_duration=float(args.bloom_dur),
            overlay_beats=beats,
            overlay_beat_multiplier=int(args.beat_mult),
            overlay_phase=float(args.overlay_phase),
            overlay_guard_seconds=float(args.overlay_guard),
            mark_cuts=bool(args.cut_markers),
        )
    if not ok:
        return 4
    print(f"✅ Created {out_file} with {len(images)} images and {len(durations)} segments")

    if not args.no_audio:
        # First ensure we have an AAC audio file to mux (MP3-in-MP4 can be flaky)
        if not audio_mod.merge_audio([args.audio], AUDIO_OUTPUT):
            print("Warning: failed to prepare audio track; leaving video without audio", file=sys.stderr)
            return 0
        final_with_audio = "beat_aligned_with_audio.mp4"
        if not audio_mod.combine_video_audio(out_file, AUDIO_OUTPUT, final_with_audio):
            print("Warning: failed to mux audio; leaving video without audio", file=sys.stderr)
            return 0
        print(f"🎵 Muxed audio -> {final_with_audio}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))


