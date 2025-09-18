#!/usr/bin/env python3
"""
VRChat Slideshow Creator - Main Entry Point
Creates a slideshow from PNG images with audio, much simpler than complex FFmpeg scripting.
Usage: python3 main.py [image_directory]
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slideshow_maker import create_slideshow_with_audio


def main():
    """Main entry point for the slideshow creator"""
    # Parse arguments
    args = sys.argv[1:]

    # Default values
    image_dir = "."
    test_mode = False
    min_duration = 3
    max_duration = 5

    # Parse command line arguments
    i = 0
    while i < len(args):
        if args[i] == "--test":
            test_mode = True
            i += 1
        elif args[i] == "--min-duration" and i + 1 < len(args):
            min_duration = int(args[i + 1])
            i += 2
        elif args[i] == "--max-duration" and i + 1 < len(args):
            max_duration = int(args[i + 1])
            i += 2
        elif not args[i].startswith("--"):
            image_dir = args[i]
            i += 1
        else:
            i += 1

    # Create the slideshow
    success = create_slideshow_with_audio(
        image_dir=image_dir,
        test_mode=test_mode,
        min_duration=min_duration,
        max_duration=max_duration
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
