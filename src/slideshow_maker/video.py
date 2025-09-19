#!/usr/bin/env python3
"""
Video processing for the VRChat Slideshow Maker
"""

import os
import random
import shutil
from .config import (
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS, DEFAULT_CRF, DEFAULT_PRESET,
    DEFAULT_MIN_DURATION, DEFAULT_MAX_DURATION, DEFAULT_TRANSITION_DURATION,
    DEFAULT_CHUNK_SIZE, VIDEO_OUTPUT, TEMP_DIR
)
from .transitions import get_random_transition
from .utils import run_command, get_image_info, get_available_transitions, print_ffmpeg_capabilities, detect_nvenc_support


def get_encoding_params(nvenc_available, fps):
    """Get encoding parameters based on available hardware"""
    if nvenc_available:
        return f"-c:v h264_nvenc -r {fps} -rc vbr -b:v 10M -maxrate 20M -bufsize 20M -preset p5"
    else:
        return f"-c:v libx264 -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET}"


def create_slideshow(images, output_file, min_duration=DEFAULT_MIN_DURATION, 
                    max_duration=DEFAULT_MAX_DURATION, width=DEFAULT_WIDTH, 
                    height=DEFAULT_HEIGHT, fps=DEFAULT_FPS, temp_dir=None):
    """Create slideshow video from images with smooth transitions using FFmpeg xfade"""

    if len(images) == 0:
        print("No images found!")
        return False

    if len(images) == 1:
        # Single image - just create a video with random duration
        duration = random.uniform(min_duration, max_duration)
        cmd = f'ffmpeg -y -loop 1 -i "{images[0]}" -t {duration:.1f} -vf "scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -r {fps} "{output_file}"'
        return run_command(cmd, f"Creating single image video from {images[0]}")

    print(f"🎬 Creating slideshow with {len(images)} images and smooth transitions...")

    # Use chunked approach with crossfades between chunks
    return create_slideshow_chunked(images, output_file, min_duration, max_duration, width, height, fps, temp_dir)


def create_slideshow_with_durations(
    images,
    durations,
    output_file,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    fps=DEFAULT_FPS,
    temp_dir=None,
    visualize_cuts: bool = False,
    marker_duration: float = 0.12,
    beat_markers=None,
    pulse_beats=None,
    pulse_duration: float = 0.08,
    pulse_saturation: float = 1.25,
    pulse_brightness: float = 0.00,
    pulse_bloom: bool = False,
    pulse_bloom_sigma: float = 8.0,
    pulse_bloom_duration: float = 0.08,
    counter_beats=None,
    counter_fontsize: int = 36,
    counter_position: str = "tr",
    cut_markers=None,
):
    """Create a slideshow where each image uses an explicit duration (no transitions).

    Minimal, reliable path to support beat-aligned segment lengths. Transitions will
    be added in a later phase; this function focuses on honoring exact durations.
    """
    if len(images) == 0:
        print("No images found!")
        return False

    if temp_dir is None:
        temp_dir = ".slideshow_tmp"
    os.makedirs(temp_dir, exist_ok=True)

    # Trim to matching counts
    count = min(len(images), len(durations))
    images = images[:count]
    durations = durations[:count]

    temp_clips = []
    print(f"🎬 Creating fixed-duration clips for {count} images...")

    elapsed = 0.0
    for i, (img, dur) in enumerate(zip(images, durations)):
        # Quantize duration to exact frame count to keep cuts on frame boundaries
        frames = max(1, int(round(float(dur) * fps)))
        dur = max(1.0 / fps, frames / float(fps))

        clip_path = f"{temp_dir}/clip_{i:04d}.mp4"
        vf_parts = [
            f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        ]

        # Debug cut marker at clip start (except first)
        if visualize_cuts and i > 0 and marker_duration > 0:
            vf_parts.append(
                f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=white@1.0:t=fill:enable='between(t,0,{marker_duration:.3f})'"
            )

        # Beat markers across the clip
        if beat_markers:
            try:
                for bt in beat_markers:
                    if bt < elapsed:
                        continue
                    if bt >= elapsed + dur:
                        break
                    rel_t = max(0.0, bt - elapsed)
                    vf_parts.append(
                        f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=white@1.0:t=fill:enable='between(t,{rel_t:.3f},{(rel_t+marker_duration):.3f})'"
                    )
            except Exception:
                pass

        # Selected cut markers (distinct color) - draw slightly before clip end
        if cut_markers:
            try:
                for ct in cut_markers:
                    if ct <= elapsed:
                        continue
                    if ct > elapsed + dur:
                        break
                    rel_t = max(0.0, ct - elapsed)
                    rel_t = min(max(0.0, rel_t - 0.02), max(0.0, dur - 0.02))
                    vf_parts.append(
                        f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=red@1.0:t=fill:enable='between(t,{rel_t:.3f},{(rel_t+marker_duration):.3f})'"
                    )
            except Exception:
                pass

        # Pulse saturation/brightness at beats
        if pulse_beats and pulse_duration > 0 and (pulse_saturation > 1.0 or pulse_brightness != 0.0):
            try:
                for bt in pulse_beats:
                    if bt < elapsed:
                        continue
                    if bt >= elapsed + dur:
                        break
                    rel_t = max(0.0, bt - elapsed)
                    vf_parts.append(
                        f"eq=saturation={float(pulse_saturation):.3f}:brightness={float(pulse_brightness):.3f}:enable='between(t,{rel_t:.3f},{(rel_t+pulse_duration):.3f})'"
                    )
            except Exception:
                pass

        # Bloom pulse via gaussian blur
        if pulse_bloom and pulse_bloom_duration > 0 and pulse_bloom_sigma > 0:
            try:
                beats_for_bloom = pulse_beats or beat_markers or []
                for bt in beats_for_bloom:
                    if bt < elapsed:
                        continue
                    if bt >= elapsed + dur:
                        break
                    rel_t = max(0.0, bt - elapsed)
                    vf_parts.append(
                        f"gblur=sigma={float(pulse_bloom_sigma):.2f}:steps=1:enable='between(t,{rel_t:.3f},{(rel_t+pulse_bloom_duration):.3f})'"
                    )
            except Exception:
                pass

        # Sticky numeric beat counter
        if counter_beats and counter_fontsize > 0:
            try:
                beats_in_order = list(counter_beats)
                # Count beats strictly before this clip
                count_before = 0
                first_idx_in_clip = None
                for idx_b, b in enumerate(beats_in_order):
                    if b < elapsed:
                        count_before += 1
                    else:
                        first_idx_in_clip = idx_b
                        break

                # Position presets
                if counter_position == "tr":
                    x_expr = "w-tw-20"; y_expr = "20"
                elif counter_position == "tl":
                    x_expr = "20"; y_expr = "20"
                elif counter_position == "br":
                    x_expr = "w-tw-20"; y_expr = "h-th-20"
                else:
                    x_expr = "20"; y_expr = "h-th-20"

                # Carry previous number until first beat in clip
                first_rel = None
                if first_idx_in_clip is not None and first_idx_in_clip < len(beats_in_order):
                    first_rel = max(0.0, beats_in_order[first_idx_in_clip] - elapsed)
                if count_before > 0 and first_rel is not None and first_rel > 0:
                    prev_idx = count_before
                    vf_parts.append(
                        "drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
                        f":text='{prev_idx}':x={x_expr}:y={y_expr}:fontsize={int(counter_fontsize)}:fontcolor=white:"
                        f"bordercolor=black:borderw=2:enable='between(t,0,{first_rel:.3f})'"
                    )

                # Per-beat number until next beat (or clip end)
                local_beats = []
                for bt in beats_in_order:
                    if bt < elapsed:
                        continue
                    if bt >= elapsed + dur:
                        break
                    local_beats.append(bt)

                for j, bt in enumerate(local_beats):
                    rel_t = max(0.0, bt - elapsed)
                    rel_next = dur if j + 1 >= len(local_beats) else max(0.0, local_beats[j + 1] - elapsed)
                    idx = count_before + j + 1
                    vf_parts.append(
                        "drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'"
                        f":text='{idx}':x={x_expr}:y={y_expr}:fontsize={int(counter_fontsize)}:fontcolor=white:"
                        f"bordercolor=black:borderw=2:enable='between(t,{rel_t:.3f},{rel_next:.3f})'"
                    )
            except Exception:
                pass

        vf_filter = ",".join(vf_parts)
        cmd = (
            f'ffmpeg -y -loop 1 -i "{img}" -t {float(dur):.3f} '
            f'-vf "{vf_filter}" -frames:v {frames} -c:v libx264 -r {fps} "{clip_path}"'
        )
        if not run_command(cmd, f"Clip {i+1}/{count} ({dur:.2f}s)"):
            return False
        temp_clips.append(clip_path)
        elapsed += float(dur)

    # Concat
    if len(temp_clips) == 1:
        os.rename(temp_clips[0], output_file)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return True

    concat_list = f"{temp_dir}/concat.txt"
    with open(concat_list, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" -c copy "{output_file}"'
    ok = run_command(cmd, "Concatenating fixed-duration clips")

    shutil.rmtree(temp_dir, ignore_errors=True)
    return ok


def create_beat_aligned_with_transitions(
    images,
    durations,
    output_file,
    *,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    fps=DEFAULT_FPS,
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

    # Safety check: if any pair too short for xfade with reasonable effect, fallback
    too_short = False
    for i in range(1, count):
        prev_d = durations[i - 1]
        curr_d = durations[i]
        td_eff = min(max(0.05, transition_duration), max(0.05, prev_d - 0.05), max(0.05, curr_d - 0.05))
        if td_eff < min_effective:
            too_short = True
            break
    if too_short:
        print("⚠️ Segments too short for safe xfade; falling back to hard cuts.")
        return create_slideshow_with_durations(
            images,
            durations,
            output_file,
            width=width,
            height=height,
            fps=fps,
        )

    # Build ffmpeg inputs: looped stills with explicit -t
    input_args = []
    for img, d in zip(images, durations):
        input_args.append(f'-loop 1 -t {d:.3f} -i "{img}"')

    # Filters: scale/pad each input to labeled stream sN
    scale_parts = []
    for idx in range(count):
        scale_parts.append(
            f'[{idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p[s{idx}]'
        )
    filters = [';'.join(scale_parts)]  # start filter graph with scaling chain

    # Create chained xfade graph with offsets aligned near the beat
    prev_label = 's0'
    prev_duration = durations[0]
    last_label = prev_label
    transition_times = []  # absolute times (seconds) when the beat-aligned transition should "land"
    for i in range(1, count):
        curr_d = durations[i]
        td_eff = min(max(0.05, transition_duration), max(0.05, prev_duration - 0.05), max(0.05, curr_d - 0.05))
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

    if count == 1:
        last_label = 's0'

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

    # Optional overlays (ticks/pulses) after the xfade chain
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

        # Cut markers first (drawn underneath beat markers)
        if mark_cuts and transition_times and marker_duration > 0:
            for tt in transition_times:
                overlay_chain_parts.append(
                    f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=red@1.0:t=fill:enable='between(t,{tt:.3f},{(tt+marker_duration):.3f})'"
                )

        # Beat tick markers (white), drawn after to appear on top
        if (mark_transitions or overlay_beats) and marker_duration > 0:
            for tt in overlay_times:
                overlay_chain_parts.append(
                    f"drawbox=x=(iw/2-5):y=0:w=10:h=ih:color=white@1.0:t=fill:enable='between(t,{tt:.3f},{(tt+marker_duration):.3f})'"
                )
        # Pulse
        if pulse and pulse_duration > 0 and (pulse_saturation > 1.0 or pulse_brightness != 0.0):
            for tt in overlay_times:
                overlay_chain_parts.append(
                    f"eq=saturation={float(pulse_saturation):.3f}:brightness={float(pulse_brightness):.3f}:enable='between(t,{tt:.3f},{(tt+pulse_duration):.3f})'"
                )
        # Bloom
        if bloom and bloom_duration > 0 and bloom_sigma > 0:
            for tt in overlay_times:
                overlay_chain_parts.append(
                    f"gblur=sigma={float(bloom_sigma):.2f}:steps=1:enable='between(t,{tt:.3f},{(tt+bloom_duration):.3f})'"
                )
        if overlay_chain_parts:
            overlay_chain = ','.join(overlay_chain_parts)
            out_overlay_label = 'vo'
            filters.append(f'[{last_label}]{overlay_chain}[{out_overlay_label}]')
            final_label = out_overlay_label

    filter_complex = ';'.join(filters)

    nvenc_available = detect_nvenc_support()
    enc = get_encoding_params(nvenc_available, fps)

    cmd = (
        f'ffmpeg -y {" ".join(input_args)} -filter_complex "{filter_complex}" '
        f'-map [{final_label}] {enc} -pix_fmt yuv420p "{output_file}"'
    )
    ok = run_command(cmd, "Beat-aligned transitions", show_output=True, timeout_seconds=300)
    if ok:
        return True
    # CPU fallback if NVENC path failed
    cpu_enc = get_encoding_params(False, fps)
    cmd_cpu = (
        f'ffmpeg -y {" ".join(input_args)} -filter_complex "{filter_complex}" '
        f'-map [{final_label}] {cpu_enc} -pix_fmt yuv420p "{output_file}"'
    )
    return run_command(cmd_cpu, "Beat-aligned transitions (CPU fallback)", show_output=True, timeout_seconds=300)

def create_slideshow_chunked(images, output_file, min_duration=DEFAULT_MIN_DURATION, 
                           max_duration=DEFAULT_MAX_DURATION, width=DEFAULT_WIDTH, 
                           height=DEFAULT_HEIGHT, fps=DEFAULT_FPS, temp_dir=None):
    """Create slideshow in very small chunks for reliability with VARIED transitions"""
    # Use much smaller chunks to avoid FFmpeg complexity limits
    chunk_size = DEFAULT_CHUNK_SIZE
    # Use specified temp directory or default
    if temp_dir is None:
        temp_dir = TEMP_DIR
    else:
        from .config import get_temp_dir
        temp_dir = get_temp_dir(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # Detect FFmpeg capabilities and get available transitions
    available_transitions, capabilities = get_available_transitions()
    nvenc_available = detect_nvenc_support()
    
    if not available_transitions:
        print("❌ No transitions available! FFmpeg xfade support not detected.")
        print("   Please install FFmpeg with xfade filter support.")
        return False

    chunk_files = []

    print(f"📦 Processing {len(images)} images in chunks of {chunk_size}")
    print(f"🎭 Using {len(available_transitions)} available FFmpeg xfade transition types!")
    
    # Print capability information
    print_ffmpeg_capabilities()
    
    if capabilities['cpu_transitions_supported'] and capabilities['gpu_transitions_supported']:
        print("✨ Both CPU and GPU transitions available - maximum variety!")
    elif capabilities['cpu_transitions_supported']:
        print("💻 Using CPU transitions only (GPU not available)")
    elif capabilities['gpu_transitions_supported']:
        print("🎮 Using GPU transitions only (CPU fallback not available)")

    # Process images in very small chunks
    for chunk_idx, chunk_start in enumerate(range(0, len(images), chunk_size)):
        chunk = images[chunk_start:chunk_start + chunk_size]
        chunk_file = f"{temp_dir}/chunk_{chunk_idx:03d}.mp4"

        # Check if chunk already exists (resume capability)
        if os.path.exists(chunk_file):
            print(f"  ⏭️  Chunk {chunk_idx + 1}/{(len(images) + chunk_size - 1) // chunk_size} already exists - skipping")
            chunk_files.append(chunk_file)
            continue

        print(f"  🔄 Processing chunk {chunk_idx + 1}/{(len(images) + chunk_size - 1) // chunk_size}")

        # Create simple concatenation without complex transitions
        # This is much more reliable than complex xfade chains
        temp_clips = []

        for i, img in enumerate(chunk):
            temp_clip = f"{temp_dir}/temp_{chunk_idx}_{i}.mp4"
            # Use variable duration for this image
            duration = random.uniform(min_duration, max_duration)

            # Show progress with image info
            if i % 2 == 0 or i == len(chunk) - 1:  # Show every other image or last one
                image_info = get_image_info(img)
                print(f"  📸 Processing: {image_info} ({duration:.1f}s)")

            # Simple scaling and padding - crossfades will be added between clips
            vf_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"

            # Use optimal encoding based on available hardware
            encoding_params = get_encoding_params(nvenc_available, fps)
            cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration:.1f} -vf "{vf_filter}" {encoding_params} "{temp_clip}"'
            if not run_command(cmd, f"    Creating image {i+1}/{len(chunk)}", show_output=False, timeout_seconds=30):
                print(f"    ⚠️  Skipping problematic image: {os.path.basename(img)}")
                continue  # Skip this image instead of failing the entire chunk
            temp_clips.append(temp_clip)

        # Check if we have any valid images in this chunk
        if len(temp_clips) == 0:
            print(f"    ⚠️  No valid images in chunk {chunk_idx + 1} - skipping")
            continue

        # Create VARIED transitions between ALL images in this chunk
        if len(temp_clips) == 1:
            # Just move single clip (use shutil.move for cross-drive compatibility)
            shutil.move(temp_clips[0], chunk_file)
        else:
            print(f"    🎭 Creating VARIED smooth transitions between {len(temp_clips)} images...")

            # ACTUAL TRANSITIONS: Create proper varied transitions
            print(f"      ✨ Creating REAL VARIED transitions")
            transition_clips = []

            for j in range(len(temp_clips)):
                if j == 0:
                    # First clip: just add it as-is
                    transition_clips.append(temp_clips[j])
                else:
                    # Create VARIED transition between previous and current
                    prev_clip = temp_clips[j-1]
                    curr_clip = temp_clips[j]
                    transition_file = f"{temp_dir}/transition_{chunk_idx}_{j}.mp4"

                    # RANDOMLY SELECT TRANSITION TYPES for maximum variety!
                    transition_type = random.choice(available_transitions)

                    # Use DRAMATIC transition - 1 second duration so it's UNMISSABLE
                    # ADD TEXT OVERLAY TO SHOW WHICH TRANSITION IS BEING USED!
                    # Try OpenCL transition first, fallback to CPU if it fails
                    if capabilities['gpu_transitions_supported']:
                        # OpenCL transition with RGBA format handling
                        cmd = f'ffmpeg -y -init_hw_device opencl=ocl:0.0 -filter_hw_device ocl -i "{prev_clip}" -i "{curr_clip}" -filter_complex "[0:v]format=rgba,hwupload=extra_hw_frames=16[0hw];[1:v]format=rgba,hwupload=extra_hw_frames=16[1hw];[0hw][1hw]xfade_opencl=transition={transition_type}:duration={DEFAULT_TRANSITION_DURATION}:offset={duration-DEFAULT_TRANSITION_DURATION:.1f},hwdownload,format=yuv420p" -c:v libx264 -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET} -t {duration:.1f} "{transition_file}"'
                    else:
                        # CPU transition with optimal encoding
                        encoding_params = get_encoding_params(nvenc_available, fps)
                        cmd = f'ffmpeg -y -i "{prev_clip}" -i "{curr_clip}" -filter_complex "[0:v][1:v]xfade=transition={transition_type}:duration={DEFAULT_TRANSITION_DURATION}:offset={duration-DEFAULT_TRANSITION_DURATION:.1f}" {encoding_params} -t {duration:.1f} "{transition_file}"'

                    print(f"      🔄 {transition_type.upper()} transition command: {cmd}")
                    if run_command(cmd, f"    {transition_type.upper()} transition {j}/{len(temp_clips)-1}", show_output=True):
                        transition_clips.append(transition_file)
                        print(f"      ✅ {transition_type.upper()} transition {j} SUCCESS")
                    else:
                        # If OpenCL failed, try CPU fallback
                        if capabilities['gpu_transitions_supported'] and capabilities['cpu_transitions_supported']:
                            print(f"      ⚠️ OpenCL transition failed, trying CPU fallback...")
                            encoding_params = get_encoding_params(nvenc_available, fps)
                            cpu_cmd = f'ffmpeg -y -i "{prev_clip}" -i "{curr_clip}" -filter_complex "[0:v][1:v]xfade=transition={transition_type}:duration={DEFAULT_TRANSITION_DURATION}:offset={duration-DEFAULT_TRANSITION_DURATION:.1f}" {encoding_params} -t {duration:.1f} "{transition_file}"'
                            if run_command(cpu_cmd, f"    CPU fallback {transition_type.upper()} transition {j}/{len(temp_clips)-1}", show_output=True):
                                transition_clips.append(transition_file)
                                print(f"      ✅ CPU fallback {transition_type.upper()} transition {j} SUCCESS")
                            else:
                                print(f"      ❌ Both OpenCL and CPU transitions failed - using original clip")
                                transition_clips.append(curr_clip)
                        else:
                            print(f"      ❌ {transition_type.upper()} transition {j} FAILED - using original clip")
                            transition_clips.append(curr_clip)

            # Now create the final chunk from transition clips
            if len(transition_clips) == 1:
                os.rename(transition_clips[0], chunk_file)
            else:
                concat_file = f"{temp_dir}/final_concat_{chunk_idx}.txt"
                with open(concat_file, 'w') as f:
                    for clip in transition_clips:
                        f.write(f"file '{os.path.abspath(clip)}'\n")

                # RE-ENCODE during concatenation to PRESERVE crossfade transitions
                cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:v libx264 -c:a aac -r {fps} -crf {DEFAULT_CRF} -preset {DEFAULT_PRESET} "{chunk_file}"'
                if not run_command(cmd, f"    Finalizing chunk {chunk_idx + 1} (re-encoding to preserve transitions)", show_output=False):
                    return False

                # Clean up transition files
                for clip in transition_clips[1:]:  # Skip first clip (original)
                    try:
                        os.remove(clip)
                    except:
                        pass
                os.remove(concat_file)

            # Clean up original temp clips
            for clip in temp_clips:
                try:
                    os.remove(clip)
                except:
                    pass

        chunk_files.append(chunk_file)

        # Progress update
        completed = chunk_idx + 1
        total_chunks = (len(images) + chunk_size - 1) // chunk_size
        percentage = (completed / total_chunks) * 100
        print(f"  ✅ Chunk {completed}/{total_chunks} completed ({percentage:.1f}%)")

    # Final concatenation - transitions are already within chunks
    print("\n🎬 Final concatenation...")

    if len(chunk_files) == 1:
        # Just move single chunk (use shutil.move for cross-drive compatibility)
        shutil.move(chunk_files[0], output_file)
        success = True
    else:
        # Simple concatenation - smooth transitions are already built into each chunk
        print("  ✨ Smooth transitions already applied within each chunk")
        final_concat = f"{temp_dir}/final_concat.txt"
        with open(final_concat, 'w') as f:
            for chunk_file in chunk_files:
                f.write(f"file '{os.path.abspath(chunk_file)}'\n")

        # Calculate timeout based on number of chunks (30 seconds per chunk, minimum 60 seconds)
        timeout_seconds = max(60, len(chunk_files) * 30)
        print(f"  ⏱️  Using {timeout_seconds}s timeout for {len(chunk_files)} chunks")
        
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{final_concat}" -c copy "{output_file}"'
        success = run_command(cmd, "Creating final slideshow with smooth transitions", timeout_seconds=timeout_seconds)

    # Clean up only if successful
    if success:
        shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        print(f"⚠️  Final concatenation failed - temp files preserved in {temp_dir}")

    return success
