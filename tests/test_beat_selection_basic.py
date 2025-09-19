import math

from slideshow_maker.beat_selection import select_beats


def test_selection_respects_window_strict():
    # Beats roughly every 1.5s starting at 0.5
    beats = [0.5, 2.0, 3.5, 5.0, 6.5]
    cuts = select_beats(
        beats,
        audio_end=7.0,
        period_min=1.4,
        period_max=2.6,
        target_period=2.0,
        strict=True,
        grace=0.0,
        min_cut_gap=0.0,
        phase=0.0,
        strategy="nearest",
    )
    # Expect cuts to be picked near 2.0, 3.5, 5.0 (within window widths)
    assert cuts == [2.0, 3.5, 5.0]
    # Intervals within [1.4, 2.6]
    diffs = [cuts[i] - cuts[i - 1] for i in range(1, len(cuts))]
    assert all(1.4 - 1e-6 <= d <= 2.6 + 1e-6 for d in diffs)


def test_min_cut_gap_enforced():
    # Tight beats; enforce min_cut_gap so adjacent near-beats are skipped
    beats = [0.0, 0.6, 1.2, 1.8, 2.4]
    cuts = select_beats(
        beats,
        audio_end=2.5,
        period_min=0.5,
        period_max=1.0,
        target_period=0.8,
        strict=True,
        grace=0.0,
        min_cut_gap=0.9,  # force skipping too-close candidates
        phase=0.0,
        strategy="nearest",
    )
    # Should not include cuts closer than 0.9s apart
    diffs = [cuts[i] - cuts[i - 1] for i in range(1, len(cuts))]
    assert all(d >= 0.9 - 1e-6 for d in diffs)


def test_phase_compensation():
    beats = [0.5, 2.0, 3.5, 5.0]
    # Negative phase leads earlier
    cuts_neg = select_beats(
        beats,
        audio_end=6.0,
        period_min=1.4,
        period_max=2.6,
        target_period=2.0,
        strict=True,
        grace=0.0,
        min_cut_gap=0.0,
        phase=-0.5,
        strategy="nearest",
    )
    # Positive phase lags later
    cuts_pos = select_beats(
        beats,
        audio_end=6.0,
        period_min=1.4,
        period_max=2.6,
        target_period=2.0,
        strict=True,
        grace=0.0,
        min_cut_gap=0.0,
        phase=0.5,
        strategy="nearest",
    )
    assert cuts_neg != cuts_pos

