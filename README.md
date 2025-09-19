# VRChat Slideshow Maker

A powerful Python script that creates stunning slideshow videos from PNG images with smooth transitions, perfect for VRChat worlds and presentations.

## Features

🎬 **50+ Different Transition Types:**
- **Basic Fades**: fade, fadeblack, fadewhite, fadegrays
- **Wipe Effects**: wipeleft, wiperight, wipeup, wipedown, wipetl, wipetr, wipebl, wipebr
- **Slide Effects**: slideleft, slideright, slideup, slidedown
- **Smooth Effects**: smoothleft, smoothright, smoothup, smoothdown
- **Circle Effects**: circlecrop, circleclose, circleopen
- **Rectangle Effects**: rectcrop
- **Horizontal/Vertical**: horzclose, horzopen, vertclose, vertopen
- **Diagonal Effects**: diagbl, diagbr, diagtl, diagtr
- **Slice Effects**: hlslice, hrslice, vuslice, vdslice
- **Special Effects**: dissolve, pixelize, radial, hblur, distance
- **Squeeze Effects**: squeezev, squeezeh
- **Zoom Effects**: zoomin
- **Wind Effects**: hlwind, hrwind, vuwind, vdwind
- **Cover Effects**: coverleft, coverright, coverup, coverdown
- **Reveal Effects**: revealleft, revealright, revealup, revealdown

✨ **Advanced Features:**
- Text overlays showing transition names during playback
- Variable image durations (4-5 seconds by default)
- Automatic audio duration matching
- Chunked processing for reliability
- Progress reporting during creation
- Audio reuse for faster subsequent runs
- Support for multiple audio files (merged automatically)

## Requirements

- Python 3.6+
- FFmpeg (with xfade filter support)
- ImageMagick (for image metadata)

### Installation

```bash
# Install Python dependencies (if any)
pip install -r requirements.txt

# Ensure FFmpeg is installed
sudo apt-get install ffmpeg imagemagick
```

## Usage

### Basic Usage (New Modular Structure)

```bash
python3 main.py [image_directory]
```

### Command Line Options

- `--test`: Create a 1-minute test video instead of full duration
- `--min-duration SECONDS`: Minimum duration for each image (default: 3)
- `--max-duration SECONDS`: Maximum duration for each image (default: 5)

### Examples

```bash
# Create full slideshow from images in current directory
python3 main.py

# Create test slideshow (1 minute) from specific directory
python3 main.py --test /path/to/images

# Create slideshow with custom durations
python3 main.py --min-duration 3 --max-duration 6 /path/to/images
```

### Using as a Python Package

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

### Beat-Aligned Slideshow CLI

See docs/beatslides.md for the full reference of the `beatslides` command, including beat detection, selection windows, and on-beat debug overlays (markers, pulses, bloom, counters).

### Backward Compatibility

The old `slideshow.py` file is still available for backward compatibility:

```bash
# This still works
python3 slideshow.py /path/to/images
```

See [MIGRATION.md](MIGRATION.md) for detailed migration information.

## How It Works

1. **Image Processing**: Converts PNG images to video clips with variable durations
2. **Transition Creation**: Applies smooth transitions between image clips using FFmpeg's xfade filter
3. **Audio Merging**: Combines multiple MP3/M4A files into a single audio track
4. **Video Assembly**: Combines video slideshow with audio, looping video to match audio duration
5. **Text Overlays**: Adds transition names as text overlays for identification

## Transition Types

The script cycles through ALL 50+ FFmpeg xfade transition effects! Here's the complete list:

### Basic Fades (4 types)
- `fade` - Simple crossfade (default)
- `fadeblack` - Fade through black
- `fadewhite` - Fade through white  
- `fadegrays` - Fade through grayscale

### Wipe Effects (8 types)
- `wipeleft` - Wipe from left to right
- `wiperight` - Wipe from right to left
- `wipeup` - Wipe from bottom to top
- `wipedown` - Wipe from top to bottom
- `wipetl` - Wipe from top-left
- `wipetr` - Wipe from top-right
- `wipebl` - Wipe from bottom-left
- `wipebr` - Wipe from bottom-right

### Slide Effects (4 types)
- `slideleft` - Slide from left
- `slideright` - Slide from right
- `slideup` - Slide from bottom
- `slidedown` - Slide from top

### Smooth Effects (4 types)
- `smoothleft` - Smooth wipe from left
- `smoothright` - Smooth wipe from right
- `smoothup` - Smooth wipe from bottom
- `smoothdown` - Smooth wipe from top

### Circle Effects (3 types)
- `circlecrop` - Circular crop transition
- `circleclose` - Circle closing
- `circleopen` - Circle opening

### Rectangle Effects (1 type)
- `rectcrop` - Rectangular crop transition

### Horizontal/Vertical Effects (4 types)
- `horzclose` - Horizontal close
- `horzopen` - Horizontal open
- `vertclose` - Vertical close
- `vertopen` - Vertical open

### Diagonal Effects (4 types)
- `diagbl` - Diagonal bottom-left
- `diagbr` - Diagonal bottom-right
- `diagtl` - Diagonal top-left
- `diagtr` - Diagonal top-right

### Slice Effects (4 types)
- `hlslice` - Horizontal left slice
- `hrslice` - Horizontal right slice
- `vuslice` - Vertical up slice
- `vdslice` - Vertical down slice

### Special Effects (5 types)
- `dissolve` - Dissolve effect
- `pixelize` - Pixelize effect
- `radial` - Radial transition
- `hblur` - Horizontal blur
- `distance` - Distance effect

### Squeeze Effects (2 types)
- `squeezev` - Vertical squeeze
- `squeezeh` - Horizontal squeeze

### Zoom Effects (1 type)
- `zoomin` - Zoom in transition

### Wind Effects (4 types)
- `hlwind` - Horizontal left wind
- `hrwind` - Horizontal right wind
- `vuwind` - Vertical up wind
- `vdwind` - Vertical down wind

### Cover Effects (4 types)
- `coverleft` - Cover from left
- `coverright` - Cover from right
- `coverup` - Cover from bottom
- `coverdown` - Cover from top

### Reveal Effects (4 types)
- `revealleft` - Reveal from left
- `revealright` - Reveal from right
- `revealup` - Reveal from bottom
- `revealdown` - Reveal from top

**Total: 50+ transition types** - All based on the official [FFmpeg xfade documentation](https://trac.ffmpeg.org/wiki/Xfade)!

## Output

- `slideshow_with_audio.mp4` - Final video with slideshow and audio
- `audio_merged.m4a` - Merged audio file (reused on subsequent runs)

## Project Structure

### Modular Package Structure
```
slideshow-maker/
├── src/
│   └── slideshow_maker/          # Main package
│       ├── __init__.py           # Package initialization
│       ├── config.py             # Configuration and constants
│       ├── transitions.py        # Transition management (50+ effects)
│       ├── audio.py              # Audio processing
│       ├── video.py              # Video processing
│       ├── utils.py              # Utility functions
│       └── slideshow.py          # Main orchestrator
├── main.py                       # New entry point
├── setup.py                      # Package setup
├── slideshow.py                  # Legacy entry point (backward compatibility)
├── test_modular.py               # Test script
└── MIGRATION.md                  # Migration guide
```

### Input File Structure
```
/path/to/images/
├── image1.png
├── image2.png
├── audio1.mp3
├── audio2.mp3
└── ...
```

## Technical Details

- **Video Format**: H.264/AAC MP4
- **Resolution**: 1920x1080 (configurable)
- **Frame Rate**: 25 FPS
- **Quality**: CRF 23 (high quality)
- **Chunk Size**: 10 images per processing chunk

## VRChat Integration

Perfect for VRChat worlds:
- High-quality video output
- Smooth transitions between slides
- Audio synchronization
- Text overlays for presentation clarity
- Optimized file sizes for Unity import

## Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
sudo apt-get install ffmpeg
```

**Images not processing:**
- Ensure images are PNG format
- Check file permissions
- Verify ImageMagick is installed

**Transitions not working:**
- Update FFmpeg to latest version
- Check xfade filter availability
- Verify transition names are correct

**Audio sync issues:**
- Check audio file formats (MP3/M4A supported)
- Ensure audio files are not corrupted
- Verify FFmpeg audio processing capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the IntroVRt Lounge organization and is available under the MIT License.

## Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting section
- Review FFmpeg documentation for advanced usage

---

**Created by IntroVRt Lounge** - Making VR experiences more immersive! 🎭✨
