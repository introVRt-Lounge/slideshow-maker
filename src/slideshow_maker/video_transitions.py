#!/usr/bin/env python3
"""
Beat-aligned transitions renderer, extracted from video.py
"""
from __future__ import annotations

import json
import os
import tempfile
import shutil
from typing import List, Optional

from .config import (
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS, DEFAULT_TRANSITION_DURATION
)
from .utils import run_command, detect_nvenc_support
from .video_chunked import get_encoding_params  # reuse helper


def create_slideshow_with_durations(
    images: List[str],
    durations: List[float],
    output_file: str,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
    temp_dir: Optional[str] = None,
    quantize: str = "nearest",
    visualize_cuts: bool = False,
    marker_duration: float = 0.12,
    beat_markers: Optional[List[float]] = None,
    pulse_beats: Optional[List[float]] = None,
    pulse_duration: float = 0.08,
    pulse_saturation: float = 1.25,
    pulse_brightness: float = 0.00,
    pulse_bloom: bool = False,
    pulse_bloom_sigma: float = 8.0,
    pulse_bloom_duration: float = 0.08,
    counter_beats: Optional[List[float]] = None,
    counter_fontsize: int = 36,
    counter_position: str = "tr",
    cut_markers: Optional[List[float]] = None,
    mask_scope: str = "none",
    workers: int = 1,
) -> bool:
    """Create a slideshow with xfade transitions aligned to beat-planned segment durations.

    Safety: If any effective transition duration would be too small (< min_effective)
    for a given adjacent segment pair, fallback to hardcuts for the entire render.
    """
    if not images:
        print("No images found!")
        return False

    count = min(len(images), len(durations))
    images = images[:count]
    durations = [max(0.1, float(d)) for d in durations[:count]]
    # Quantize durations to exact frame boundaries for precise cut alignment
    q_durations = []
    for d in durations:
        if quantize == "floor":
            frames = max(1, int(float(d) * fps))
        elif quantize == "ceil":
            frames = max(1, int((float(d) * fps) + 0.999999))
        else:
            frames = max(1, int(round(float(d) * fps)))
        q_durations.append(max(1.0 / fps, frames / float(fps)))
    durations = q_durations


    # Unified approach: Always generate individual clips then concat
    # No arbitrary limits - scales to any number of images

    # Build ffmpeg inputs: looped stills with explicit -t (and optional masks)
    input_args = []
    use_masks = False
    masks = []
    if mask_scope in ("foreground", "background"):
        # Prefer precomputed masks next to images or in a sibling 'masks/' directory
        found_all = True
        tentative_masks = []
        for img in images:
            base, ext = os.path.splitext(img)
            filename = os.path.basename(img)
            name_no_ext, _ = os.path.splitext(filename)
            candidates = [
                f"{base}_mask.png",
                os.path.join(os.path.dirname(img), "masks", f"{name_no_ext}_mask.png"),
            ]
            chosen = None
            for cand in candidates:
                if os.path.exists(cand):
                    chosen = cand
                    break
            if chosen is None:
                found_all = False
                tentative_masks.append(None)
            else:
                tentative_masks.append(chosen)
        if found_all and tentative_masks:
            masks = tentative_masks  # type: ignore
            use_masks = True
        else:
            # Avoid heavy init during tests; try rembg generation only if needed
            if not os.environ.get("PYTEST_CURRENT_TEST"):
                try:
                    from .background_removal import BackgroundRemover  # type: ignore
                    remover = BackgroundRemover(gpu_acceleration=False)
                    if remover.is_available():
                        gen_masks = []
                        for img in images:
                            m = remover.create_mask(img, None)
                            gen_masks.append(m)
                        if all(bool(m) for m in gen_masks) and len(gen_masks) == len(images):
                            masks = gen_masks  # type: ignore
                            use_masks = True
                    else:
                        use_masks = False
                except Exception:
                    use_masks = False
    for img, d in zip(images, durations):
        input_args.append(f'-loop 1 -t {d:.3f} -i "{img}"')
    if use_masks:
        for m, d in zip(masks, durations):
            input_args.append(f'-loop 1 -t {d:.3f} -i "{m}"')

    # Filters: scale/pad each input to labeled stream sN (and optional masks to mN)
    scale_parts = []
    for idx in range(count):
        scale_parts.append(
            f'[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[s{idx}]'
        )
    filters = [';'.join(scale_parts)]  # start filter graph with scaling chain
    if use_masks:
        mask_scale_parts = []
        for idx in range(count):
            # mask inputs start after image inputs
            midx = count + idx
            mask_scale_parts.append(
                f'[{midx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,'
                f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=gray[m{idx}]'
            )
        filters.append(';'.join(mask_scale_parts))

    # Create chained xfade graph with offsets aligned near the beat
    prev_label = 's0'
    prev_duration = durations[0]
    last_label = prev_label
    # Parallel mask chain
    if use_masks:
        mask_prev_label = 'm0'
        mask_last_label = mask_prev_label
    transition_times = []  # absolute times (seconds) when the beat-aligned transition should "land"
    for i in range(1, count):
        curr_d = durations[i]
        td_eff = min(max(0.05, transition_duration), max(0.05, prev_duration - 0.05), max(0.05, curr_d - 0.05))
        if td_eff < 0.25:
            # Per-segment fallback: hardcut concat with optional micro-effect at boundary
            out_label = f'v{i}'
            boundary_t = prev_duration
            if fallback_style != "none" and fallback_duration > 0:
                # Build a tiny overlay chain on last_label before concat
                eff = None
                if fallback_style == "whitepop":
                    eff = f"drawbox=x=0:y=0:w=iw:h=ih:color=white@1.0:t=fill:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                elif fallback_style == "blackflash":
                    eff = f"drawbox=x=0:y=0:w=iw:h=ih:color=black@1.0:t=fill:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                elif fallback_style == "pulse":
                    eff = f"eq=saturation={float(pulse_saturation):.3f}:brightness={float(pulse_brightness):.3f}:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                elif fallback_style == "bloom":
                    eff = f"gblur=sigma={float(bloom_sigma):.2f}:steps=1:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                if eff:
                    # Apply effect and optionally mask it
                    eff_label = f'eff{i}'
                    filters.append(f'[{last_label}]{eff}[{eff_label}]')
                    if use_masks and mask_scope in ("foreground", "background"):
                        # Use alphamerge+overlay to avoid grayscale artifacts
                        base_rgba = f'br{i}'
                        eff_rgba = f'er{i}'
                        eff_with_alpha = f'eam{i}'
                        filters.append(f'[{last_label}]format=rgba[{base_rgba}]')
                        filters.append(f'[{eff_label}]format=rgba[{eff_rgba}]')
                        mask_to_use = f'{mask_last_label}'
                        if mask_scope == "background":
                            inv_label = f'minv{i}'
                            filters.append(f'[{mask_last_label}]negate,format=gray[{inv_label}]')
                            mask_to_use = inv_label
                        filters.append(f'[{eff_rgba}][{mask_to_use}]alphamerge[{eff_with_alpha}]')
                        styled_label = f'sty{i}'
                        # Overlay effect (with mask alpha) onto base
                        filters.append(f'[{base_rgba}][{eff_with_alpha}]overlay=shortest=1:format=auto[{styled_label}]')
                        last_label = styled_label
                    else:
                        last_label = eff_label

            filters.append(f'[{last_label}][s{i}]concat=n=2:v=1:a=0[{out_label}]')
            transition_times.append(boundary_t)
            last_label = out_label
            prev_duration = prev_duration + curr_d
            # Mask chain concat in parallel
            if use_masks:
                m_out_label = f'mv{i}'
                filters.append(f'[{mask_last_label}][m{i}]concat=n=2:v=1:a=0[{m_out_label}]')
                mask_last_label = m_out_label
        else:
            if align == "midpoint":
                offset = max(0.0, prev_duration - (td_eff / 2.0))
            else:
                offset = max(0.0, prev_duration - td_eff)
            out_label = f'v{i}'
            filters.append(
                f'[{last_label}][s{i}]xfade=transition={transition_type}:duration={td_eff:.3f}:offset={offset:.3f}[{out_label}]'
            )
            # The perceptual on-beat moment is at prev_duration for both align modes
            transition_times.append(prev_duration)
            last_label = out_label
            prev_duration = prev_duration + curr_d - td_eff
            if use_masks:
                m_out_label = f'mv{i}'
                # Use simple fade for masks to align with visual transition
                filters.append(
                    f'[{mask_last_label}][m{i}]xfade=transition=fade:duration={td_eff:.3f}:offset={offset:.3f}[{m_out_label}]'
                )
                mask_last_label = m_out_label

    if count == 1:
        last_label = 's0'
        if use_masks:
            mask_last_label = 'm0'

    # Build list of overlay times: prefer true beat times if provided; otherwise use xfade landing times
    overlay_times = []
    if overlay_beats:
        # Apply optional phase and downsample by multiplier (every Nth beat)
        for idx, bt in enumerate(overlay_beats, start=1):
            if overlay_beat_multiplier > 1 and (idx % overlay_beat_multiplier) != 0:
                continue
            overlay_times.append(max(0.0, bt + overlay_phase))
    else:
        overlay_times = list(transition_times)

    # Optional overlays (ticks/pulses/counter) after the xfade chain
    final_label = last_label
    overlay_chain_parts = []
    if overlay_times:
        # Optionally exclude overlays that are too close to transition landing times
        if overlay_guard_seconds > 0 and transition_times:
            guarded = []
            for bt in overlay_times:
                if all(abs(bt - xt) >= overlay_guard_seconds for xt in transition_times):
                    guarded.append(bt)
            overlay_times = guarded

        # Separate draw overlays (ticks/counter) from effect overlays (pulse/bloom)
        draw_parts = []
        effect_parts = []

        # Cut markers first (drawn underneath beat markers)
        if mark_cuts and transition_times and marker_duration > 0:
            for tt in transition_times:
                draw_parts.append(
                    f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=red@1.0:t=fill:enable='between(t,{tt:.3f},{(tt+marker_duration):.3f})'"
                )

        # Beat tick markers (white), only when explicitly requested
        if mark_transitions and marker_duration > 0:
            for tt in overlay_times:
                draw_parts.append(
                    f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=white@1.0:t=fill:enable='between(t,{tt:.3f},{(tt+marker_duration):.3f})'"
                )

        # Pulse effects on background/foreground only
        if pulse and pulse_duration > 0 and (pulse_saturation > 1.0 or pulse_brightness != 0.0):
            for tt in overlay_times:
                effect_parts.append(
                    f"eq=saturation={float(pulse_saturation):.3f}:brightness={float(pulse_brightness):.3f}:enable='between(t,{tt:.3f},{(tt+pulse_duration):.3f})'"
                )
        # Bloom glow
        if bloom and bloom_duration > 0 and bloom_sigma > 0:
            for tt in overlay_times:
                effect_parts.append(
                    f"gblur=sigma={float(bloom_sigma):.2f}:steps=1:enable='between(t,{tt:.3f},{(tt+bloom_duration):.3f})'"
                )

        # Sticky numeric beat counter (absolute timeline)
        if counter_beats and counter_fontsize > 0:
            try:
                # Position presets
                if counter_position == "tr":
                    x_expr = "w-tw-20"; y_expr = "20"
                elif counter_position == "tl":
                    x_expr = "20"; y_expr = "20"
                elif counter_position == "br":
                    x_expr = "w-tw-20"; y_expr = "h-th-20"
                else:
                    x_expr = "20"; y_expr = "h-th-20"

                numbered_beats = sorted([t for t in overlay_times if t >= 0.0])

                if numbered_beats:
                    first_bt = max(0.0, numbered_beats[0])
                    if first_bt > 0:
                        draw_parts.append(
                            "drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
                            f":text='0':x={x_expr}:y={y_expr}:fontsize={int(counter_fontsize)}:fontcolor=white:"
                            f"bordercolor=black:borderw=2:enable='between(t,0,{first_bt:.3f})'"
                        )

                for j, bt in enumerate(numbered_beats):
                    start_t = max(0.0, bt)
                    end_t = prev_duration if j + 1 >= len(numbered_beats) else max(0.0, numbered_beats[j + 1])
                    label = j + 1
                    draw_parts.append(
                        "drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
                        f":text='{label}':x={x_expr}:y={y_expr}:fontsize={int(counter_fontsize)}:fontcolor=white:"
                        f"bordercolor=black:borderw=2:enable='between(t,{start_t:.3f},{end_t:.3f})'"
                    )
            except Exception:
                pass

        # Build split -> effects -> maskedmerge -> draws pipeline
        base_label = 'ob'
        eff_in_label = 'oe'
        eff_out_label = 'oeo'
        merged_label = 'om'
        # Split the last_label into base/effect branches
        # Ensure color space suitable; keep full color (rgba) for alpha overlays
        filters.append(f'[{last_label}]format=rgba,split=2[{base_label}][{eff_in_label}]')
        if effect_parts:
            filters.append(f'[{eff_in_label}]{",".join(effect_parts)}[{eff_out_label}]')
        else:
            # No effects, just forward
            eff_out_label = eff_in_label

        # Choose mask (invert for background scope)
        mask_to_use = mask_last_label if use_masks else None
        if use_masks and mask_scope in ("foreground", "background"):
            if mask_scope == "background":
                inv_label = 'm_over_inv'
                filters.append(f'[{mask_last_label}]negate,format=gray[{inv_label}]')
                mask_to_use = inv_label
            # Alpha merge effect branch with mask, then overlay onto base
            eff_alpha = 'eff_over_alpha'
            filters.append(f'[{eff_out_label}][{mask_to_use}]alphamerge[{eff_alpha}]')
            filters.append(f'[{base_label}][{eff_alpha}]overlay=shortest=1:format=auto[{merged_label}]')
            work_label = merged_label
        else:
            work_label = eff_out_label

        # Apply draw overlays on top of merged output
        final_label = work_label
        if draw_parts:
            out_draw_label = 'od'
            filters.append(f'[{work_label}]{",".join(draw_parts)}[{out_draw_label}]')
            final_label = out_draw_label

    filter_complex = ';'.join(filters)

    # Write complex filter to a temp script file to avoid command-length limits
    filter_script_path = None
    try:
        with tempfile.NamedTemporaryFile('w', suffix='.fffilter', delete=False) as tf:
            tf.write(filter_complex)
            filter_script_path = tf.name
    except Exception:
        # Fallback to inline if tempfile fails (rare)
        filter_script_path = None

    nvenc_available = detect_nvenc_support()
    enc = get_encoding_params(nvenc_available, fps)

    if filter_script_path:
        cmd = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex_script "{filter_script_path}" '
            f'-map [{final_label}] {enc} -pix_fmt yuv420p "{output_file}"'
        )
        ok = run_command(cmd, "Beat-aligned transitions", show_output=True, timeout_seconds=300)
    else:
        cmd = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex "{filter_complex}" '
            f'-map [{final_label}] {enc} -pix_fmt yuv420p "{output_file}"'
        )
        ok = run_command(cmd, "Beat-aligned transitions", show_output=True, timeout_seconds=300)
    if ok:
        return True
    # CPU fallback if NVENC path failed
    cpu_enc = get_encoding_params(False, fps)
    if filter_script_path:
        cmd_cpu = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex_script "{filter_script_path}" '
            f'-map [{final_label}] {cpu_enc} -pix_fmt yuv420p "{output_file}"'
        )
    else:
        cmd_cpu = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex "{filter_complex}" '
            f'-map [{final_label}] {cpu_enc} -pix_fmt yuv420p "{output_file}"'
        )
    ok_cpu = run_command(cmd_cpu, "Beat-aligned transitions (CPU fallback)", show_output=True, timeout_seconds=300)
    # Cleanup temp filter script
    try:
        if filter_script_path:
            os.remove(filter_script_path)
    except Exception:
        pass
    return ok_cpu



def create_beat_aligned_with_transitions(
    images,
    durations,
    output_file,
    *,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    fps=DEFAULT_FPS,
    quantize: str = "nearest",
    transition_type: str = "fade",
    transition_duration: float = DEFAULT_TRANSITION_DURATION,
    align: str = "midpoint",
    min_effective: float = 0.25,
    # debug overlays
    mark_transitions: bool = False,
    marker_duration: float = 0.12,
    pulse: bool = False,
    pulse_duration: float = 0.08,
    pulse_saturation: float = 1.25,
    pulse_brightness: float = 0.00,
    bloom: bool = False,
    bloom_sigma: float = 8.0,
    bloom_duration: float = 0.08,
    overlay_beats=None,
    overlay_beat_multiplier: int = 1,
    overlay_phase: float = 0.0,
    overlay_guard_seconds: float = 0.0,
    mark_cuts: bool = False,
    # numeric counter overlay
    counter_beats=None,
    counter_fontsize: int = 36,
    counter_position: str = "tr",
    # per-boundary fallback styling
    fallback_style: str = "none",
    fallback_duration: float = 0.06,
    mask_scope: str = "none",
    workers: int = 1,
):
    """Create a slideshow with xfade transitions aligned to beat-planned segment durations.

    Safety: If any effective transition duration would be too small (< min_effective)
    for a given adjacent segment pair, fallback to hardcuts for the entire render.
    """
    if not images:
        print("No images found!")
        return False

    count = min(len(images), len(durations))
    images = images[:count]
    durations = [max(0.1, float(d)) for d in durations[:count]]
    # Quantize durations to exact frame boundaries for precise cut alignment
    q_durations = []
    for d in durations:
        if quantize == "floor":
            frames = max(1, int(float(d) * fps))
        elif quantize == "ceil":
            frames = max(1, int((float(d) * fps) + 0.999999))
        else:
            frames = max(1, int(round(float(d) * fps)))
        q_durations.append(max(1.0 / fps, frames / float(fps)))
    durations = q_durations

    # Safety check: if any pair too short for xfade with reasonable effect, fallback
    too_short = False
    for i in range(1, count):
        prev_d = durations[i - 1]
        curr_d = durations[i]
        td_eff = min(max(0.05, 0.5), max(0.05, prev_d - 0.05), max(0.05, curr_d - 0.05))
        if td_eff < 0.25:
            too_short = True
            break
    if too_short:
        print("⚠️ Segments too short for safe xfade; falling back to hard cuts.")
        # Preserve overlays/masks/counters in fallback path
        return create_slideshow_with_durations(
            images,
            durations,
            output_file,
            width=width,
            height=height,
            fps=fps,
            quantize=quantize,
            visualize_cuts=bool(mark_transitions or mark_cuts),
            marker_duration=marker_duration,
            beat_markers=overlay_beats,
            pulse_beats=overlay_beats if pulse else None,
            pulse_duration=pulse_duration,
            pulse_saturation=pulse_saturation,
            pulse_brightness=pulse_brightness,
            pulse_bloom=bloom,
            pulse_bloom_sigma=bloom_sigma,
            pulse_bloom_duration=bloom_duration,
            counter_beats=counter_beats,
            counter_fontsize=counter_fontsize,
            counter_position=counter_position,
            mask_scope=mask_scope,
            workers=workers,
        )

    # Unified approach: Always generate individual clips then concat
    # No arbitrary limits - scales to any number of images

    # Build ffmpeg inputs: looped stills with explicit -t (and optional masks)
    input_args = []
    use_masks = False
    masks = []
    if mask_scope in ("foreground", "background"):
        # Prefer precomputed masks next to images or in a sibling 'masks/' directory
        found_all = True
        tentative_masks = []
        for img in images:
            base, ext = os.path.splitext(img)
            filename = os.path.basename(img)
            name_no_ext, _ = os.path.splitext(filename)
            candidates = [
                f"{base}_mask.png",
                os.path.join(os.path.dirname(img), "masks", f"{name_no_ext}_mask.png"),
            ]
            chosen = None
            for cand in candidates:
                if os.path.exists(cand):
                    chosen = cand
                    break
            if chosen is None:
                found_all = False
                tentative_masks.append(None)
            else:
                tentative_masks.append(chosen)
        if found_all and tentative_masks:
            masks = tentative_masks  # type: ignore
            use_masks = True
        else:
            # Avoid heavy init during tests; try rembg generation only if needed
            if not os.environ.get("PYTEST_CURRENT_TEST"):
                try:
                    from .background_removal import BackgroundRemover  # type: ignore
                    remover = BackgroundRemover(gpu_acceleration=False)
                    if remover.is_available():
                        gen_masks = []
                        for img in images:
                            m = remover.create_mask(img, None)
                            gen_masks.append(m)
                        if all(bool(m) for m in gen_masks) and len(gen_masks) == len(images):
                            masks = gen_masks  # type: ignore
                            use_masks = True
                    else:
                        use_masks = False
                except Exception:
                    use_masks = False
    for img, d in zip(images, durations):
        input_args.append(f'-loop 1 -t {d:.3f} -i "{img}"')
    if use_masks:
        for m, d in zip(masks, durations):
            input_args.append(f'-loop 1 -t {d:.3f} -i "{m}"')

    # Filters: scale/pad each input to labeled stream sN (and optional masks to mN)
    scale_parts = []
    for idx in range(count):
        scale_parts.append(
            f'[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[s{idx}]'
        )
    filters = [';'.join(scale_parts)]  # start filter graph with scaling chain
    if use_masks:
        mask_scale_parts = []
        for idx in range(count):
            # mask inputs start after image inputs
            midx = count + idx
            mask_scale_parts.append(
                f'[{midx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,'
                f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=gray[m{idx}]'
            )
        filters.append(';'.join(mask_scale_parts))

    # Create chained xfade graph with offsets aligned near the beat
    prev_label = 's0'
    prev_duration = durations[0]
    last_label = prev_label
    # Parallel mask chain
    if use_masks:
        mask_prev_label = 'm0'
        mask_last_label = mask_prev_label
    transition_times = []  # absolute times (seconds) when the beat-aligned transition should "land"
    for i in range(1, count):
        curr_d = durations[i]
        td_eff = min(max(0.05, transition_duration), max(0.05, prev_duration - 0.05), max(0.05, curr_d - 0.05))
        if td_eff < 0.25:
            # Per-segment fallback: hardcut concat with optional micro-effect at boundary
            out_label = f'v{i}'
            boundary_t = prev_duration
            if fallback_style != "none" and fallback_duration > 0:
                # Build a tiny overlay chain on last_label before concat
                eff = None
                if fallback_style == "whitepop":
                    eff = f"drawbox=x=0:y=0:w=iw:h=ih:color=white@1.0:t=fill:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                elif fallback_style == "blackflash":
                    eff = f"drawbox=x=0:y=0:w=iw:h=ih:color=black@1.0:t=fill:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                elif fallback_style == "pulse":
                    eff = f"eq=saturation={float(pulse_saturation):.3f}:brightness={float(pulse_brightness):.3f}:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                elif fallback_style == "bloom":
                    eff = f"gblur=sigma={float(bloom_sigma):.2f}:steps=1:enable='between(t,{boundary_t:.3f},{(boundary_t+fallback_duration):.3f})'"
                if eff:
                    # Apply effect and optionally mask it
                    eff_label = f'eff{i}'
                    filters.append(f'[{last_label}]{eff}[{eff_label}]')
                    if use_masks and mask_scope in ("foreground", "background"):
                        # Use alphamerge+overlay to avoid grayscale artifacts
                        base_rgba = f'br{i}'
                        eff_rgba = f'er{i}'
                        eff_with_alpha = f'eam{i}'
                        filters.append(f'[{last_label}]format=rgba[{base_rgba}]')
                        filters.append(f'[{eff_label}]format=rgba[{eff_rgba}]')
                        mask_to_use = f'{mask_last_label}'
                        if mask_scope == "background":
                            inv_label = f'minv{i}'
                            filters.append(f'[{mask_last_label}]negate,format=gray[{inv_label}]')
                            mask_to_use = inv_label
                        filters.append(f'[{eff_rgba}][{mask_to_use}]alphamerge[{eff_with_alpha}]')
                        styled_label = f'sty{i}'
                        # Overlay effect (with mask alpha) onto base
                        filters.append(f'[{base_rgba}][{eff_with_alpha}]overlay=shortest=1:format=auto[{styled_label}]')
                        last_label = styled_label
                    else:
                        last_label = eff_label

            filters.append(f'[{last_label}][s{i}]concat=n=2:v=1:a=0[{out_label}]')
            transition_times.append(boundary_t)
            last_label = out_label
            prev_duration = prev_duration + curr_d
            # Mask chain concat in parallel
            if use_masks:
                m_out_label = f'mv{i}'
                filters.append(f'[{mask_last_label}][m{i}]concat=n=2:v=1:a=0[{m_out_label}]')
                mask_last_label = m_out_label
        else:
            if align == "midpoint":
                offset = max(0.0, prev_duration - (td_eff / 2.0))
            else:
                offset = max(0.0, prev_duration - td_eff)
            out_label = f'v{i}'
            filters.append(
                f'[{last_label}][s{i}]xfade=transition={transition_type}:duration={td_eff:.3f}:offset={offset:.3f}[{out_label}]'
            )
            # The perceptual on-beat moment is at prev_duration for both align modes
            transition_times.append(prev_duration)
            last_label = out_label
            prev_duration = prev_duration + curr_d - td_eff
            if use_masks:
                m_out_label = f'mv{i}'
                # Use simple fade for masks to align with visual transition
                filters.append(
                    f'[{mask_last_label}][m{i}]xfade=transition=fade:duration={td_eff:.3f}:offset={offset:.3f}[{m_out_label}]'
                )
                mask_last_label = m_out_label

    if count == 1:
        last_label = 's0'
        if use_masks:
            mask_last_label = 'm0'

    # Build list of overlay times: prefer true beat times if provided; otherwise use xfade landing times
    overlay_times = []
    if overlay_beats:
        # Apply optional phase and downsample by multiplier (every Nth beat)
        for idx, bt in enumerate(overlay_beats, start=1):
            if overlay_beat_multiplier > 1 and (idx % overlay_beat_multiplier) != 0:
                continue
            overlay_times.append(max(0.0, bt + overlay_phase))
    else:
        overlay_times = list(transition_times)

    # Optional overlays (ticks/pulses/counter) after the xfade chain
    final_label = last_label
    overlay_chain_parts = []
    if overlay_times:
        # Optionally exclude overlays that are too close to transition landing times
        if overlay_guard_seconds > 0 and transition_times:
            guarded = []
            for bt in overlay_times:
                if all(abs(bt - xt) >= overlay_guard_seconds for xt in transition_times):
                    guarded.append(bt)
            overlay_times = guarded

        # Separate draw overlays (ticks/counter) from effect overlays (pulse/bloom)
        draw_parts = []
        effect_parts = []

        # Cut markers first (drawn underneath beat markers)
        if mark_cuts and transition_times and marker_duration > 0:
            for tt in transition_times:
                draw_parts.append(
                    f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=red@1.0:t=fill:enable='between(t,{tt:.3f},{(tt+marker_duration):.3f})'"
                )

        # Beat tick markers (white), only when explicitly requested
        if mark_transitions and marker_duration > 0:
            for tt in overlay_times:
                draw_parts.append(
                    f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=white@1.0:t=fill:enable='between(t,{tt:.3f},{(tt+marker_duration):.3f})'"
                )

        # Pulse effects on background/foreground only
        if pulse and pulse_duration > 0 and (pulse_saturation > 1.0 or pulse_brightness != 0.0):
            for tt in overlay_times:
                effect_parts.append(
                    f"eq=saturation={float(pulse_saturation):.3f}:brightness={float(pulse_brightness):.3f}:enable='between(t,{tt:.3f},{(tt+pulse_duration):.3f})'"
                )
        # Bloom glow
        if bloom and bloom_duration > 0 and bloom_sigma > 0:
            for tt in overlay_times:
                effect_parts.append(
                    f"gblur=sigma={float(bloom_sigma):.2f}:steps=1:enable='between(t,{tt:.3f},{(tt+bloom_duration):.3f})'"
                )

        # Sticky numeric beat counter (absolute timeline)
        if counter_beats and counter_fontsize > 0:
            try:
                # Position presets
                if counter_position == "tr":
                    x_expr = "w-tw-20"; y_expr = "20"
                elif counter_position == "tl":
                    x_expr = "20"; y_expr = "20"
                elif counter_position == "br":
                    x_expr = "w-tw-20"; y_expr = "h-th-20"
                else:
                    x_expr = "20"; y_expr = "h-th-20"

                numbered_beats = sorted([t for t in overlay_times if t >= 0.0])

                if numbered_beats:
                    first_bt = max(0.0, numbered_beats[0])
                    if first_bt > 0:
                        draw_parts.append(
                            "drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
                            f":text='0':x={x_expr}:y={y_expr}:fontsize={int(counter_fontsize)}:fontcolor=white:"
                            f"bordercolor=black:borderw=2:enable='between(t,0,{first_bt:.3f})'"
                        )

                for j, bt in enumerate(numbered_beats):
                    start_t = max(0.0, bt)
                    end_t = prev_duration if j + 1 >= len(numbered_beats) else max(0.0, numbered_beats[j + 1])
                    label = j + 1
                    draw_parts.append(
                        "drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
                        f":text='{label}':x={x_expr}:y={y_expr}:fontsize={int(counter_fontsize)}:fontcolor=white:"
                        f"bordercolor=black:borderw=2:enable='between(t,{start_t:.3f},{end_t:.3f})'"
                    )
            except Exception:
                pass

        # Build split -> effects -> maskedmerge -> draws pipeline
        base_label = 'ob'
        eff_in_label = 'oe'
        eff_out_label = 'oeo'
        merged_label = 'om'
        # Split the last_label into base/effect branches
        # Ensure color space suitable; keep full color (rgba) for alpha overlays
        filters.append(f'[{last_label}]format=rgba,split=2[{base_label}][{eff_in_label}]')
        if effect_parts:
            filters.append(f'[{eff_in_label}]{",".join(effect_parts)}[{eff_out_label}]')
        else:
            # No effects, just forward
            eff_out_label = eff_in_label

        # Choose mask (invert for background scope)
        mask_to_use = mask_last_label if use_masks else None
        if use_masks and mask_scope in ("foreground", "background"):
            if mask_scope == "background":
                inv_label = 'm_over_inv'
                filters.append(f'[{mask_last_label}]negate,format=gray[{inv_label}]')
                mask_to_use = inv_label
            # Alpha merge effect branch with mask, then overlay onto base
            eff_alpha = 'eff_over_alpha'
            filters.append(f'[{eff_out_label}][{mask_to_use}]alphamerge[{eff_alpha}]')
            filters.append(f'[{base_label}][{eff_alpha}]overlay=shortest=1:format=auto[{merged_label}]')
            work_label = merged_label
        else:
            work_label = eff_out_label

        # Apply draw overlays on top of merged output
        final_label = work_label
        if draw_parts:
            out_draw_label = 'od'
            filters.append(f'[{work_label}]{",".join(draw_parts)}[{out_draw_label}]')
            final_label = out_draw_label

    filter_complex = ';'.join(filters)

    # Write complex filter to a temp script file to avoid command-length limits
    filter_script_path = None
    try:
        with tempfile.NamedTemporaryFile('w', suffix='.fffilter', delete=False) as tf:
            tf.write(filter_complex)
            filter_script_path = tf.name
    except Exception:
        # Fallback to inline if tempfile fails (rare)
        filter_script_path = None

    nvenc_available = detect_nvenc_support()
    enc = get_encoding_params(nvenc_available, fps)

    if filter_script_path:
        cmd = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex_script "{filter_script_path}" '
            f'-map [{final_label}] {enc} -pix_fmt yuv420p "{output_file}"'
        )
        ok = run_command(cmd, "Beat-aligned transitions", show_output=True, timeout_seconds=300)
    else:
        cmd = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex "{filter_complex}" '
            f'-map [{final_label}] {enc} -pix_fmt yuv420p "{output_file}"'
        )
        ok = run_command(cmd, "Beat-aligned transitions", show_output=True, timeout_seconds=300)
    if ok:
        return True
    # CPU fallback if NVENC path failed
    cpu_enc = get_encoding_params(False, fps)
    if filter_script_path:
        cmd_cpu = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex_script "{filter_script_path}" '
            f'-map [{final_label}] {cpu_enc} -pix_fmt yuv420p "{output_file}"'
        )
    else:
        cmd_cpu = (
            f'ffmpeg -y {" ".join(input_args)} -filter_complex "{filter_complex}" '
            f'-map [{final_label}] {cpu_enc} -pix_fmt yuv420p "{output_file}"'
        )
    ok_cpu = run_command(cmd_cpu, "Beat-aligned transitions (CPU fallback)", show_output=True, timeout_seconds=300)
    # Cleanup temp filter script
    try:
        if filter_script_path:
            os.remove(filter_script_path)
    except Exception:
        pass
    return ok_cpu


