#!/usr/bin/env python3
"""
Background removal functionality for slideshow images using rembg
"""

import os
import time
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("⚠️  rembg not available - background removal disabled")

class BackgroundRemover:
    """Handles background removal for slideshow images"""

    def __init__(self, gpu_acceleration: bool = True):
        """
        Initialize background remover

        Args:
            gpu_acceleration: Whether to attempt GPU acceleration (falls back to CPU)
        """
        self.session = None
        # Honor env override to force CPU on Windows runs
        force_cpu = os.environ.get("REMBG_CPU_ONLY") == "1"
        self.gpu_acceleration = (not force_cpu) and gpu_acceleration and REMBG_AVAILABLE

        if REMBG_AVAILABLE:
            try:
                providers_to_use = ['CPUExecutionProvider']
                if self.gpu_acceleration:
                    try:
                        import onnxruntime as ort  # type: ignore
                        avail = set(getattr(ort, 'get_available_providers', lambda: [])())
                        if 'CUDAExecutionProvider' in avail:
                            providers_to_use = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                        else:
                            self.gpu_acceleration = False
                    except Exception:
                        # If ORT probe fails, stick to CPU to avoid noisy CUDA errors
                        self.gpu_acceleration = False
                        providers_to_use = ['CPUExecutionProvider']
                self.session = new_session(providers=providers_to_use)
                providers = self.session.inner_session.get_providers()
                if 'CUDAExecutionProvider' in providers:
                    print("🎨 Background removal: GPU acceleration enabled")
                else:
                    print("🎨 Background removal: CPU mode")
            except Exception as e:
                print(f"⚠️  Failed to initialize background remover: {e}")
                self.session = None
        else:
            print("🎨 Background removal: rembg not installed")

    def is_available(self) -> bool:
        """Check if background removal is available"""
        return REMBG_AVAILABLE and self.session is not None

    def remove_background(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Remove background from an image

        Args:
            image_path: Path to input image
            output_path: Path for output image (optional, auto-generated if None)

        Returns:
            Path to processed image, or None if failed
        """
        if not self.is_available():
            print(f"⚠️  Background removal not available for {image_path}")
            return image_path  # Return original if processing unavailable

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found: {image_path}")
            return None

        try:
            # Load image
            with Image.open(image_path) as img:
                # Convert to RGBA if needed
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                start_time = time.time()

                # Remove background
                result = remove(img, session=self.session)

                end_time = time.time()
                processing_time = end_time - start_time

                # Generate output path
                if output_path is None:
                    base, ext = os.path.splitext(image_path)
                    output_path = f"{base}_bg_removed{ext}"

                # Save result
                result.save(output_path)

                print(f"✅ Background removed in {processing_time:.2f}s: {output_path}")
                return output_path

        except Exception as e:
            print(f"❌ Failed to process {image_path}: {e}")
            return None

    def create_mask(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Create a binary mask from an image (foreground = white, background = black)

        Args:
            image_path: Path to input image
            output_path: Path for mask output (optional, auto-generated if None)

        Returns:
            Path to mask image, or None if failed
        """
        if not self.is_available():
            print(f"⚠️  Mask creation not available for {image_path}")
            return None

        try:
            with Image.open(image_path) as img:
                # Get mask only
                mask = remove(img, session=self.session, only_mask=True)

                # Generate output path in a 'masks' subfolder next to the image
                if output_path is None:
                    base_dir = os.path.dirname(image_path)
                    filename = os.path.basename(image_path)
                    name_no_ext, _ = os.path.splitext(filename)
                    mask_dir = os.path.join(base_dir, "masks")
                    try:
                        os.makedirs(mask_dir, exist_ok=True)
                    except Exception:
                        pass
                    output_path = os.path.join(mask_dir, f"{name_no_ext}_mask.png")
                # Skip regeneration if it already exists
                try:
                    if output_path and os.path.exists(output_path):
                        print(f"🎭 Mask exists, skipping: {output_path}")
                        return output_path
                except Exception:
                    pass

                # Save mask
                if isinstance(mask, np.ndarray):
                    # Convert numpy array to PIL Image
                    mask_img = Image.fromarray((mask * 255).astype(np.uint8), mode='L')
                    mask_img.save(output_path)
                else:
                    # Already a PIL Image
                    mask.save(output_path)

                print(f"🎭 Mask created: {output_path}")
                return output_path

        except Exception as e:
            print(f"❌ Failed to create mask for {image_path}: {e}")
            return None

    def process_batch(self, image_paths: List[str], output_dir: Optional[str] = None,
                     create_masks: bool = False) -> List[str]:
        """
        Process multiple images for background removal

        Args:
            image_paths: List of image paths to process
            output_dir: Directory for output files (optional)
            create_masks: Whether to also create masks for each image

        Returns:
            List of processed image paths
        """
        if not self.is_available():
            print("⚠️  Background removal not available - returning original paths")
            return image_paths

        processed_paths = []
        total_images = len(image_paths)

        print(f"🎨 Processing {total_images} images for background removal...")

        for i, image_path in enumerate(image_paths, 1):
            print(f"📷 [{i}/{total_images}] Processing: {os.path.basename(image_path)}")

            # Determine output path
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                filename = os.path.basename(image_path)
                base, ext = os.path.splitext(filename)
                output_path = os.path.join(output_dir, f"{base}_bg_removed{ext}")
            else:
                output_path = None

            # Remove background
            processed_path = self.remove_background(image_path, output_path)
            if processed_path:
                processed_paths.append(processed_path)

                # Create mask if requested
                if create_masks:
                    self.create_mask(image_path, None)  # Auto-generate mask path

        print(f"✅ Background removal complete: {len(processed_paths)}/{total_images} images processed")
        return processed_paths


def demo_background_removal():
    """Demo function showing background removal capabilities"""
    if not REMBG_AVAILABLE:
        print("❌ rembg not available for demo")
        return

    remover = BackgroundRemover()

    if not remover.is_available():
        print("❌ Background remover initialization failed")
        return

    print("\n🎨 Background Removal Demo")
    print("=" * 40)

    # Create a test image
    from PIL import ImageDraw
    test_img = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(test_img)

    # Draw some shapes
    draw.rectangle([50, 50, 250, 250], fill=(255, 0, 0, 255))  # Red square
    draw.ellipse([100, 100, 200, 200], fill=(0, 255, 0, 255))   # Green circle

    test_img.save("demo_input.png")
    print("📷 Created demo image: demo_input.png")

    # Remove background
    result_path = remover.remove_background("demo_input.png", "demo_output.png")
    if result_path:
        print(f"✅ Background removed: {result_path}")

    # Create mask
    mask_path = remover.create_mask("demo_input.png", "demo_mask.png")
    if mask_path:
        print(f"✅ Mask created: {mask_path}")

    print("\n🎨 Demo complete! Check demo_input.png, demo_output.png, and demo_mask.png")


if __name__ == "__main__":
    demo_background_removal()
