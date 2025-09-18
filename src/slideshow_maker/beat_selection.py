#!/usr/bin/env python3
"""
Window-constrained beat selection algorithm.

Implements the redux pseudocode for choosing a subset of beats so that inter-cut
intervals land within [period_min, period_max], with strict/grace handling and
basic strategy selection (nearest only for Phase 1).
"""
from __future__ import annotations

from typing import List, Optional, Sequence


def choose_candidate_nearest(
    candidates: Sequence[float], target_time: float
) -> Optional[float]:
    if not candidates:
        return None
    return min(candidates, key=lambda x: abs(x - target_time))


def select_beats(
    beats: Sequence[float],
    audio_end: float,
    period_min: float,
    period_max: float,
    target_period: float,
    *,
    strict: bool = True,
    grace: float = 0.0,
    min_cut_gap: float = 0.0,
    phase: float = 0.0,
    strategy: str = "nearest",
) -> List[float]:
    # Phase compensation
    adjusted = [b + phase for b in beats if (b + phase) >= 0.0]
    chosen: List[float] = []
    if not adjusted:
        return chosen

    t = 0.0
    MIN = max(0.0, float(period_min))
    MAX = max(MIN, float(period_max))
    TP = max(MIN, float(target_period))

    # Helper to slice candidates inside a window
    def in_window(w_start: float, w_end: float) -> List[float]:
        return [b for b in adjusted if w_start <= b <= w_end]

    while True:
        w_start = t + MIN
        w_end = t + MAX
        S = in_window(w_start, w_end)

        if not S:
            if strict:
                S = in_window(t + MIN - grace, t + MAX + grace)
                if not S:
                    break
            else:
                target = max(w_start, min(t + TP, w_end))
                # Pick nearest across all beats to clamped target
                # We could narrow search, but adjusted is small enough.
                nearest = min(adjusted, key=lambda x: abs(x - target))
                S = [nearest]

        target = t + TP
        if strategy == "nearest":
            cand = choose_candidate_nearest(S, target)
        else:
            cand = choose_candidate_nearest(S, target)

        if cand is None:
            break

        if chosen and (cand - chosen[-1]) < min_cut_gap:
            # Try to find next best candidate that satisfies min_cut_gap
            viable = [c for c in S if (not chosen) or (c - chosen[-1]) >= min_cut_gap]
            cand = choose_candidate_nearest(viable, target)
            if cand is None:
                # No viable candidate; skip and continue planning from same t window
                # Move t slightly forward to avoid infinite loop
                t = t + MIN
                if t + MIN > audio_end:
                    break
                continue

        chosen.append(cand)
        t = cand
        if t + MIN > audio_end:
            break

    return chosen


