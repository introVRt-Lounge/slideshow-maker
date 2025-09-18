#!/usr/bin/env python3
"""
Tests for the transitions module
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slideshow_maker.transitions import (
    get_random_transition, get_transitions_by_category, get_transition_categories,
    get_transition_info, get_transition_description, get_all_transitions, get_transition_count
)


@pytest.mark.unit
class TestTransitions:
    """Test transition management functions"""
    
    def test_get_all_transitions(self):
        """Test getting all transitions"""
        transitions = get_all_transitions()
        assert isinstance(transitions, list)
        assert len(transitions) > 0
        assert 'fade' in transitions
    
    def test_get_transition_count(self):
        """Test getting transition count"""
        count = get_transition_count()
        assert isinstance(count, int)
        assert count > 0
        assert count == len(get_all_transitions())
    
    def test_get_random_transition(self):
        """Test getting random transition"""
        # Test multiple times to ensure randomness
        transitions = set()
        for _ in range(10):
            transition = get_random_transition()
            assert isinstance(transition, str)
            assert transition in get_all_transitions()
            transitions.add(transition)
        
        # With 10 random calls, we should get at least 2 different transitions
        # (unless there's only 1 transition, which there isn't)
        assert len(transitions) >= 2
    
    def test_get_transition_categories(self):
        """Test getting transition categories"""
        categories = get_transition_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert 'basic_fades' in categories
        assert 'wipe_effects' in categories
    
    def test_get_transitions_by_category(self):
        """Test getting transitions by category"""
        # Test valid category
        fade_transitions = get_transitions_by_category('basic_fades')
        assert isinstance(fade_transitions, list)
        assert 'fade' in fade_transitions
        assert 'fadeblack' in fade_transitions
        
        # Test invalid category
        invalid_transitions = get_transitions_by_category('nonexistent_category')
        assert invalid_transitions == []
    
    def test_get_transition_info(self):
        """Test getting transition info"""
        # Test valid transition
        info = get_transition_info('fade')
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'category' in info
        assert 'description' in info
        assert info['name'] == 'fade'
        assert info['category'] == 'basic_fades'
        
        # Test invalid transition
        invalid_info = get_transition_info('nonexistent_transition')
        assert invalid_info == {}
    
    def test_get_transition_description(self):
        """Test getting transition description"""
        # Test valid transition
        desc = get_transition_description('fade')
        assert isinstance(desc, str)
        assert len(desc) > 0
        assert 'crossfade' in desc.lower()
        
        # Test another transition
        desc2 = get_transition_description('wipeleft')
        assert isinstance(desc2, str)
        assert len(desc2) > 0
        assert 'wipe' in desc2.lower()
        
        # Test invalid transition
        invalid_desc = get_transition_description('nonexistent_transition')
        assert isinstance(invalid_desc, str)
        assert 'Unknown transition' in invalid_desc
    
    def test_transition_descriptions_completeness(self):
        """Test that all transitions have descriptions"""
        all_transitions = get_all_transitions()
        for transition in all_transitions:
            desc = get_transition_description(transition)
            assert isinstance(desc, str)
            assert len(desc) > 0
            assert desc != f'Unknown transition: {transition}'
    
    def test_transition_info_completeness(self):
        """Test that all transitions have info"""
        all_transitions = get_all_transitions()
        for transition in all_transitions:
            info = get_transition_info(transition)
            assert isinstance(info, dict)
            assert 'name' in info
            assert 'category' in info
            assert 'description' in info
            assert info['name'] == transition
    
    def test_category_consistency(self):
        """Test that categories are consistent with transitions"""
        all_transitions = get_all_transitions()
        all_categories = get_transition_categories()
        
        for category in all_categories:
            category_transitions = get_transitions_by_category(category)
            for transition in category_transitions:
                assert transition in all_transitions
                
                # Verify the transition's info matches the category
                info = get_transition_info(transition)
                assert info['category'] == category
