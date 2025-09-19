#!/usr/bin/env python3
"""
Waveform/spectrum overlays driven by the video's own audio.

Presets:
  bottom     - full-width waveform footer
  inset      - small waveform with a translucent backing plate (top-right)
  spectrum   - full-width scrolling spectrum footer
  equalizer  - stereo graphic-EQ bars (L on top, R on bottom)

Examples:
  python make_overlay.py
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p equalizer --height 320
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p equalizer --height 320 --blend-mode multiply
  python make_overlay.py -i beat_aligned_with_audio.mp4 -p bottom --color 0x00ffcc --height 220
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

    elif preset == "inset":
        # Inset thicker waveform with a translucent plate; uses expressions (no hardcoded 1920).
        w = args.width
        color = args.color
        f = (
            f"[0:a]aformat=channel_layouts=mono,"
            f"showwaves=s={w}x{h}:mode=p2p:colors={color},"
            f"format=rgba,colorkey=0x000000:0.01:0.0[w];"
            f"[0:v]format=rgba,drawbox=x=W-{w}-20:y=20:w={w}:h={h}:color=black@0.45:t=fill[vb];"
            f"[vb][w]overlay=x=W-w-20:y=20[v]"
        )
        return f, "wave_inset"

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

    elif preset == "equalizer":
        # Graphic equalizer bars with flipped right channel.
        # Left channel on top (normal), right channel on bottom (flipped).
        # Both channels: bass left, treble right, mirrored out from midpoint.
        eq_height = h // 2  # Height per channel
        colors = args.eq_colors or "0x00ffcc|0xff0066"
        blend_mode = getattr(args, 'blend_mode', 'normal')
        f = (
            f"[0:a]asplit=2[al][ar];"  # Split stereo into left and right
            f"[al]showfreqs="           # Left channel (top, normal orientation)
              f"s=1280x{eq_height}:"
              f"mode=bar:"
              f"ascale=log:"
              f"fscale=log:"
              f"win_size=2048:"
              f"overlap=1:"
              f"colors={colors.split('|')[0]},"
            f"format=rgba[el];"
            f"[ar]showfreqs="           # Right channel (bottom, will be flipped)
              f"s=1280x{eq_height}:"
              f"mode=bar:"
              f"ascale=log:"
              f"fscale=log:"
              f"win_size=2048:"
              f"overlap=1:"
              f"colors={colors.split('|')[1] if '|' in colors else colors},"
            f"format=rgba,vflip[er];"  # Flip right channel vertically
            f"[el][er]vstack,"         # Stack left on top, flipped right on bottom
            f"format=rgba,"
            f"scale=1920:1080[eq];"   # Scale equalizer to match video dimensions
            f"[0:v]format=rgba[vid];"
            f"[vid][eq]blend=all_mode={blend_mode}:all_opacity=1.0[v]"
        )
        return f, f"eq_{blend_mode}"

    else:
        raise ValueError(f"Unknown preset: {preset}")

def main():
    p = argparse.ArgumentParser(description="Overlay a waveform/spectrum on a video's own audio via ffmpeg.")
    p.add_argument("-i", "--input", default="beat_aligned_with_audio.mp4", help="Input video file")
    p.add_argument("-o", "--output", default=None, help="Output file path. If omitted, auto-names by preset.")
    p.add_argument("-p", "--preset", choices=["bottom", "inset", "spectrum", "equalizer"], default="bottom", help="Overlay style")
    p.add_argument("--color", default="0x00ffcc", help="Waveform color for bottom/inset")
    p.add_argument("--spec-color", default="rainbow", help="Palette for spectrum preset")
    p.add_argument("--eq-colors", dest="eq_colors", default=None, help="Equalizer colors per channel, e.g. '0x00ffcc|0xff0066'")
    p.add_argument("--blend-mode", dest="blend_mode", default="normal", choices=["normal", "multiply", "screen", "overlay", "darken", "lighten", "difference", "addition", "subtract", "burn", "dodge", "hardlight", "softlight"], help="Blending mode for overlay (equalizer preset)")
    p.add_argument("--height", type=int, default=200, help="Overlay height in px (footer or inset)")
    p.add_argument("--width", type=int, default=640, help="Inset overlay width in px (inset preset)")
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
