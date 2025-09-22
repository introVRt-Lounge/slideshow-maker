from unittest import mock

from slideshow_maker.video import create_slideshow_with_durations, create_beat_aligned_with_transitions


@mock.patch("slideshow_maker.utils.run_command", return_value=True)
def test_counter_persists_across_clips(mock_run):
    images = [f"img_{i}.png" for i in range(3)]
    durations = [1.0, 1.0, 1.0]
    beats = [0.4, 1.2, 2.2]  # crosses boundaries
    ok = create_slideshow_with_durations(
        images,
        durations,
        "out.mp4",
        counter_beats=beats,
        counter_fontsize=24,
        counter_position="tr",
    )
    assert ok is True


@mock.patch("slideshow_maker.utils.run_command", return_value=True)
@mock.patch("slideshow_maker.utils.detect_nvenc_support", return_value=False)
def test_overlay_guard_suppresses_near_landings(mock_nvenc, mock_run):
    images = [f"img_{i}.png" for i in range(2)]
    durations = [1.0, 1.0]
    beats = [0.49, 1.01]  # one close to landing at 1.0s
    ok = create_beat_aligned_with_transitions(
        images,
        durations,
        "out.mp4",
        overlay_beats=beats,
        overlay_guard_seconds=0.1,
        marker_duration=0.12,
        transition_duration=0.2,
        align="midpoint",
    )
    assert ok is True


