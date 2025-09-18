
# Task: Beat-Aligned, Window-Constrained Slideshow (CLI) for slideshow-maker

## Goal

Upgrade the existing slideshow renderer to:

* Detect beats from the audio.
* Choose a **subset** of beats as **cut points** so that:

  * **Every cut lands exactly on a detected beat.**
  * **Time between consecutive cuts stays within `[PERIOD_MIN, PERIOD_MAX]` seconds** (e.g., 5–10s).
  * Selection adapts to tempo changes (no “every Nth beat” fixed logic).
* Render images with optional transitions (crossfade), centered on each chosen cut.

## CLI (add/extend)

```
beatslides \
  --images "./images/*.png" \
  --audio "./track.mp3" \
  --period 5.0 10.0 \
  --target 7.5 \
  --selection-strategy [nearest|energy|downbeat|hybrid] \
  --strict true \
  --grace 0.75 \
  --phase -0.03 \
  --latency 0.05 \
  --transition [none|fade|slideleft|slideright|wipeleft|circleopen] \
  --xfade 0.20 \
  --min-cut-gap 0.30 \
  --width 1920 --height 1080 --fps 30 \
  --shuffle --seed 42 \
  --workdir ./.work --out ./out.mp4 --verbose
```

### Flags explained

* `--period MIN MAX` (required): global allowed time between cuts. All cuts must fall on beats and respect this window.
* `--target` (soft): desired average period. Used to bias selection (e.g., 7.5s within a 5–10s window).
* `--selection-strategy`:

  * `nearest`: pick the beat whose timestamp is closest to `prev_cut + target`.
  * `energy`: pick the beat with max onset strength within the window.
  * `downbeat`: prefer downbeats (bar starts) within the window if available, else fallback to nearest.
  * `hybrid` (default): prefer downbeat if within tolerance of target; else energy; else nearest.
* `--strict true|false`: if **true** and no beat is found within the window, expand by `±grace` once; if still none, **error out**. If false, pick the **closest** beat to the window (still a beat), warn.
* `--grace`: max expansion seconds applied once when strict mode can’t find a beat.
* `--phase`: shift detected beats before planning (compensate detector early/late).
* `--latency`: apply final offset to all cut times (presentation/stream delay).
* `--min-cut-gap`: ensures you don’t pick beats so close that transitions clip.

## Beat detection

* Primary: `aubio beat input.mp3 > beats.txt` (one timestamp per line, seconds).
* Fallback: Python `librosa`:

  * Get `tempo`, `beats` (frames→times).
  * Compute `onset_strength` to score “energy”.
  * Optional: try downbeat estimation (`librosa.beat.beat_track` + `librosa.beat.plp`/`madmom` if available). If downbeat detection unavailable, emulate downbeats via tempo + periodicity heuristics.
* Apply `--phase` shift; drop negative/duplicate/too-close beats (min gap 0.12s).

## Selection algorithm (core)

Let `B = {b1, b2, ..., bn}` be ascending beat times (post-phase). We choose a subsequence `C = {c1, c2, ..., ck}`, each `ci ∈ B`.

1. **Init**

   * `c1`: choose first cut at the first beat ≥ `start + target` clamped to `[start + MIN, start + MAX]`. If nothing in window, apply strict/grace rule. Typically `start = 0`.
2. **Iterate** for i ≥ 2:

   * Window for next cut: `W = [c_{i-1} + MIN, c_{i-1} + MAX]` where `MIN, MAX` come from `--period`.
   * Candidate beats: `S = { b ∈ B | b ∈ W }`.
   * If `S` empty:

     * If `--strict`:

       * Expand once to `W' = [W.min - grace, W.max + grace]`, recompute `S`.
       * If still empty: **error**.
     * Else (non-strict): pick `b* = argmin_b |b − clamp(prev+target, W.min, W.max)|` from beats **near** W; warn.
   * If `S` non-empty:

     * **Strategy choice**:

       * `nearest`: `b* = argmin_{b∈S} |b − (c_{i-1} + target)|`.
       * `energy`: `b* = argmax_{b∈S} onset_strength[b]`.
       * `downbeat`: pick any downbeat in `S` whose distance to `(c_{i-1}+target)` ≤ `(MAX−MIN)/2`; else nearest.
       * `hybrid`: downbeat if present and near target; else energy; else nearest.
     * Enforce `b* − c_{i-1} ≥ min_cut_gap`. If violated, try next-best candidate in `S`. If none left, fallback as above.
   * Set `c_i = b*`.
3. Stop when `c_k + MIN` would exceed audio end; last segment trims to audio length.

**Invariants**:

* All `c_i` are beats.
* Each inter-cut interval `Δ_i = c_i − c_{i−1}` respects `MIN ≤ Δ_i ≤ MAX` (or the documented strict/grace deviation with warning).

## Transitions

* If `--transition != none`:

  * The **cut time** is the **center** of the crossfade.
  * Ensure both adjacent segments ≥ `2*xfade + 0.05`. If not:

    * Try alternate candidate in `S` that satisfies timing.
    * If impossible, downgrade that cut to a hard cut (warn) or nudge within window if legal.
* Implement via a single `ffmpeg -filter_complex` `xfade` chain at cut centers.
* If `none`, use concat demuxer with per-image durations computed from `C`.

## Image sequencing

* Gather images by glob; default natural sort.
* `--shuffle` with `--seed` for deterministic randomization.
* `--image-loop` to loop when you have fewer images than cuts; otherwise truncate `C` to image count.

## Output

* H.264/AAC MP4, `yuv420p`, defaults 1920x1080\@30.
* Expose `--width --height --fps --preset`.
* Don’t drift: lock video timeline to audio duration.

## Robustness

* If no beats detected at all: warn and optionally fall back to fixed duration (`--fallback-duration SEC`) but **only if user passes `--allow-offbeat-fallback`**; otherwise exit with clear message (since requirement is “cuts on beats”).
* Write to `--workdir`:

  * `beats.txt` (post-phase),
  * `plan.json` (chosen cuts, windows, images, transition placements),
  * `render_cmd.txt` (full ffmpeg line).
* `--verbose` prints BPM estimate, beat count, chosen strategy, window stats, deviations from target, and any strict/grace fallbacks.

## Minimal implementation steps

1. Beat extraction (aubio first, librosa fallback) + optional downbeat & onset strength arrays.
2. Planner implementing the window-constrained subsequence selection.
3. Duration builder from `C` → per-image segments.
4. Renderer:

   * concat path (no transitions),
   * xfade graph path (transitions).
5. CLI + README.

## Acceptance tests

1. **Window constraint honored**

   * `--period 5 10 --target 7.5 --selection-strategy nearest --transition none`
   * Verify all cuts are in `beats.txt`, and inter-cut deltas ∈ \[5,10]s.
2. **Hybrid preference**

   * `--selection-strategy hybrid --transition fade --xfade 0.2`
   * Where downbeats exist in-window near target, they’re chosen; otherwise energy/nearest.
3. **Strict failure**

   * Provide an audio segment with a deliberate long beat gap; with `--strict true --grace 0.25`, expect a clean error message if no beat fits.
4. **Grace success**

   * Same as above but with `--grace 1.0`; expect one window to expand; log must note the expansion.
5. **Deterministic shuffle**

   * Two runs with `--shuffle --seed 1234` produce identical `plan.json`.

## Constraints

* Linux-first. Dependencies: `ffmpeg`, `aubio` (optional), Python packages (`librosa`, `numpy`, `soundfile`) for fallback and scoring.
* Keep the ffmpeg filtergraph readable; one invocation preferred.
* Fail fast, clear messages, non-zero exit codes on hard failures.
