Short version: yes, it makes sense, and yes, it’s tractable.

### Why it’s sane

* You’re not inventing DSP. Beat detection is solved (aubio/librosa).
* The “novel” bit is just picking a subset of beats so gaps land within \[min,max] seconds. That’s planning logic, not heavy math.
* Rendering is stock ffmpeg. Reliable.

### Complexity

* Beats array length n \~ a few thousand for a 2.5 hr set.
* Selection is a single pass with small windowed searches. O(n). Fast on a laptop.

### Edge cases and fixes

* **Sparse or breakdown sections**: no beat inside window.

  * Fix: strict vs grace mode. Expand window by ±grace once, or pick nearest beat and warn.
* **Tempo drifts**: your windowing sidesteps “every N beats” brittleness.
* **False positives**: clamp min beat gap (e.g., 120 ms) after detection.
* **Transitions starving**: enforce min segment >= 2\*xfade + 0.05. If not, try next candidate in window or hard cut.
* **Sync feel off**: phase and latency knobs. Small values like phase -0.03, latency +0.05 do wonders.
* **Too few images**: loop or truncate. Deterministic shuffle with seed.

### Minimal planner pseudocode

```python
beats = load_beats()              # seconds, ascending, de-duped
beats = [b + phase for b in beats if b + phase >= 0]
chosen = []
i = 0
t = 0.0                           # last cut time
MIN, MAX = period_min, period_max
while True:
    w_start = t + MIN
    w_end   = t + MAX
    S = [b for b in beats if w_start <= b <= w_end]
    if not S:
        if strict:
            S = [b for b in beats if (t + MIN - grace) <= b <= (t + MAX + grace)]
            if not S: break_or_error()
        else:
            # nearest beat to clamped target
            target = clamp(t + target_period, w_start, w_end)
            b = min(beats, key=lambda x: abs(x - target))
            S = [b]

    # choose candidate by strategy
    target = t + target_period
    cand = choose_candidate(S, strategy, target, onset_strength, downbeat_flags)

    # enforce min_cut_gap and xfade safety
    if chosen:
        if cand - chosen[-1] < min_cut_gap:
            cand = next_best_in_S_or_fallback(S, cand, min_cut_gap, chosen[-1])
            if cand is None: continue

    chosen.append(cand)
    t = cand
    if t + MIN > audio_end: break
```

### Test plan that will catch 90% of issues

1. 3 tracks: steady 120 BPM, drifting live set, quiet ambient with weak beats.
2. Run `--period 5 10 --target 7.5` with and without transitions.
3. Verify: all cuts in beats.txt, deltas in \[5,10] except explicit grace cases, no segment shorter than xfade requirement, end trimmed to audio length.
4. Determinism: run twice with `--shuffle --seed 1337`, same plan.json.

### Tooling reality check

* **Beat detection**: aubio CLI first. If missing, librosa fallback.
* **Downbeats/energy**: optional nice-to-have, improves feel but not required.
* **Render**: one ffmpeg call. Keep filtergraph simple. Use concat when transitions=none.

### Effort

* Polished CLI with logs, seeds, transitions in 2–3 more.
* Nothing here is research-grade pain.
