#!/usr/bin/env python3
"""
Waveform/spectrum overlays driven by the video's own audio.

Presets:
  bottom     - full-width waveform footer
  spectrum   - full-width scrolling spectrum footer
  waveform   - stereo center-mirrored waveform (L on top, R on bottom)
  equalizer  - classic LED-style VU meter with discrete columns

Examples:
  python make_overlay.py
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p bottom --height 200
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p spectrum --height 300
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p waveform --height 200
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p equalizer --bands 10 --levels 16 --height 320
"""

import argparse, os, shutil, subprocess, sys

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        sys.stderr.write("Error: ffmpeg not found in PATH. Install ffmpeg first.\n")
        sys.exit(1)

def build_filter(preset, args):
    """
    Returns (filter_complex_str, out_suffix).
    We end the graph with [v] so we can map it explicitly.
    """
    h = args.height

    if preset == "bottom":
        # Full-width thin line footer.
        color = args.color
        f = (
            f"[0:a]aformat=channel_layouts=mono,"
            f"showwaves=s=1280x{h}:mode=cline:colors={color},"
            f"format=rgba,colorkey=0x000000:0.01:0.0[w];"
            f"[0:v]format=rgba[v0];"
            f"[w][v0]scale2ref=w=iw:h={h}[w2][v2];"
            f"[v2][w2]overlay=x=0:y=H-h[v]"
        )
        return f, "wave_bottom"


    elif preset == "spectrum":
        # Scrolling spectrum footer (pretty but heavier).
        spec_color = args.spec_color
        f = (
            f"[0:a]showspectrum=s=1280x{h}:mode=combined:color={spec_color}:slide=scroll:scale=log,"
            f"format=rgba,colorkey=0x000000:0.01:0.0[spec];"
            f"[0:v]format=rgba[v0];"
            f"[spec][v0]scale2ref=w=iw:h={h}[spec2][v2];"
            f"[v2][spec2]overlay=x=0:y=H-h[v]"
        )
        return f, "spectrum_footer"

    elif preset == "waveform":
        # Stereo center-mirrored waveform: bass in middle, treble at edges
        # Left channel on top (normal), right channel on bottom (mirrored)
        # Positioned in bottom quarter of screen, full width
        wave_height = h // 2  # Height per channel
        colors = args.eq_colors or "0x00ffcc|0xff0066"
        blend_mode = getattr(args, 'blend_mode', 'normal')
        # Position in bottom quarter: y = 1080 - h = 1080 - 200 = 880 for default
        y_pos = 1080 - h
        f = (
            f"[0:a]asplit=2[al][ar];"  # Split stereo into left and right
            f"[al]showwaves="           # Left channel (top, normal orientation)
              f"s=1920x{wave_height}:"  # Full width
              f"mode=cline:"
              f"colors={colors.split('|')[0]},"
            f"format=rgba[wl];"
            f"[ar]showwaves="           # Right channel (bottom, will be flipped)
              f"s=1920x{wave_height}:"
              f"mode=cline:"
              f"colors={colors.split('|')[1] if '|' in colors else colors},"
            f"format=rgba,vflip[wr];"  # Flip right channel vertically
            f"[wl][wr]vstack,"         # Stack left on top, flipped right on bottom
            f"format=rgba,"
            f"scale=1920:{h}[wave];"   # Scale to full width and specified height
            f"[0:v]format=rgba[vid];"
            f"[vid][wave]overlay=x=0:y={y_pos}:format=rgb[v]"
        )
        return f, f"waveform_{blend_mode}"

    elif preset == "equalizer":
        # Classic LED-style VU meter with discrete columns and stacked boxes
        # Uses showfreqs with nearest-neighbor scaling for pixelated LED effect
        bands = getattr(args, 'bands', 10)
        levels = getattr(args, 'levels', 16)
        grid_thickness = getattr(args, 'grid', 1)
        colors = args.eq_colors or "0x00ffcc|0xff0066"

        eq_height = h // 2  # Height per channel

        f = (
            f"[0:a]asplit=2[al][ar];"  # Split stereo into left and right
            f"[al]showfreqs="           # Left channel (top)
              f"s={bands}x{levels}:"    # Tiny logical resolution
              f"mode=bar:"
              f"cmode=separate:"
              f"ascale=log:"
              f"fscale=log:"
              f"win_size=2048:"
              f"overlap=1:"
              f"colors={colors.split('|')[0]},"
            f"format=rgba,"
            f"scale=1920:{eq_height}:flags=neighbor[el];"  # Scale up with nearest neighbor
            f"[ar]showfreqs="           # Right channel (bottom, will be flipped)
              f"s={bands}x{levels}:"
              f"mode=bar:"
              f"cmode=separate:"
              f"ascale=log:"
              f"fscale=log:"
              f"win_size=2048:"
              f"overlap=1:"
              f"colors={colors.split('|')[1] if '|' in colors else colors},"
            f"format=rgba,"
            f"scale=1920:{eq_height}:flags=neighbor,"  # Scale up with nearest neighbor
            f"vflip[er];"  # Flip right channel vertically
        )

        # Add optional grid overlay
        if grid_thickness > 0:
            f += (
                f"[el]drawgrid=w={bands*1920//bands}:h={levels*eq_height//levels}:"
                f"t={grid_thickness}:c=white@0.3[el_grid];"
                f"[er]drawgrid=w={bands*1920//bands}:h={levels*eq_height//levels}:"
                f"t={grid_thickness}:c=white@0.3[er_grid];"
                f"[el_grid][er_grid]vstack,"
            )
        else:
            f += f"[el][er]vstack,"

        f += (
            f"format=rgba,"
            f"scale=1920:{h}[eq];"     # Scale to full width and specified height
            f"[0:v]format=rgba[vid];"
            f"[vid][eq]overlay=x=0:y=1080-{h}:format=rgb[v]"
        )
        return f, f"eq_{bands}x{levels}"

    else:
        raise ValueError(f"Unknown preset: {preset}")

def main():
    p = argparse.ArgumentParser(description="Overlay a waveform/spectrum on a video's own audio via ffmpeg.")
    p.add_argument("-i", "--input", default="beat_aligned_with_audio.mp4", help="Input video file")
    p.add_argument("-o", "--output", default=None, help="Output file path. If omitted, auto-names by preset.")
    p.add_argument("-p", "--preset", choices=["bottom", "spectrum", "waveform", "equalizer"], default="bottom", help="Overlay style")
    p.add_argument("--color", default="0x00ffcc", help="Waveform color for bottom/inset")
    p.add_argument("--spec-color", default="rainbow", help="Palette for spectrum preset")
    p.add_argument("--eq-colors", dest="eq_colors", default=None, help="Equalizer colors per channel, e.g. '0x00ffcc|0xff0066'")
    p.add_argument("--blend-mode", dest="blend_mode", default="normal", choices=["normal", "multiply", "screen", "overlay", "darken", "lighten", "difference", "addition", "subtract", "burn", "dodge", "hardlight", "softlight"], help="Blending mode for overlay (waveform preset)")
    p.add_argument("--height", type=int, default=200, help="Overlay height in px (footer or inset)")
    p.add_argument("--width", type=int, default=640, help="Inset overlay width in px (inset preset)")
    p.add_argument("--bands", type=int, default=10, help="Number of frequency bands for equalizer (default 10)")
    p.add_argument("--levels", type=int, default=16, help="Number of LED levels per band for equalizer (default 16)")
    p.add_argument("--grid", type=int, default=1, help="Grid line thickness in px for equalizer (0 to disable)")
    p.add_argument("--fps", type=int, default=None, help="Force output FPS, e.g. 30")
    p.add_argument("--crf", type=int, default=18, help="x264 CRF (quality). Lower is better. Default 18.")
    p.add_argument("--vpreset", default="veryfast", help="x264 speed preset. Default veryfast.")
    p.add_argument("--reencode-audio", action="store_true", help="Re-encode audio to AAC 192k instead of copying.")
    args = p.parse_args()

    check_ffmpeg()

    if not os.path.isfile(args.input):
        sys.stderr.write(f"Error: input file not found: {args.input}\n")
        sys.exit(1)

    filt, suffix = build_filter(args.preset, args)

    root, _ = os.path.splitext(args.input)
    out_path = args.output or f"{root}_{suffix}.mp4"

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", args.input,
        "-filter_complex", filt,
        "-map", "[v]", "-map", "0:a:0",
        "-c:v", "libx264", "-crf", str(args.crf), "-preset", args.vpreset,
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
    ]

    if args.fps:
        cmd += ["-r", str(args.fps)]

    if args.reencode_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-c:a", "copy"]

    cmd += [out_path]

    print("Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"ffmpeg failed with code %d\n" % e.returncode)
        sys.exit(e.returncode)

    print(f"Done: {out_path}")

if __name__ == "__main__":
    main()
