#!/usr/bin/env python3
"""
Test script for rembg background removal functionality
"""

from rembg import remove, new_session
from PIL import Image, ImageDraw
import numpy as np
import time

def create_test_image():
    """Create a test image with a colored shape on transparent background"""
    # Create a new image with alpha channel
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))

    # Draw a red circle in the center
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill=(255, 0, 0, 255))

    return img

def test_rembg_basic():
    """Test basic rembg functionality"""
    print("Creating test image...")
    test_img = create_test_image()

    print("Testing rembg background removal...")
    start_time = time.time()

    # Remove background
    result = remove(test_img)

    end_time = time.time()
    print(".2f")

    print(f"Input image size: {test_img.size}")
    print(f"Output image mode: {result.mode}")
    print(f"Output image size: {result.size}")

    # Save test results
    test_img.save("test_input.png")
    result.save("test_output.png")

    print("Test images saved: test_input.png, test_output.png")
    return result

def test_rembg_session():
    """Test rembg with session reuse for better performance"""
    print("\nTesting rembg with session reuse...")

    # Create session (currently falls back to CPU)
    session = new_session()
    print(f"Session providers: {session.inner_session.get_providers()}")

    test_img = create_test_image()

    start_time = time.time()
    result = remove(test_img, session=session)
    end_time = time.time()

    print(".2f")
    return result

def test_rembg_mask_only():
    """Test getting only the mask"""
    print("\nTesting mask-only extraction...")

    test_img = create_test_image()
    mask = remove(test_img, only_mask=True)

    print(f"Mask type: {type(mask)}")
    print(f"Mask shape: {mask.shape if hasattr(mask, 'shape') else 'N/A'}")

    # Save mask
    if isinstance(mask, np.ndarray):
        mask_img = Image.fromarray((mask * 255).astype(np.uint8), mode='L')
        mask_img.save("test_mask.png")
        print("Mask saved: test_mask.png")

    return mask

if __name__ == "__main__":
    print("=== rembg Test Script ===")
    print("Testing background removal functionality...\n")

    try:
        test_rembg_basic()
        test_rembg_session()
        test_rembg_mask_only()

        print("\n✅ All tests completed successfully!")
        print("rembg is working and ready for integration into slideshow project.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
