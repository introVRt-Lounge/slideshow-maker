#!/usr/bin/env python3
"""
Test script to verify the modular structure works correctly
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        from slideshow_maker import (
            create_slideshow_with_audio,
            get_random_transition, get_transitions_by_category, get_transition_categories,
            get_transition_info, get_transition_description, get_all_transitions, get_transition_count,
            find_audio_files, merge_audio, combine_video_audio, get_total_audio_duration,
            create_slideshow,
            get_image_info, show_progress, run_command, get_audio_duration,
            TRANSITIONS, TRANSITION_CATEGORIES
        )
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_transitions():
    """Test transition functionality"""
    try:
        from slideshow_maker import get_all_transitions, get_transition_count, get_random_transition
        
        transitions = get_all_transitions()
        count = get_transition_count()
        random_transition = get_random_transition()
        
        print(f"✅ Found {count} transitions")
        print(f"✅ Random transition: {random_transition}")
        print(f"✅ First 5 transitions: {transitions[:5]}")
        return True
    except Exception as e:
        print(f"❌ Transition test error: {e}")
        return False

def test_config():
    """Test configuration values"""
    try:
        from slideshow_maker import TRANSITIONS, TRANSITION_CATEGORIES
        
        print(f"✅ Total transitions: {len(TRANSITIONS)}")
        print(f"✅ Transition categories: {len(TRANSITION_CATEGORIES)}")
        print(f"✅ Categories: {list(TRANSITION_CATEGORIES.keys())}")
        return True
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing modular structure...")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Transitions Test", test_transitions),
        ("Config Test", test_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular structure is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
