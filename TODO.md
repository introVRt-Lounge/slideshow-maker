# 🎬 Slideshow Maker - TODO List

## 📋 Overview
This document outlines the remaining features and enhancements for the VRChat Slideshow Maker project. The core functionality is complete with 50+ FFmpeg transitions and capability detection.

## 🎯 **NEW: Beat-Aligned Slideshow System**
A critical new feature has been identified: **Beat-Aligned Slideshow System**. This feature will automatically detect musical beats and sync image transitions to create professional music video-style slideshows. This is now the **highest priority** feature as it provides the most significant user value and differentiates the tool from basic slideshow creators.

## ✅ Completed Features
- [x] Research all available FFmpeg xfade transitions and effects
- [x] Add ALL 50+ FFmpeg xfade transitions from the official gallery
- [x] Modularize the Python codebase into separate modules
- [x] Add comprehensive test suite for the modular codebase
- [x] Add FFmpeg capability detection for GPU vs CPU transitions

---

## 🚀 High Priority Features

### 1. Beat-Aligned Slideshow System (NEW - Critical Feature)
**Priority:** Critical | **Effort:** High | **Impact:** Very High

#### Overview:
Implement intelligent beat detection and alignment system that automatically syncs image transitions to musical beats, creating professional music video-style slideshows.

#### Tasks:
- [ ] **Beat Detection System**
  - [ ] Primary: `aubio` beat detection (`aubio beat input.mp3 > beats.txt`)
  - [ ] Fallback: `librosa` beat tracking with onset strength analysis
  - [ ] Downbeat detection using `librosa.beat.plp` and `madmom`
  - [ ] BPM estimation and tempo change detection
  - [ ] Beat validation and cleanup (remove duplicates, too-close beats)

- [ ] **Window-Constrained Selection Algorithm**
  - [ ] Implement core selection algorithm with `[PERIOD_MIN, PERIOD_MAX]` windows
  - [ ] Add selection strategies: `nearest`, `energy`, `downbeat`, `hybrid`
  - [ ] Implement strict vs non-strict modes with grace period expansion
  - [ ] Add phase shift and latency compensation
  - [ ] Ensure all cuts land exactly on detected beats

- [ ] **Beat-Aligned CLI Interface**
  - [ ] `beatslides` command with comprehensive parameter set
  - [ ] `--period MIN MAX` for window constraints
  - [ ] `--target` for desired average period
  - [ ] `--selection-strategy` for beat selection method
  - [ ] `--strict` and `--grace` for error handling
  - [ ] `--phase` and `--latency` for timing compensation

- [ ] **Integration with Existing Transition System**
  - [ ] Use existing 50+ FFmpeg transitions for beat-aligned cuts
  - [ ] Integrate with capability detection system
  - [ ] Support all transition types (CPU and GPU)
  - [ ] Add transition timing validation for beat constraints

- [ ] **Advanced Beat Analysis**
  - [ ] Onset strength scoring for energy-based selection
  - [ ] Downbeat estimation and preference
  - [ ] Tempo change adaptation
  - [ ] Beat confidence scoring

- [ ] **Robust Error Handling**
  - [ ] Graceful fallback when no beats detected
  - [ ] Clear error messages for strict mode failures
  - [ ] Warning system for non-strict mode deviations
  - [ ] Beat detection quality validation

#### Files to create:
- `src/slideshow_maker/beat_detection.py` - Beat detection and analysis
- `src/slideshow_maker/beat_selection.py` - Window-constrained selection algorithm
- `src/slideshow_maker/beat_alignment.py` - Main beat alignment orchestrator
- `src/slideshow_maker/cli/beatslides.py` - Beat-aligned CLI interface
- `tests/test_beat_detection.py` - Beat detection tests
- `tests/test_beat_selection.py` - Selection algorithm tests
- `tests/test_beat_alignment.py` - Integration tests

#### Files to modify:
- `main.py` - Add beatslides command
- `src/slideshow_maker/video.py` - Integrate beat-aligned rendering
- `src/slideshow_maker/transitions.py` - Add beat-aligned transition support
- `requirements.txt` - Add aubio, librosa, madmom dependencies

#### Dependencies:
- `aubio` - Primary beat detection
- `librosa` - Fallback beat detection and analysis
- `madmom` - Advanced downbeat detection
- `numpy` - Numerical analysis
- `soundfile` - Audio file handling

#### Acceptance Criteria:
- [ ] All cuts land exactly on detected beats
- [ ] Inter-cut intervals respect `[PERIOD_MIN, PERIOD_MAX]` windows
- [ ] Selection adapts to tempo changes automatically
- [ ] Supports all existing transition types
- [ ] Graceful error handling with clear messages
- [ ] Deterministic output with seed control
- [ ] Comprehensive test coverage

---

### 2. Add Advanced Transition Categories (3D, Particle, Morphing, etc.)
**Priority:** High | **Effort:** Medium | **Impact:** High

#### Tasks:
- [ ] **Research advanced FFmpeg filters**
  - [ ] 3D rotation and perspective transforms
  - [ ] Particle systems using `noise` and `random` filters
  - [ ] Morphing effects using `morpho` and `morphology` filters
  - [ ] Liquid/wave effects using `waveform` and `liquid` filters
  - [ ] Glitch effects using `glitch` and `noise` filters

- [ ] **Implement 3D transition category**
  - [ ] `rotate3d` - 3D rotation transitions
  - [ ] `flip3d` - 3D flip effects
  - [ ] `cube3d` - Cube rotation transitions
  - [ ] `sphere3d` - Sphere morphing transitions

- [ ] **Implement particle transition category**
  - [ ] `particle_fade` - Particle-based fade effects
  - [ ] `snow` - Snow particle transitions
  - [ ] `fire` - Fire particle effects
  - [ ] `sparkle` - Sparkle particle transitions

- [ ] **Implement morphing transition category**
  - [ ] `morph` - Shape morphing transitions
  - [ ] `liquid` - Liquid wave transitions
  - [ ] `ripple` - Ripple effect transitions
  - [ ] `blob` - Blob morphing transitions

- [ ] **Update transition categorization system**
  - [ ] Add `ADVANCED_CATEGORIES` to config.py
  - [ ] Update transition selection logic
  - [ ] Add category-based filtering

#### Files to modify:
- `src/slideshow_maker/config.py` - Add new transition categories
- `src/slideshow_maker/transitions.py` - Add category management
- `src/slideshow_maker/video.py` - Update transition selection
- `tests/test_transitions.py` - Add tests for new categories

---

### 2. Implement Custom Transition Effects Using FFmpeg Filters
**Priority:** High | **Effort:** High | **Impact:** High

#### Tasks:
- [ ] **Research custom FFmpeg filter combinations**
  - [ ] Study `filter_complex` advanced usage
  - [ ] Research `glsl` (OpenGL Shading Language) filters
  - [ ] Study `libplacebo` filters for advanced effects
  - [ ] Research `vapoursynth` integration possibilities

- [ ] **Implement custom transition framework**
  - [ ] Create `CustomTransition` class
  - [ ] Add `filter_complex` builder functions
  - [ ] Implement transition parameter system
  - [ ] Add custom transition validation

- [ ] **Create custom transition library**
  - [ ] `kaleidoscope` - Kaleidoscope effect transitions
  - [ ] `hologram` - Holographic display transitions
  - [ ] `matrix` - Matrix-style digital rain transitions
  - [ ] `neon` - Neon glow transitions
  - [ ] `vhs` - VHS tape effect transitions
  - [ ] `datamosh` - Datamoshing glitch transitions

- [ ] **Add custom transition configuration**
  - [ ] JSON-based transition definitions
  - [ ] Parameter validation system
  - [ ] Custom transition testing framework

#### Files to create:
- `src/slideshow_maker/custom_transitions.py` - Custom transition framework
- `src/slideshow_maker/transitions/custom/` - Custom transition definitions
- `tests/test_custom_transitions.py` - Custom transition tests

#### Files to modify:
- `src/slideshow_maker/config.py` - Add custom transition support
- `src/slideshow_maker/transitions.py` - Integrate custom transitions
- `src/slideshow_maker/video.py` - Support custom transition rendering

---

### 3. Add Transition Timing Controls and Easing Functions
**Priority:** High | **Effort:** Medium | **Impact:** High

#### Tasks:
- [ ] **Implement easing function system**
  - [ ] `linear` - Linear timing
  - [ ] `ease_in` - Ease in timing
  - [ ] `ease_out` - Ease out timing
  - [ ] `ease_in_out` - Ease in-out timing
  - [ ] `bounce` - Bounce effect timing
  - [ ] `elastic` - Elastic effect timing
  - [ ] `back` - Back effect timing

- [ ] **Add transition timing controls**
  - [ ] `transition_duration` - Per-transition duration control
  - [ ] `transition_delay` - Delay before transition starts
  - [ ] `transition_speed` - Speed multiplier for transitions
  - [ ] `transition_curve` - Easing curve selection

- [ ] **Implement timing parameter system**
  - [ ] Add timing parameters to transition config
  - [ ] Create timing validation system
  - [ ] Add timing preview functionality

- [ ] **Update FFmpeg command generation**
  - [ ] Integrate easing functions into xfade parameters
  - [ ] Add custom timing curves using `curves` filter
  - [ ] Support per-transition timing overrides

#### Files to create:
- `src/slideshow_maker/timing.py` - Easing functions and timing controls
- `src/slideshow_maker/easing.py` - Mathematical easing functions

#### Files to modify:
- `src/slideshow_maker/config.py` - Add timing configuration
- `src/slideshow_maker/video.py` - Integrate timing controls
- `src/slideshow_maker/transitions.py` - Add timing support

---

## 🎯 Medium Priority Features

### 4. Create Transition Preview System
**Priority:** Medium | **Effort:** Medium | **Impact:** Medium

#### Tasks:
- [ ] **Implement preview generation**
  - [ ] Create preview video generation function
  - [ ] Add preview thumbnail generation
  - [ ] Implement preview caching system
  - [ ] Add preview quality controls

- [ ] **Create preview interface**
  - [ ] CLI preview command
  - [ ] Preview gallery generation
  - [ ] Transition comparison tool
  - [ ] Preview export functionality

- [ ] **Add preview optimization**
  - [ ] Low-resolution preview generation
  - [ ] Fast preview mode
  - [ ] Preview compression
  - [ ] Batch preview generation

#### Files to create:
- `src/slideshow_maker/preview.py` - Preview generation system
- `src/slideshow_maker/cli/preview.py` - CLI preview commands
- `preview_gallery.html` - Web-based preview gallery

#### Files to modify:
- `main.py` - Add preview CLI commands
- `src/slideshow_maker/transitions.py` - Add preview support

---

### 5. Add Audio-Reactive Transitions
**Priority:** Medium | **Effort:** High | **Impact:** High

#### Tasks:
- [ ] **Implement audio analysis**
  - [ ] Beat detection using `libavfilter`
  - [ ] Frequency analysis
  - [ ] Volume level detection
  - [ ] Tempo analysis

- [ ] **Create audio-reactive transition system**
  - [ ] Beat-synchronized transitions
  - [ ] Volume-based transition intensity
  - [ ] Frequency-based transition selection
  - [ ] Tempo-based transition timing

- [ ] **Add audio-reactive transition types**
  - [ ] `beat_sync` - Beat-synchronized transitions
  - [ ] `volume_fade` - Volume-based fade intensity
  - [ ] `bass_boom` - Bass-triggered effects
  - [ ] `treble_sparkle` - Treble-triggered sparkles

- [ ] **Implement audio analysis caching**
  - [ ] Cache audio analysis results
  - [ ] Fast audio analysis mode
  - [ ] Audio analysis validation

#### Files to create:
- `src/slideshow_maker/audio_analysis.py` - Audio analysis system
- `src/slideshow_maker/audio_reactive.py` - Audio-reactive transitions

#### Files to modify:
- `src/slideshow_maker/audio.py` - Integrate audio analysis
- `src/slideshow_maker/video.py` - Support audio-reactive transitions

---

### 6. Implement Transition Randomization and Smart Selection
**Priority:** Medium | **Effort:** Medium | **Impact:** Medium

#### Tasks:
- [ ] **Implement smart transition selection**
  - [ ] Image content analysis
  - [ ] Transition appropriateness scoring
  - [ ] Context-aware transition selection
  - [ ] Transition variety balancing

- [ ] **Add randomization controls**
  - [ ] Random seed control
  - [ ] Transition probability weighting
  - [ ] Category-based randomization
  - [ ] Transition sequence optimization

- [ ] **Create transition intelligence**
  - [ ] Learn from user preferences
  - [ ] Transition effectiveness scoring
  - [ ] Automatic transition optimization
  - [ ] Transition recommendation system

- [ ] **Add transition constraints**
  - [ ] Avoid similar consecutive transitions
  - [ ] Balance transition categories
  - [ ] Respect transition duration limits
  - [ ] Handle edge cases gracefully

#### Files to create:
- `src/slideshow_maker/smart_selection.py` - Smart transition selection
- `src/slideshow_maker/randomization.py` - Randomization controls

#### Files to modify:
- `src/slideshow_maker/transitions.py` - Add smart selection
- `src/slideshow_maker/video.py` - Integrate smart selection

---

## 🔧 Low Priority Features

### 7. Add Transition Configuration File Support
**Priority:** Low | **Effort:** Low | **Impact:** Medium

#### Tasks:
- [ ] **Implement configuration file system**
  - [ ] JSON configuration file support
  - [ ] YAML configuration file support
  - [ ] Configuration validation
  - [ ] Configuration merging

- [ ] **Create transition configuration schema**
  - [ ] Transition parameter definitions
  - [ ] Timing configuration schema
  - [ ] Category configuration schema
  - [ ] Custom transition schema

- [ ] **Add configuration management**
  - [ ] Configuration file discovery
  - [ ] Configuration hot-reloading
  - [ ] Configuration backup/restore
  - [ ] Configuration migration

#### Files to create:
- `src/slideshow_maker/config_manager.py` - Configuration management
- `config/schema.json` - Configuration schema
- `config/default.json` - Default configuration

#### Files to modify:
- `src/slideshow_maker/config.py` - Add configuration file support
- `main.py` - Add configuration CLI options

---

### 8. Create Transition Testing and Validation System
**Priority:** Low | **Effort:** Medium | **Impact:** Low

#### Tasks:
- [ ] **Implement transition validation**
  - [ ] FFmpeg command validation
  - [ ] Transition parameter validation
  - [ ] Transition compatibility checking
  - [ ] Transition performance testing

- [ ] **Create transition test suite**
  - [ ] Unit tests for each transition
  - [ ] Integration tests for transition combinations
  - [ ] Performance tests for transition rendering
  - [ ] Compatibility tests for different FFmpeg versions

- [ ] **Add transition quality assurance**
  - [ ] Visual quality validation
  - [ ] Transition smoothness testing
  - [ ] Edge case testing
  - [ ] Regression testing

- [ ] **Implement transition benchmarking**
  - [ ] Rendering speed benchmarks
  - [ ] Memory usage benchmarks
  - [ ] Quality benchmarks
  - [ ] Compatibility benchmarks

#### Files to create:
- `src/slideshow_maker/validation.py` - Transition validation
- `tests/benchmarks/` - Performance benchmarks
- `tests/quality/` - Quality assurance tests

#### Files to modify:
- `tests/test_transitions.py` - Add validation tests
- `run_tests.py` - Add validation test runner

---

## 📊 Implementation Priority Matrix

| Feature | Priority | Effort | Impact | Dependencies |
|---------|----------|--------|--------|--------------|
| **Beat-Aligned System** | **Critical** | **High** | **Very High** | **None** |
| Advanced Categories | High | Medium | High | None |
| Custom Transitions | High | High | High | Advanced Categories |
| Timing Controls | High | Medium | High | Beat-Aligned System |
| Preview System | Medium | Medium | Medium | Beat-Aligned System |
| Audio-Reactive | Medium | High | High | Beat-Aligned System |
| Smart Selection | Medium | Medium | Medium | Beat-Aligned System |
| Config Files | Low | Low | Medium | None |
| Testing System | Low | Medium | Low | All Features |

## 🎯 Next Steps

1. **Implement Beat-Aligned System** - **CRITICAL** - Provides maximum user value and differentiation
2. **Add Advanced Categories** - Builds foundation for other features
3. **Add Timing Controls** - Enhances existing transitions and beat alignment
4. **Create Preview System** - Improves user experience, especially for beat alignment
5. **Implement Custom Transitions** - Adds unique value
6. **Add Audio-Reactive Features** - Complements beat alignment system

## 📝 Notes

- All features should maintain backward compatibility
- Each feature should include comprehensive tests
- Documentation should be updated for each feature
- Performance impact should be considered for each feature
- User experience should be prioritized in all implementations

## 🔍 Beat-Alignment Feature Critique

### ✅ **Strengths of beat-alignment.md:**
- **Comprehensive CLI design** - Well-thought-out parameter set with clear explanations
- **Robust beat detection** - Primary (aubio) + fallback (librosa) approach ensures reliability
- **Sophisticated selection algorithm** - Multiple strategies with mathematical precision
- **Clear invariants** - Window constraints and beat alignment requirements are well-defined
- **Good error handling** - Strict vs non-strict modes with grace periods
- **Detailed acceptance tests** - Clear validation criteria for testing

### ⚠️ **Areas for Improvement:**
- **Missing integration** - Doesn't leverage existing 50+ transition system
- **Complex CLI** - 15+ parameters might overwhelm users (need simplified presets)
- **No preview system** - Can't test beat alignment before rendering
- **Limited transition support** - Only basic xfade, not the full transition library
- **No configuration files** - All parameters via CLI only (need JSON/YAML support)
- **Missing audio analysis** - No BPM estimation or tempo change detection in output

### 🚀 **Integration Enhancements:**
- **Leverage existing capability detection** - Use our FFmpeg detection system
- **Integrate with transition system** - Use all 50+ transitions for beat-aligned cuts
- **Add to preview system** - Beat-aligned preview generation
- **Configuration file support** - JSON/YAML for complex beat alignment setups
- **Smart selection enhancement** - Combine with our AI selection system
- **Simplified presets** - Common beat alignment patterns (e.g., "dance", "ambient", "rock")

### 🎯 **Implementation Strategy:**
1. **Phase 1:** Core beat detection and selection algorithm
2. **Phase 2:** Integration with existing transition system
3. **Phase 3:** CLI interface and error handling
4. **Phase 4:** Preview system and configuration files
5. **Phase 5:** Advanced features and optimization

---

### 🔜 Beat-Aligned: Next Phases

- [ ] Phase 2c: Per-segment transition fallback and stability
  - [x] Fallback to hardcut for too-short boundaries
  - [x] Add --xfade-min threshold and per-boundary fallback styles (whitepop/blackflash/pulse/bloom)
  - [x] Guard: auto-hardcut when segment count is very high
  - [ ] Unit tests: verify fallback triggers and effect enable windows

- [ ] Phase 2d: Frame controls and overlays polish
  - [x] Add --frame-quantize nearest|floor|ceil
  - [x] Sticky counter overlays in both modes
  - [ ] Tests: counter continuity across clips; quantization correctness at 24/25/30 fps

- [ ] Phase 3: Presets and UX
  - [x] Presets: music-video, hypercut, slow-cinematic, documentary, edm-strobe
  - [x] Non-clobbering preset application; min-gap safety
  - [ ] Tests: preset mapping table; user overrides win; min-gap auto-adjust

- [ ] Phase 4: Musical structure
  - [ ] Downbeats/bars/phrases; half/double-time handling
  - [ ] Tempo change adaptation; local BPM windows
  - [ ] Optional cut bias to downbeats/phrase starts

- [ ] Phase 5: Auto phase/latency calibration
  - [ ] Generate calibration clip; search best --phase per track
  - [ ] Cache per-track phase in plan JSON; reuse

- [ ] Phase 6: Visual dynamics
  - [ ] On-beat Ken Burns (zoom/rotate pulses); color-matched fades
  - [ ] Energy-to-transition mapping; ramp durations

- [ ] Phase 7: Performance & robustness
  - [ ] Chunked xfade pipeline for large segment counts
  - [x] Use filter_complex_script to avoid arg-length limits
  - [ ] ffconcat input lists for very large image sets
  - [ ] Better progress/ETA; resume from temp

- [ ] Phase 8: Plans & tooling
  - [x] --plan-out/--plan-in planning JSON
  - [ ] Plan diff/inspect CLI; human-readable summaries
  - [ ] Preset JSON import/export

---

### ✅ Beat-Aligned: Test Plan (additions)

- Detection/selection
  - [ ] Mock aubio/librosa detectors; ensure cleaned beat list (no dups, min gap)
  - [ ] Window-constrained selection: respects [period_min, period_max]
  - [ ] Strategy=nearest correctness on synthetic beat grids

- Rendering correctness (mock ffmpeg)
  - [ ] Hardcuts: exact segment counts, per-segment frames match quantized durations
  - [ ] Transitions: offset/td_eff math for align=end|midpoint
  - [ ] Per-segment fallback: when td_eff < --xfade-min, chain uses concat not xfade
  - [ ] Fallback styles: enable window inserted at boundary (whitepop/blackflash/pulse/bloom)

- Overlays
  - [ ] Beat ticks render at provided beat times; overlay_guard suppresses near-landings
  - [ ] Counter persists between beats and across clip boundaries; never resets in mid-video

- Presets/CLI
  - [ ] Preset application is non-clobbering; explicit flags override
  - [ ] min-gap auto-enforcement >= 2*xfade+0.05
  - [ ] Plan I/O round-trip: --plan-out then --plan-in reproduces durations/images

- Performance/timeout
  - [ ] All ffmpeg/ffprobe commands use timeouts; tests prove non-hanging behavior
  - [ ] For large segment counts, renderer auto-selects hardcut path (guard tested)

- Integration E2E (fast)
  - [ ] 10-20s synthetic audio + 8 images; asserts muxed mp4 exists and basic size
  - [ ] --all-beats diagnostic path with hardcuts and overlays

Notes:
- Prefer mocking subprocess to keep runtime < 60s for whole suite.
- Avoid probing large outputs in tests; rely on planned durations and mocks.

*Last updated: $(date)*
*Total remaining features: 9 (including Beat-Aligned System)*
*Estimated total effort: 8-10 weeks*
