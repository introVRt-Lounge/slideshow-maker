#!/usr/bin/env python3
"""
Debug CLI issues - repeatable script
"""
import os
import sys
import subprocess

def debug_cli():
    """Debug the CLI by running it with verbose output"""

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = "/home/heavygee/coding/slideshow-maker/src"

    # Test directory
    test_dir = "/home/heavygee/coding/slideshow-maker/runtime-smoke-testing/temp_classic_20250923_233929"

    if not os.path.exists(test_dir):
        print(f"❌ Test directory doesn't exist: {test_dir}")
        return False

    # Count images
    import glob
    images = glob.glob(os.path.join(test_dir, "*.png"))
    print(f"🖼️  Found {len(images)} images in {test_dir}")

    # Run CLI with verbose output
    cmd = [
        sys.executable, "-m", "slideshow_maker.cli.slideshow_cli",
        test_dir, "--min-duration", "1.5", "--max-duration", "3.0"
    ]

    print(f"🎬 Running: {' '.join(cmd)}")
    print(f"📂 CWD: /home/heavygee/coding/slideshow-maker")
    print(f"🐍 PYTHONPATH: {env.get('PYTHONPATH')}")

    result = subprocess.run(
        cmd,
        cwd="/home/heavygee/coding/slideshow-maker",
        env=env,
        capture_output=False,  # Show output live
        text=True
    )

    print(f"\\n📊 Exit code: {result.returncode}")

    if result.returncode != 0:
        print("❌ CLI FAILED")
        return False
    else:
        print("✅ CLI SUCCESS")
        return True

if __name__ == "__main__":
    success = debug_cli()
    sys.exit(0 if success else 1)
