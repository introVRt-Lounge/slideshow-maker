# Test Suite Summary

## Overview
Comprehensive test suite for the VRChat Slideshow Maker modular codebase.

## Test Structure

### Unit Tests (Fast - < 1 second each)
- **test_config.py** - Configuration constants and values (13 tests)
- **test_transitions.py** - Transition management functions (10 tests)  
- **test_utils.py** - Utility functions (13 tests)
- **test_audio.py** - Audio processing functions (12 tests)
- **test_video.py** - Video processing functions (10 tests)
- **test_slideshow.py** - Main slideshow functionality (12 tests)

### Integration Tests (Slower - 2-5 seconds each)
- **test_integration.py** - End-to-end workflow tests (4 tests)

## Test Categories

### Fast Tests (Recommended for development)
```bash
python3 run_tests.py --type fast
```

### Unit Tests Only
```bash
python3 run_tests.py --type unit
```

### All Tests
```bash
python3 run_tests.py --type all
```

### Specific Test File
```bash
python3 run_tests.py --test test_config.py
```

## Test Coverage

The test suite covers:
- ✅ All 50+ transition types and categories
- ✅ Configuration constants and validation
- ✅ Audio file discovery and processing
- ✅ Video creation and transition application
- ✅ Error handling and edge cases
- ✅ Integration workflows
- ✅ Mocked external dependencies (FFmpeg, ImageMagick)

## Running Tests

### Quick Test (Recommended)
```bash
python3 run_tests.py --test test_config.py
python3 run_tests.py --test test_transitions.py
```

### Full Test Suite
```bash
python3 run_tests.py --type all --verbose
```

### With Coverage Report
```bash
python3 run_tests.py --type all --coverage
```

## Test Dependencies

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

## Test Results

- **Total Tests**: 81
- **Unit Tests**: 77 (fast)
- **Integration Tests**: 4 (slower)
- **Coverage**: All major functions and edge cases
- **Mocking**: External dependencies properly mocked

## Notes

- Tests use pytest with comprehensive mocking
- External tools (FFmpeg, ImageMagick) are mocked for speed
- Tests run in isolated temporary directories
- All tests are deterministic and repeatable
- Fast tests are suitable for continuous integration
