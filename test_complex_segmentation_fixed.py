#!/usr/bin/env python3
"""
Test script for complex segmentation with multiple objects using rembg
"""

from PIL import Image, ImageDraw
import numpy as np
from rembg import remove, new_session
import time

def create_complex_test_image():
    """Create a test image with multiple distinct objects"""
    # Create a larger image with alpha channel
    img = Image.new('RGBA', (400, 400), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # Draw multiple distinct objects
    # 1. Red circle (top-left)
    draw.ellipse([50, 50, 150, 150], fill=(255, 0, 0, 255))

    # 2. Blue square (top-right)
    draw.rectangle([250, 50, 350, 150], fill=(0, 0, 255, 255))

    # 3. Green triangle (bottom-left)
    draw.polygon([(50, 250), (150, 250), (100, 350)], fill=(0, 255, 0, 255))

    # 4. Yellow star-like shape (bottom-right)
    draw.polygon([(250, 250), (275, 225), (300, 250), (325, 225), (350, 250),
                  (325, 275), (350, 300), (325, 325), (300, 300), (275, 325),
                  (250, 300), (275, 275)], fill=(255, 255, 0, 255))

    return img

def test_different_models():
    """Test different rembg models for complex segmentation"""
    print("🧪 Testing Complex Segmentation with Multiple Objects")
    print("=" * 60)

    # Create complex test image
    test_img = create_complex_test_image()
    test_img.save("complex_input.png")
    print("📷 Created complex test image with 4 distinct objects: complex_input.png")

    models_to_test = [
        ('u2net', 'Default U2Net (general purpose)'),
        ('sam', 'Segment Anything Model (advanced segmentation)'),
        ('birefnet_general', 'BiRefNet General (state-of-the-art)'),
    ]

    results = {}

    for model_name, description in models_to_test:
        print(f"\n🔬 Testing {model_name}: {description}")

        try:
            # Create session with specific model
            session = new_session(model_name)
            start_time = time.time()

            # Remove background
            result = remove(test_img, session=session)

            # Get mask only
            mask = remove(test_img, session=session, only_mask=True)

            end_time = time.time()
            processing_time = end_time - start_time

            # Save results
            result.save(f"complex_{model_name}_output.png")

            if isinstance(mask, np.ndarray):
                mask_img = Image.fromarray((mask * 255).astype(np.uint8), mode='L')
                mask_img.save(f"complex_{model_name}_mask.png")
            else:
                mask.save(f"complex_{model_name}_mask.png")

            results[model_name] = {
                'success': True,
                'time': processing_time,
                'description': description
            }

            print(f"  ✅ Success in {processing_time:.2f}s")
            print(f"     Output: complex_{model_name}_output.png")
            print(f"     Mask: complex_{model_name}_mask.png")

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results[model_name] = {
                'success': False,
                'error': str(e),
                'description': description
            }

    print(f"\n📊 Results Summary:")
    print("=" * 60)
    for model_name, result in results.items():
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(".2f")
        else:
            print(f"  {status} {model_name}: Failed - {result.get('error', 'Unknown error')}")

    return results

def analyze_masks():
    """Analyze the complexity of generated masks"""
    print(f"\n🔍 Analyzing Mask Complexity:")
    print("=" * 60)

    import os
    mask_files = [f for f in os.listdir('.') if f.startswith('complex_') and f.endswith('_mask.png')]

    for mask_file in mask_files:
        try:
            mask = Image.open(mask_file).convert('L')
            mask_array = np.array(mask)

            # Calculate mask complexity metrics
            unique_values = len(np.unique(mask_array))
            mean_value = np.mean(mask_array)
            std_value = np.std(mask_array)

            # Check for multiple segments (non-binary)
            is_binary = unique_values <= 2
            complexity_score = "Simple (binary)" if is_binary else f"Complex ({unique_values} levels)"

            print(f"🎭 {mask_file}:")
            print(f"     Complexity: {complexity_score}")
            print(".1f")
            print(".1f")

            # Show unique values if not too many
            if unique_values <= 10:
                unique_vals = sorted(np.unique(mask_array))
                print(f"     Values: {unique_vals}")

        except Exception as e:
            print(f"❌ Failed to analyze {mask_file}: {e}")

if __name__ == "__main__":
    try:
        results = test_different_models()
        analyze_masks()

        print("\n🎯 Key Findings:")
        print("=" * 60)

        successful_models = [m for m, r in results.items() if r['success']]
        if successful_models:
            print(f"✅ {len(successful_models)} models successfully processed complex multi-object image")
            print("📋 Check the generated mask files to see segmentation complexity!")

            # Highlight SAM specifically
            if 'sam' in successful_models:
                print("🎯 SAM (Segment Anything Model) is particularly promising for complex segmentation!")
        else:
            print("❌ No models were able to process the test image")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
