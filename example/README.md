# Example Usage

This directory shows how to structure your files for the VRChat Slideshow Maker.

## File Structure

```
your-slideshow-folder/
├── slide_001.png    # First image (PNG format)
├── slide_002.png    # Second image
├── slide_003.png    # Third image
├── ...              # More images
├── background.mp3   # Background music (optional)
├── narration.mp3    # Narration audio (optional)
└── effects.m4a      # Sound effects (optional)
```

## Supported Formats

### Images
- **PNG** (recommended) - Lossless, supports transparency
- All images should be the same resolution for best results
- Recommended: 1920x1080 or 3840x2160 for VRChat

### Audio
- **MP3** - Most common format
- **M4A** - High quality, good compression
- **WAV** - Uncompressed (large files)
- Multiple audio files will be merged automatically

## Usage Examples

### Basic slideshow
```bash
# Place your PNG images in a folder with this script
python3 slideshow.py /path/to/your/images
```

### With custom durations
```bash
python3 slideshow.py --min-duration 3 --max-duration 7 /path/to/images
```

### Test mode (1 minute)
```bash
python3 slideshow.py --test /path/to/images
```

## Tips

1. **Image Quality**: Use high-resolution PNG images for best results
2. **Aspect Ratio**: All images should have the same aspect ratio
3. **Audio Length**: The slideshow will automatically loop to match audio duration
4. **File Names**: Images are processed in alphabetical order
5. **Transitions**: Each transition lasts 1 second and shows its name on screen

## Output

The script will create:
- `slideshow_with_audio.mp4` - Your final video
- `audio_merged.m4a` - Combined audio (reused on subsequent runs)

Enjoy creating amazing VRChat slideshows! 🎬✨
