# Migration Guide: Monolithic to Modular Structure

This guide helps you migrate from the old monolithic `slideshow.py` to the new modular structure.

## What Changed

The single `slideshow.py` file has been split into a modular package structure:

```
slideshow-maker/
├── src/
│   └── slideshow_maker/
│       ├── __init__.py          # Package initialization
│       ├── config.py            # Configuration and constants
│       ├── transitions.py       # Transition management
│       ├── audio.py             # Audio processing
│       ├── video.py             # Video processing
│       ├── utils.py             # Utility functions
│       └── slideshow.py         # Main orchestrator
├── main.py                      # New entry point
├── setup.py                     # Package setup
└── slideshow.py                 # Old file (kept for compatibility)
```

## New Usage

### Option 1: Use the new main.py (Recommended)
```bash
# Instead of: python3 slideshow.py
python3 main.py

# With options:
python3 main.py --test /path/to/images
python3 main.py --min-duration 3 --max-duration 6 /path/to/images
```

### Option 2: Use as a Python package
```python
from slideshow_maker import create_slideshow_with_audio

# Create slideshow programmatically
success = create_slideshow_with_audio(
    image_dir="/path/to/images",
    test_mode=False,
    min_duration=3,
    max_duration=5
)
```

### Option 3: Use individual modules
```python
from slideshow_maker.transitions import get_random_transition, get_all_transitions
from slideshow_maker.audio import find_audio_files, merge_audio
from slideshow_maker.video import create_slideshow

# Use specific functionality
transitions = get_all_transitions()
random_transition = get_random_transition()
```

## Backward Compatibility

The old `slideshow.py` file is still present and functional, so existing scripts will continue to work:

```bash
# This still works
python3 slideshow.py /path/to/images
```

## New Features Available

### Transition Management
```python
from slideshow_maker import get_transition_categories, get_transitions_by_category

# Get all transition categories
categories = get_transition_categories()
print(categories)  # ['basic_fades', 'wipe_effects', ...]

# Get transitions in a specific category
fade_transitions = get_transitions_by_category('basic_fades')
print(fade_transitions)  # ['fade', 'fadeblack', 'fadewhite', 'fadegrays']
```

### Transition Information
```python
from slideshow_maker import get_transition_info, get_transition_description

# Get detailed info about a transition
info = get_transition_info('fade')
print(info)  # {'name': 'fade', 'category': 'basic_fades', 'description': 'Simple crossfade (default)'}

# Get just the description
desc = get_transition_description('wipeleft')
print(desc)  # 'Wipe from left to right'
```

### Configuration Access
```python
from slideshow_maker import TRANSITIONS, TRANSITION_CATEGORIES, DEFAULT_WIDTH

# Access configuration constants
print(f"Total transitions: {len(TRANSITIONS)}")
print(f"Default width: {DEFAULT_WIDTH}")
```

## Installation as Package

You can now install the slideshow maker as a Python package:

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]
```

## Benefits of Modular Structure

1. **Better Organization**: Code is split into logical modules
2. **Reusability**: Individual components can be imported and used separately
3. **Maintainability**: Easier to find and modify specific functionality
4. **Testability**: Each module can be tested independently
5. **Extensibility**: New features can be added as separate modules
6. **Documentation**: Each module has its own documentation

## Migration Steps

1. **No immediate action required** - old scripts continue to work
2. **Gradually migrate** to using `main.py` or the package imports
3. **Update scripts** to use the new modular imports when convenient
4. **Remove old `slideshow.py`** when you're ready (it's kept for compatibility)

## Testing the New Structure

Run the test script to verify everything works:

```bash
python3 test_modular.py
```

This will test all imports and basic functionality.

## Need Help?

If you encounter any issues with the new modular structure, please:
1. Check this migration guide
2. Run the test script to verify installation
3. Create an issue on GitHub with details about the problem
