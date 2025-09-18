#!/usr/bin/env python3
"""
Setup script for VRChat Slideshow Maker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slideshow-maker",
    version="2.0.0",
    author="IntroVRt Lounge",
    author_email="contact@introVRt-lounge.com",
    description="VRChat Slideshow Maker with 50+ transition effects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/introVRt-Lounge/slideshow-maker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        # No Python dependencies required - uses external FFmpeg and ImageMagick
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "slideshow-maker=slideshow_maker.slideshow:create_slideshow_with_audio",
        ],
    },
    keywords="slideshow, video, ffmpeg, transitions, vrchat, multimedia",
    project_urls={
        "Bug Reports": "https://github.com/introVRt-Lounge/slideshow-maker/issues",
        "Source": "https://github.com/introVRt-Lounge/slideshow-maker",
        "Documentation": "https://github.com/introVRt-Lounge/slideshow-maker#readme",
    },
)
