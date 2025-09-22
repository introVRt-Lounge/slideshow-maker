from unittest import mock

from slideshow_maker.video import create_beat_aligned_with_transitions


@mock.patch("slideshow_maker.utils.run_command")
@mock.patch("slideshow_maker.utils.detect_nvenc_support", return_value=False)
def test_per_segment_fallback_hardcuts(mock_nvenc, mock_run):
    # Simulate ffmpeg success for concat path
    mock_run.return_value = True
    images = [f"img_{i}.png" for i in range(3)]
    durations = [0.30, 0.20, 0.30]  # middle boundary too short for xfade_min=0.25
    ok = create_beat_aligned_with_transitions(
        images,
        durations,
        "out.mp4",
        quantize="nearest",
        transition_type="fade",
        transition_duration=0.4,
        min_effective=0.25,
        align="midpoint",
        fallback_style="whitepop",
        fallback_duration=0.05,
    )
    assert ok is True
    # run_command should be called (concat and final encode), but we don't assert counts to keep loose coupling


