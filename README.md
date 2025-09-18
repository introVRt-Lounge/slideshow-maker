# VRChat Slideshow Maker

A powerful Python script that creates stunning slideshow videos from PNG images with smooth transitions, perfect for VRChat worlds and presentations.

## Features

🎬 **13 Different Transition Types:**
- Simple fade transitions
- Wipe effects (left, right, up, down)
- Smooth wipes (left, right)
- Circular and rectangular crop transitions
- Distance effects
- Fade through black/white
- Radial transitions

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

### Basic Usage

```bash
python3 slideshow.py [image_directory]
```

### Command Line Options

- `--test`: Create a 1-minute test video instead of full duration
- `--min-duration SECONDS`: Minimum duration for each image (default: 4)
- `--max-duration SECONDS`: Maximum duration for each image (default: 5)

### Examples

```bash
# Create full slideshow from images in current directory
python3 slideshow.py

# Create test slideshow (1 minute) from specific directory
python3 slideshow.py --test /path/to/images

# Create slideshow with custom durations
python3 slideshow.py --min-duration 3 --max-duration 6 /path/to/images
```

## How It Works

1. **Image Processing**: Converts PNG images to video clips with variable durations
2. **Transition Creation**: Applies smooth transitions between image clips using FFmpeg's xfade filter
3. **Audio Merging**: Combines multiple MP3/M4A files into a single audio track
4. **Video Assembly**: Combines video slideshow with audio, looping video to match audio duration
5. **Text Overlays**: Adds transition names as text overlays for identification

## Transition Types

The script cycles through 13 different transition effects:

1. `fade` - Simple crossfade
2. `wipeleft` - Wipe from left to right
3. `wiperight` - Wipe from right to left
4. `wipeup` - Wipe from bottom to top
5. `wipedown` - Wipe from top to bottom
6. `smoothleft` - Smooth wipe from left
7. `smoothright` - Smooth wipe from right
8. `circlecrop` - Circular crop transition
9. `rectcrop` - Rectangular crop transition
10. `distance` - Distance effect
11. `fadeblack` - Fade through black
12. `fadewhite` - Fade through white
13. `radial` - Radial transition

## Output

- `slideshow_with_audio.mp4` - Final video with slideshow and audio
- `audio_merged.m4a` - Merged audio file (reused on subsequent runs)

## File Structure

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
