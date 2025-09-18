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


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description="Beat-aligned planning (Phase 1)")
    p.add_argument("audio", help="Path to audio file")
    p.add_argument("--period", nargs=2, type=float, metavar=("MIN", "MAX"), default=[5.0, 10.0])
    p.add_argument("--target", type=float, default=7.5)
    p.add_argument("--grace", type=float, default=0.5)
    p.add_argument("--min-gap", type=float, default=2.05, help="Min cut gap safety (>= 2*xfade+0.05)")
    p.add_argument("--phase", type=float, default=0.0)
    p.add_argument("--strict", action="store_true", default=False)
    p.add_argument("--audio-end", type=float, default=None, help="Audio length in seconds (optional)")
    args = p.parse_args(argv)

    beats = detect_beats(args.audio)
    if not beats:
        print("No beats detected", file=sys.stderr)
        return 1

    if args.audio_end is None:
        # Fallback: use last beat + target as rough end
        audio_end = beats[-1] + args.target
    else:
        audio_end = float(args.audio_end)

    period_min, period_max = float(args.period[0]), float(args.period[1])
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

    for c in cuts:
        print(f"{c:.6f}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))


