# 🎵 Beat-Aligned Slideshow System - Build Plan

## 📋 Overview
This document outlines the complete build strategy for implementing the **Beat-Aligned Slideshow System** - a critical new feature that automatically detects musical beats and syncs image transitions to create professional music video-style slideshows.

**Status:** Ready to implement | **Priority:** Critical | **Effort:** 5 weeks | **Impact:** Very High

## 🎯 **Why This Feature is Critical**

### **User Value**
- **Professional quality**: Music video-style slideshows with perfect beat sync
- **Differentiation**: Sets us apart from basic slideshow creators
- **Automation**: No manual timing required - just point at audio + images
- **Flexibility**: Works with any music genre and tempo

### **Technical Feasibility**
- **Not research-grade**: Beat detection is solved (aubio/librosa)
- **Tractable complexity**: O(n) selection algorithm, fast on laptop
- **Leverages existing work**: Uses our 50+ transition system
- **Proven approach**: Based on established DSP techniques

## 🏗️ **Build Strategy Overview**

### **Phase 1: Core Beat Detection & Selection (Week 1)**
**Goal:** Get basic beat detection working with window-constrained selection algorithm

### **Phase 2: CLI Interface & Integration (Week 2)**
**Goal:** Create `beatslides` command that integrates with existing transition system

### **Phase 3: Testing & Validation (Week 3)**
**Goal:** Implement comprehensive test plan and ensure robustness

### **Phase 4: Polish & Advanced Features (Week 4)**
**Goal:** Add nice-to-have features and polish user experience

### **Phase 5: Integration & Documentation (Week 5)**
**Goal:** Full integration with existing system and complete documentation

---

## 📅 **Phase 1: Core Beat Detection & Selection (Week 1)**

### **1.1 Beat Detection Foundation**

#### **Create `beat_detection.py`**
```python
# Primary: aubio beat detection (aubio beat input.mp3 > beats.txt)
# Fallback: librosa beat tracking with onset strength analysis
# Beat validation and cleanup (remove duplicates, 120ms min gap)
# Simple CLI test: python3 -m slideshow_maker.beat_detection test.mp3
```

**Tasks:**
- [ ] **Primary beat detection**: `aubio` CLI integration
  - [ ] `aubio beat input.mp3 > beats.txt` command execution
  - [ ] Parse beats.txt output into Python list
  - [ ] Error handling for aubio failures

- [ ] **Fallback beat detection**: `librosa` integration
  - [ ] Onset strength analysis for beat tracking
  - [ ] Tempo estimation and beat detection
  - [ ] Fallback when aubio fails

- [ ] **Beat validation and cleanup**
  - [ ] Remove duplicate beats
  - [ ] Enforce 120ms minimum gap between beats
  - [ ] Sort beats in ascending order
  - [ ] Filter out beats before audio start

- [ ] **CLI testing interface**
  - [ ] `python3 -m slideshow_maker.beat_detection test.mp3`
  - [ ] Output beats to console and file
  - [ ] Validation and error reporting

#### **Create `beat_selection.py`**
```python
# Implement window-constrained selection algorithm exactly as written in redux
# Strict vs grace mode handling
# Min cut gap enforcement (2*xfade + 0.05s)
# Phase and latency compensation
```

**Tasks:**
- [ ] **Core selection algorithm**
  - [ ] Implement pseudocode exactly as written in redux
  - [ ] Window-constrained selection with `[PERIOD_MIN, PERIOD_MAX]`
  - [ ] Single pass with small windowed searches (O(n))

- [ ] **Error handling modes**
  - [ ] Strict mode: expand window by ±grace once
  - [ ] Non-strict mode: pick nearest beat and warn
  - [ ] Grace period expansion logic

- [ ] **Safety constraints**
  - [ ] Min cut gap enforcement (2*xfade + 0.05s)
  - [ ] Phase and latency compensation
  - [ ] Audio end trimming

- [ ] **Selection strategies**
  - [ ] `nearest` - closest to target period
  - [ ] `energy` - highest onset strength in window
  - [ ] `downbeat` - prefer downbeats when available
  - [ ] `hybrid` - combine strategies

### **1.2 Integration Points**

#### **Update `config.py`**
```python
# Add beat alignment constants
# Add beat detection settings
# Add selection strategy options
```

**Tasks:**
- [ ] **Beat alignment constants**
  - [ ] `PERIOD_MIN`, `PERIOD_MAX` defaults
  - [ ] `TARGET_PERIOD` default
  - [ ] `GRACE_PERIOD` default
  - [ ] `MIN_CUT_GAP` default

- [ ] **Beat detection settings**
  - [ ] `AUBIO_METHOD` default
  - [ ] `LIBROSA_METHOD` fallback
  - [ ] `MIN_BEAT_GAP` (120ms)
  - [ ] `BEAT_CONFIDENCE_THRESHOLD`

- [ ] **Selection strategy options**
  - [ ] `SELECTION_STRATEGIES` enum
  - [ ] `STRICT_MODE` default
  - [ ] `PHASE_COMPENSATION` default
  - [ ] `LATENCY_COMPENSATION` default

#### **Update `requirements.txt`**
```python
# Add audio processing dependencies
aubio>=0.4.9          # Primary beat detection
librosa>=0.9.0        # Fallback beat detection + analysis
numpy>=1.21.0         # Numerical analysis
soundfile>=0.10.0     # Audio file handling
```

---

## 📅 **Phase 2: CLI Interface & Integration (Week 2)**

### **2.1 CLI Implementation**

#### **Create `cli/beatslides.py`**
```python
# beatslides command with comprehensive parameter set
# --period MIN MAX for window constraints
# --target for desired average period
# --selection-strategy for beat selection method
# --strict and --grace for error handling
# --phase and --latency for timing compensation
# --transitions to use existing 50+ transition system
# --seed for deterministic output
```

**Tasks:**
- [ ] **Core CLI interface**
  - [ ] `beatslides` command with argument parsing
  - [ ] `--period MIN MAX` for window constraints
  - [ ] `--target` for desired average period
  - [ ] `--selection-strategy` (nearest, energy, downbeat, hybrid)

- [ ] **Error handling parameters**
  - [ ] `--strict` and `--grace` for error handling
  - [ ] `--phase` and `--latency` for timing compensation
  - [ ] `--seed` for deterministic output

- [ ] **Integration parameters**
  - [ ] `--transitions` to use existing 50+ transition system
  - [ ] `--output` for output file specification
  - [ ] `--verbose` for detailed logging

#### **Update `main.py`**
```python
# Add beatslides subcommand
# Integrate with existing argument parsing
# Add help text and examples
```

**Tasks:**
- [ ] **Subcommand integration**
  - [ ] Add `beatslides` subcommand to main CLI
  - [ ] Integrate with existing argument parsing
  - [ ] Add help text and examples

- [ ] **CLI examples**
  - [ ] Basic usage: `beatslides --period 5 10 --target 7.5 input.mp3 images/`
  - [ ] Advanced usage: `beatslides --period 3 8 --target 5 --strategy energy --transitions fade input.mp3 images/`
  - [ ] Help text and parameter descriptions

### **2.2 Transition System Integration**

#### **Update `video.py`**
```python
# Add beat-aligned rendering mode
# Use existing transition system for beat-aligned cuts
# Support all 50+ transitions (CPU and GPU)
# Add transition timing validation for beat constraints
```

**Tasks:**
- [ ] **Beat-aligned rendering**
  - [ ] Add `render_beat_aligned()` function
  - [ ] Integrate with existing transition system
  - [ ] Support all 50+ transitions (CPU and GPU)

- [ ] **Transition timing validation**
  - [ ] Validate transition duration fits beat constraints
  - [ ] Handle edge cases (transitions too long for segment)
  - [ ] Fallback to hard cuts when necessary

#### **Update `transitions.py`**
```python
# Add beat-aligned transition support
# Integrate with capability detection system
# Add transition timing validation
```

**Tasks:**
- [ ] **Beat-aligned transition support**
  - [ ] Add beat timing validation for transitions
  - [ ] Integrate with capability detection system
  - [ ] Support all transition types in beat-aligned mode

---

## 📅 **Phase 3: Testing & Validation (Week 3)**

### **3.1 Test Implementation**

#### **Create test files**
```python
# tests/test_beat_detection.py - Beat detection tests
# tests/test_beat_selection.py - Selection algorithm tests
# tests/test_beat_alignment.py - Integration tests
```

**Tasks:**
- [ ] **Beat detection tests**
  - [ ] Test aubio beat detection with known audio
  - [ ] Test librosa fallback when aubio fails
  - [ ] Test beat validation and cleanup
  - [ ] Test edge cases (no beats, invalid audio)

- [ ] **Selection algorithm tests**
  - [ ] Test window-constrained selection
  - [ ] Test strict vs non-strict modes
  - [ ] Test grace period expansion
  - [ ] Test min cut gap enforcement

- [ ] **Integration tests**
  - [ ] Test full beat-aligned slideshow generation
  - [ ] Test with different audio types
  - [ ] Test with different transition types
  - [ ] Test error handling and edge cases

### **3.2 Implement Test Plan**

#### **3-track validation approach**
```python
# 1. Steady 120 BPM track
# 2. Drifting live set track
# 3. Quiet ambient track with weak beats
```

**Tasks:**
- [ ] **Test track preparation**
  - [ ] Create or obtain 3 test tracks
  - [ ] Steady 120 BPM (electronic/dance)
  - [ ] Drifting live set (jazz/rock)
  - [ ] Quiet ambient (minimal beats)

- [ ] **Validation tests**
  - [ ] Run `--period 5 10 --target 7.5` with and without transitions
  - [ ] Verify: all cuts in beats.txt, deltas in [5,10]
  - [ ] Verify: no segment shorter than xfade requirement
  - [ ] Verify: end trimmed to audio length

- [ ] **Determinism tests**
  - [ ] Run twice with `--shuffle --seed 1337`
  - [ ] Verify: same plan.json output
  - [ ] Verify: same beat selection

### **3.3 Edge Case Handling**

#### **Implement edge case fixes from redux**
```python
# Sparse/breakdown sections (grace mode expansion)
# Tempo drifts (windowing sidesteps brittleness)
# False positives (120ms min beat gap)
# Transitions starving (min segment enforcement)
# Sync feel off (phase/latency knobs)
# Too few images (loop/truncate with deterministic shuffle)
```

**Tasks:**
- [ ] **Sparse sections handling**
  - [ ] Grace mode expansion when no beats in window
  - [ ] Nearest beat selection with warnings
  - [ ] Break or error when no solution found

- [ ] **Tempo drift handling**
  - [ ] Windowing approach sidesteps "every N beats" brittleness
  - [ ] Adaptive window sizing based on tempo changes
  - [ ] Tempo change detection and adaptation

- [ ] **False positive handling**
  - [ ] 120ms minimum beat gap enforcement
  - [ ] Beat confidence scoring
  - [ ] False positive detection and removal

- [ ] **Transition constraints**
  - [ ] Min segment >= 2*xfade + 0.05s enforcement
  - [ ] Fallback to hard cuts when necessary
  - [ ] Transition timing validation

- [ ] **Sync feel adjustments**
  - [ ] Phase compensation (-0.03s typical)
  - [ ] Latency compensation (+0.05s typical)
  - [ ] User-adjustable timing knobs

- [ ] **Image handling**
  - [ ] Loop images when too few
  - [ ] Truncate when too many
  - [ ] Deterministic shuffle with seed

---

## 📅 **Phase 4: Polish & Advanced Features (Week 4)**

### **4.1 Advanced Beat Analysis**

#### **Enhance beat detection**
```python
# Onset strength scoring for energy-based selection
# Downbeat estimation (optional, improves feel)
# Tempo change adaptation
# Beat confidence scoring
```

**Tasks:**
- [ ] **Onset strength analysis**
  - [ ] Calculate onset strength for each beat
  - [ ] Use for energy-based selection strategy
  - [ ] Cache onset strength for performance

- [ ] **Downbeat estimation**
  - [ ] Optional downbeat detection using librosa
  - [ ] Improve feel for certain music types
  - [ ] Fallback when downbeat detection fails

- [ ] **Tempo change adaptation**
  - [ ] Detect tempo changes in audio
  - [ ] Adapt window sizing based on tempo
  - [ ] Handle tempo transitions smoothly

- [ ] **Beat confidence scoring**
  - [ ] Score each detected beat for confidence
  - [ ] Use confidence in selection strategies
  - [ ] Filter low-confidence beats

### **4.2 User Experience**

#### **Add convenience features**
```python
# Preset modes: "dance", "ambient", "rock"
# Progress logging during beat detection
# Warning system for non-strict mode deviations
# Beat detection quality validation
```

**Tasks:**
- [ ] **Preset modes**
  - [ ] "dance" - fast tempo, short periods
  - [ ] "ambient" - slow tempo, long periods
  - [ ] "rock" - medium tempo, varied periods
  - [ ] Custom preset support

- [ ] **Progress logging**
  - [ ] Beat detection progress
  - [ ] Selection algorithm progress
  - [ ] Rendering progress
  - [ ] Time estimates

- [ ] **Warning system**
  - [ ] Non-strict mode deviations
  - [ ] Beat detection quality warnings
  - [ ] Transition constraint violations
  - [ ] Clear, actionable warnings

- [ ] **Quality validation**
  - [ ] Beat detection quality metrics
  - [ ] Selection algorithm validation
  - [ ] Output quality assessment
  - [ ] Recommendations for improvement

### **4.3 Output Features**

#### **Add output features**
```python
# Generate beats.txt for inspection
# Generate plan.json for debugging
# Add timing validation reports
```

**Tasks:**
- [ ] **Debug output**
  - [ ] Generate `beats.txt` for beat inspection
  - [ ] Generate `plan.json` for debugging
  - [ ] Add timing validation reports
  - [ ] Add selection algorithm logs

- [ ] **Validation reports**
  - [ ] Beat alignment accuracy report
  - [ ] Transition timing validation
  - [ ] Edge case handling report
  - [ ] Performance metrics

---

## 📅 **Phase 5: Integration & Documentation (Week 5)**

### **5.1 Full Integration**

#### **Complete integration**
```python
# Use existing capability detection system
# Support all transition types (CPU and GPU)
# Add to preview system (if implemented)
# Configuration file support (JSON/YAML)
```

**Tasks:**
- [ ] **Capability detection integration**
  - [ ] Use existing FFmpeg capability detection
  - [ ] Support both CPU and GPU transitions
  - [ ] Automatic fallback for unsupported transitions

- [ ] **Preview system integration**
  - [ ] Add beat-aligned preview generation
  - [ ] Fast preview mode for testing
  - [ ] Preview with beat visualization

- [ ] **Configuration file support**
  - [ ] JSON configuration files
  - [ ] YAML configuration files
  - [ ] Configuration validation
  - [ ] Default configuration templates

### **5.2 Performance Optimization**

#### **Performance optimization**
```python
# Beat detection caching
# Fast preview mode
# Memory optimization for long tracks
```

**Tasks:**
- [ ] **Caching system**
  - [ ] Cache beat detection results
  - [ ] Cache onset strength analysis
  - [ ] Cache selection algorithm results

- [ ] **Fast preview mode**
  - [ ] Low-resolution preview generation
  - [ ] Fast beat detection for previews
  - [ ] Preview with reduced quality

- [ ] **Memory optimization**
  - [ ] Streaming audio processing
  - [ ] Memory-efficient beat storage
  - [ ] Garbage collection optimization

### **5.3 Documentation & Examples**

#### **Update documentation**
```python
# Add beat alignment section to README
# Create beat alignment examples
# Add troubleshooting guide
# Update CLI help text
```

**Tasks:**
- [ ] **README updates**
  - [ ] Add beat alignment section
  - [ ] Add installation instructions
  - [ ] Add usage examples
  - [ ] Add troubleshooting guide

- [ ] **Example creation**
  - [ ] Example audio files for testing
  - [ ] Example configuration files
  - [ ] Example output comparisons
  - [ ] Example command lines

- [ ] **CLI help updates**
  - [ ] Comprehensive help text
  - [ ] Parameter descriptions
  - [ ] Usage examples
  - [ ] Error message explanations

---

## 🎯 **Success Criteria**

### **Core Functionality**
- [ ] All cuts land exactly on detected beats
- [ ] Inter-cut intervals respect `[PERIOD_MIN, PERIOD_MAX]` windows
- [ ] Selection adapts to tempo changes automatically
- [ ] Supports all existing 50+ transition types
- [ ] Graceful error handling with clear messages

### **Quality Assurance**
- [ ] Deterministic output with seed control
- [ ] Comprehensive test coverage (3-track test plan)
- [ ] Edge case handling (sparse sections, tempo drifts, etc.)
- [ ] Performance: O(n) selection, fast on laptop

### **User Experience**
- [ ] Simple CLI: `beatslides --period 5 10 --target 7.5 input.mp3 images/`
- [ ] Clear error messages and warnings
- [ ] Progress logging during processing
- [ ] Output validation and reporting

## 🚀 **Implementation Principles**

### **1. Leverage Existing System**
- **Don't reinvent**: Use existing 50+ transition system
- **Don't duplicate**: Use existing capability detection
- **Don't complicate**: Keep FFmpeg rendering simple

### **2. Follow Redux Pseudocode Exactly**
- **Window-constrained selection**: Implement exactly as written
- **Edge case handling**: Use proven fixes from redux
- **Test plan**: Follow 3-track validation approach

### **3. Keep It Practical**
- **aubio first**: CLI beat detection, librosa fallback
- **Simple rendering**: One FFmpeg call, keep filtergraph simple
- **Deterministic**: Seed control for reproducible output

### **4. Progressive Enhancement**
- **Phase 1**: Basic beat detection + selection
- **Phase 2**: CLI + transition integration
- **Phase 3**: Testing + edge cases
- **Phase 4**: Advanced features + polish
- **Phase 5**: Full integration + docs

## 📊 **Effort Estimation**

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | 1 week | Beat detection + selection algorithm |
| **Phase 2** | 1 week | CLI interface + transition integration |
| **Phase 3** | 1 week | Test implementation + edge cases |
| **Phase 4** | 1 week | Advanced features + UX polish |
| **Phase 5** | 1 week | Full integration + documentation |
| **Total** | **5 weeks** | **Complete beat-aligned system** |

## 🔧 **Technical Dependencies**

### **New Dependencies**
```python
aubio>=0.4.9          # Primary beat detection
librosa>=0.9.0        # Fallback beat detection + analysis
numpy>=1.21.0         # Numerical analysis
soundfile>=0.10.0     # Audio file handling
```

### **Existing Dependencies**
- FFmpeg (already required)
- Python 3.7+ (already required)
- Existing transition system (already implemented)
- Existing capability detection (already implemented)

## 🎵 **Next Immediate Steps**

1. **Start Phase 1**: Create `beat_detection.py` with aubio integration
2. **Implement pseudocode**: Create `beat_selection.py` exactly as written in redux
3. **Add dependencies**: Update `requirements.txt` with audio libraries
4. **Test with simple case**: 120 BPM track, basic window selection

## 📝 **Notes**

- All phases build incrementally on previous work
- Each phase includes comprehensive testing
- Edge case handling is built in from the start
- Performance optimization is considered throughout
- User experience is prioritized in all implementations

---

*Last updated: $(date)*
*Total estimated effort: 5 weeks*
*Ready to implement: Phase 1*
