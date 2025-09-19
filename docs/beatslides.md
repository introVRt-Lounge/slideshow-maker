## Beat-Aligned Slideshow (`beatslides`) - Command Reference

### Synopsis

```bash
PYTHONPATH=src python3 -m slideshow_maker.cli.beatslides <audio_file> <images_dir> [options]
```

### Core arguments

- **audio_file**: Path to a single audio file (mp3, m4a, etc.). Used for beat detection and final muxing.
- **images_dir**: Directory containing images (jpg, jpeg, png). Images are sorted and looped as needed.

### Planning options

- **--period MIN MAX** (default: 5.0 10.0)
  - Window-constrained selection. Chooses cuts such that segment length remains within [MIN, MAX] seconds.
  - Practical: these are the acceptable slide lengths; longer tracks feel more cinematic; smaller values feel more frenetic.

- **--target SECONDS** (default: 7.5)
  - Preference for average segment length within the window. Selection aims for the nearest beat to this target.

- **--grace SECONDS** (default: 0.5)
  - Grace expansion when no beat exists in the window; planner widens the search by this amount to find a cut.

- **--min-gap SECONDS** (default: 2.05)
  - Safety margin for transitions (>= 2*xfade + 0.05). For hardcuts, this prevents ultra-short segments.

- **--phase SECONDS** (default: 0.0)
  - Phase/latency compensation applied to beats before selection. Negative leads cuts earlier for punchier sync.

- **--strict**
  - If set, the planner does not widen the window on sparse sections; it will pick the nearest beat inside the strict window only.

- **--all-beats**
  - Bypass selection and cut on every detected beat. Useful for diagnostics or hyper-cut styles.

- **--audio-end SECONDS** (default: auto)
  - Override end time for planning; by default the true audio duration is used.

- **--max-seconds SECONDS**
  - Preview limit. Shorten planned duration for quick demos; omit for full-length output.

### Rendering mode

- **--hardcuts**
  - Render using hard cuts only (no xfade). Recommended for verifying on-beat timing.

- Transitions mode (experimental):
  - **--transition NAME** (default: fade)
  - **--xfade SECONDS** (default: 1.0)
  - **--align end|midpoint** (default: end)
  - Tip: for on-beat perceptual switch, prefer `--align midpoint --xfade 0.5..0.8 --phase -0.03`.

### Debug overlays (hardcuts mode)

- **--mark-beats**
  - Draw a white vertical bar for every detected beat.

- **--pulse** (with defaults)
  - Subtle image pulse at each beat.
  - Defaults: `--pulse-sat 1.25 --pulse-bright 0.0 --pulse-dur 0.08`.

- **--bloom** (optional glow)
  - Adds gaussian blur pulse at each beat for a soft bloom.
  - Defaults: `--bloom-sigma 8.0 --bloom-dur 0.08`.

- **--counter**
  - Shows a sticky beat counter that increments each beat and persists until the next beat.
  - Options: `--counter-size 36` and `--counter-pos tr|tl|br|bl`.

### Audio options

- **--no-audio**
  - Skip muxing. By default, the final MP4 includes the input audio.

### Examples

Render a full-length hardcut debug with overlays:
```bash
PYTHONPATH=src python3 -m slideshow_maker.cli.beatslides song.mp3 ./images \
  --period 5 10 --target 7.5 --hardcuts --mark-beats --pulse --bloom --counter
```

Every-beat cut diagnostic (short preview):
```bash
PYTHONPATH=src python3 -m slideshow_maker.cli.beatslides song.mp3 ./images \
  --all-beats --hardcuts --mark-beats --counter --max-seconds 30
```

Transitions test (perceptual on-beat midpoints):
```bash
PYTHONPATH=src python3 -m slideshow_maker.cli.beatslides song.mp3 ./images \
  --transition fade --xfade 0.6 --align midpoint --phase -0.03
```

### Notes

- If beats feel late/early, adjust `--phase` slightly (e.g., -0.03 .. +0.03).
- For performance, overlays add filter complexity. Use `--hardcuts` for verification, then iterate with transitions.


