#!/usr/bin/env python3
"""
Beat detection utilities for beat-aligned slideshow creation.

Primary detector: aubio (CLI)
Fallback detector: librosa

Outputs beats in seconds (float), ascending, de-duplicated, with a minimum gap enforcement.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple

import numpy as np

try:
    import librosa  # type: ignore
    import soundfile as sf  # noqa: F401  # ensure backend present
except Exception:  # pragma: no cover - optional at runtime; validated in tests
    librosa = None  # type: ignore


def _run_command(command: str) -> Tuple[int, str, str]:
    process = subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = process.communicate()
    return process.returncode, out, err


def _dedupe_and_enforce_min_gap(beats: Iterable[float], min_gap_seconds: float = 0.12) -> List[float]:
    sorted_beats = sorted(float(b) for b in beats if b is not None)
    cleaned: List[float] = []
    last: Optional[float] = None
    for b in sorted_beats:
        if b < 0:
            continue
        if last is None or (b - last) >= min_gap_seconds:
            cleaned.append(b)
            last = b
    return cleaned


def detect_beats_with_aubio(audio_path: str) -> Optional[List[float]]:
    """Use aubio CLI to detect beats. Returns list of times in seconds or None if aubio not available."""
    if not shutil_which("aubio"):
        return None
    # aubio beat -i input -o - prints timestamps, one per line
    cmd = f"aubio beat -i {shlex.quote(audio_path)}"
    code, out, err = _run_command(cmd)
    if code != 0 or not out.strip():
        return None
    beats: List[float] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            beats.append(float(line))
        except ValueError:
            continue
    return beats if beats else None


def detect_beats_with_librosa(audio_path: str, sr: Optional[int] = None) -> Optional[List[float]]:
    if librosa is None:
        return None
    try:
        y, sr_used = librosa.load(audio_path, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr_used)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr_used, units="time")
        # beats returned as np array of times when units='time'
        return beats.tolist() if beats is not None and len(beats) > 0 else None
    except Exception:
        return None


def detect_beats(audio_path: str, min_gap_seconds: float = 0.12) -> List[float]:
    """Detect beats using aubio first, then librosa. Returns cleaned list of beat times in seconds."""
    beats = detect_beats_with_aubio(audio_path)
    if not beats:
        beats = detect_beats_with_librosa(audio_path)
    if not beats:
        return []
    return _dedupe_and_enforce_min_gap(beats, min_gap_seconds=min_gap_seconds)


def write_beats_to_file(beats: List[float], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        for b in beats:
            f.write(f"{b:.6f}\n")


def write_beats_json(beats: List[float], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"beats": beats}, f, indent=2)


def shutil_which(cmd: str) -> Optional[str]:
    from shutil import which

    return which(cmd)


def _cli(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Detect beats and print to stdout")
    parser.add_argument("audio", help="Path to audio file")
    parser.add_argument("--json", dest="json_path", help="Optional path to write JSON beats")
    parser.add_argument("--txt", dest="txt_path", help="Optional path to write text beats")
    parser.add_argument("--min-gap", type=float, default=0.12, help="Min gap between beats in seconds")
    args = parser.parse_args(argv)

    beats = detect_beats(args.audio, min_gap_seconds=args.min_gap)
    for b in beats:
        print(f"{b:.6f}")
    if args.json_path:
        write_beats_json(beats, args.json_path)
    if args.txt_path:
        write_beats_to_file(beats, args.txt_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli(sys.argv[1:]))


