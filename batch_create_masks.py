#!/usr/bin/env python3
"""
Batch process images to create masks using rembg
"""

import os
import sys
import glob
from pathlib import Path

# Add src directory to path so we can import slideshow_maker
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slideshow_maker.background_removal import BackgroundRemover

def find_images(directory, extensions=['*.png', '*.jpg', '*.jpeg', '*.bmp']):
    """Find all image files in directory"""
    images = []
    for ext in extensions:
        pattern = os.path.join(directory, ext)
        images.extend(glob.glob(pattern))
    return sorted(images)

def create_masks_for_directory(input_dir, output_dir):
    """Create masks for all images in input directory"""
    print("🎨 Batch Mask Creation Started")
    print("=" * 60)

    # Find all images
    images = find_images(input_dir)
    if not images:
        print(f"❌ No images found in {input_dir}")
        return

    print(f"📁 Found {len(images)} images to process")
    print(f"📂 Output directory: {output_dir}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize background remover
    remover = BackgroundRemover(gpu_acceleration=True)

    if not remover.is_available():
        print("❌ Background remover not available")
        return

    # Process each image
    successful = 0
    failed = 0

    for i, image_path in enumerate(images, 1):
        filename = os.path.basename(image_path)
        base_name = os.path.splitext(filename)[0]

        print(f"🎭 [{i}/{len(images)}] Processing: {filename}")

        # Create mask
        mask_path = os.path.join(output_dir, f"{base_name}_mask.png")
        result = remover.create_mask(image_path, mask_path)

        if result:
            successful += 1
            print(f"     ✅ Mask created: {os.path.basename(result)}")
        else:
            failed += 1
            print("     ❌ Failed to create mask")

    print("\n" + "=" * 60)
    print("🎯 Batch Processing Complete!")
    print(f"✅ Successfully processed: {successful} images")
    print(f"❌ Failed: {failed} images")
    print(f"📂 Masks saved to: {output_dir}")

if __name__ == "__main__":
    import sys

    # Default to test-slideshow, but allow command line arguments
    if len(sys.argv) >= 2:
        input_directory = sys.argv[1]
        output_directory = os.path.join(input_directory, "masks")
    else:
        # Process the test-slideshow directory
        input_directory = r"W:\test-slideshow"
        output_directory = r"W:\test-slideshow\masks"

    create_masks_for_directory(input_directory, output_directory)
