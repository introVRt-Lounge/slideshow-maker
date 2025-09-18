#!/usr/bin/env python3
"""
Utility functions for the VRChat Slideshow Maker
"""

import os
import subprocess


def get_image_info(image_path):
    """Get basic info about an image"""
    try:
        # Use identify command (ImageMagick) if available
        cmd = f'identify -format "📏 %wx%h 📷 %[colorspace] 🎨 %[channels]" "{image_path}" 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    try:
        # Fallback to file command
        cmd = f'file "{image_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"📄 {result.stdout.strip()}"
    except:
        pass

    return f"🖼️ {os.path.basename(image_path)}"


def show_progress(current, total, image_path=None, transition=None):
    """Show progress with image info"""
    percentage = (current / total) * 100
    progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))

    status_line = f"🔄 Progress: [{progress_bar}] {percentage:.1f}% ({current}/{total})"

    if image_path and transition:
        # Show detailed info for transition processing
        image_info = get_image_info(image_path)
        print(f"\n{status_line}")
        print(f"  🎯 Processing: {image_info}")
        print(f"  ✨ Transition: {transition}")
    else:
        # Simple progress for other operations
        print(f"\r{status_line}", end="", flush=True)


def run_command(cmd, description="", show_output=False):
    """Run a command and return True if successful"""
    try:
        if show_output:
            print(f"⚡ {description}")
        else:
            print(f"⚙️  {description}", end="", flush=True)

        result = subprocess.run(cmd, shell=True, check=True, capture_output=not show_output, text=True)

        if not show_output:
            print(" ✅" if result.returncode == 0 else " ❌")

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if show_output and e.output:
            print(f"Output: {e.output}")
        return False


def get_audio_duration(audio_file):
    """Get duration of an audio file in seconds"""
    try:
        cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_file}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return 0.0


def get_ffmpeg_path():
    """Get the path to FFmpeg executable"""
    # Try to find FFmpeg in common locations
    common_paths = [
        'ffmpeg',  # In PATH
        'ffmpeg.exe',  # Windows
        '/usr/bin/ffmpeg',  # Linux
        '/usr/local/bin/ffmpeg',  # macOS
        'C:\\ffmpeg\\bin\\ffmpeg.exe',  # Windows common
    ]
    
    for path in common_paths:
        try:
            if path in ['ffmpeg', 'ffmpeg.exe']:
                # Check if it's in PATH
                result = subprocess.run([path, '-version'], capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            else:
                # Check if file exists
                if os.path.exists(path):
                    return path
        except:
            continue
    
    # Fallback to 'ffmpeg' if nothing else works
    return 'ffmpeg'


def detect_ffmpeg_capabilities():
    """Detect FFmpeg capabilities for transitions"""
    capabilities = {
        'xfade_available': False,
        'xfade_opencl_available': False,
        'opencl_available': False,
        'gpu_transitions_supported': False,
        'cpu_transitions_supported': False
    }
    
    ffmpeg_path = get_ffmpeg_path()
    
    try:
        # Check if xfade filter is available
        cmd = f'"{ffmpeg_path}" -f lavfi -i "color=red:size=320x240:duration=1" -f lavfi -i "color=blue:size=320x240:duration=1" -filter_complex "[0][1]xfade=transition=fade:duration=0.5:offset=0.5" -t 1 -f null - 2>&1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            capabilities['xfade_available'] = True
            capabilities['cpu_transitions_supported'] = True
    except:
        pass
    
    try:
        # Check if xfade_opencl is available with proper RGBA format handling
        cmd = f'"{ffmpeg_path}" -init_hw_device opencl=ocl:0.0 -filter_hw_device ocl -f lavfi -i "color=red:size=320x240:duration=1" -f lavfi -i "color=blue:size=320x240:duration=1" -filter_complex "[0:v]format=rgba,hwupload=extra_hw_frames=16[0hw];[1:v]format=rgba,hwupload=extra_hw_frames=16[1hw];[0hw][1hw]xfade_opencl=transition=fade:duration=0.5:offset=0.5,hwdownload,format=yuv420p" -t 1 -f null - 2>&1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            capabilities['xfade_opencl_available'] = True
            capabilities['gpu_transitions_supported'] = True
    except:
        pass
    
    try:
        # Check if OpenCL is available
        cmd = f'"{ffmpeg_path}" -f lavfi -i "color=red:size=320x240:duration=1" -vf "scale_opencl=w=640:h=480" -t 1 -f null - 2>&1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            capabilities['opencl_available'] = True
    except:
        pass
    
    return capabilities


def get_available_transitions():
    """Get list of transitions available based on FFmpeg capabilities"""
    from .config import CPU_TRANSITIONS, GPU_TRANSITIONS
    
    capabilities = detect_ffmpeg_capabilities()
    available_transitions = []
    
    if capabilities['cpu_transitions_supported']:
        available_transitions.extend(CPU_TRANSITIONS)
    
    if capabilities['gpu_transitions_supported']:
        available_transitions.extend(GPU_TRANSITIONS)
    
    return available_transitions, capabilities


def detect_nvenc_support():
    """Detect if NVENC hardware encoding is available"""
    ffmpeg_path = get_ffmpeg_path()
    
    try:
        # Check if h264_nvenc encoder is available
        cmd = f'"{ffmpeg_path}" -hide_banner -encoders 2>&1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and 'h264_nvenc' in result.stdout:
            return True
    except:
        pass
    
    return False


def print_ffmpeg_capabilities():
    """Print FFmpeg capabilities information"""
    from .config import CPU_TRANSITIONS, GPU_TRANSITIONS
    
    capabilities = detect_ffmpeg_capabilities()
    nvenc_available = detect_nvenc_support()
    
    print("🔍 FFmpeg Capability Detection:")
    print(f"  📊 xfade filter (CPU): {'✅ Available' if capabilities['xfade_available'] else '❌ Not available'}")
    print(f"  🚀 xfade_opencl (GPU): {'✅ Available' if capabilities['xfade_opencl_available'] else '❌ Not available'}")
    print(f"  🎮 OpenCL support: {'✅ Available' if capabilities['opencl_available'] else '❌ Not available'}")
    print(f"  🚀 NVENC encoding: {'✅ Available' if nvenc_available else '❌ Not available'}")
    
    if capabilities['cpu_transitions_supported']:
        print(f"  💻 CPU transitions: ✅ {len(CPU_TRANSITIONS)} available")
    else:
        print("  💻 CPU transitions: ❌ Not supported")
    
    if capabilities['gpu_transitions_supported']:
        print(f"  🎮 GPU transitions: ✅ {len(GPU_TRANSITIONS)} available")
    else:
        print("  🎮 GPU transitions: ❌ Not supported")
    
    total_available = len(get_available_transitions()[0])
    print(f"  🎬 Total transitions: {total_available}")
    
    if nvenc_available:
        print("  🚀 GPU encoding available - faster video processing!")
    else:
        print("  💻 Using CPU encoding")
    
    if not capabilities['xfade_available'] and not capabilities['xfade_opencl_available']:
        print("  ⚠️  WARNING: No xfade support detected! Transitions may not work.")
        print("     Install FFmpeg with xfade filter support.")
    
    return capabilities
