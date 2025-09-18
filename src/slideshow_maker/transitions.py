#!/usr/bin/env python3
"""
Transition management for the VRChat Slideshow Maker
"""

import random
from .config import TRANSITIONS, TRANSITION_CATEGORIES


def get_random_transition():
    """Get a random transition from all available transitions"""
    return random.choice(TRANSITIONS)


def get_transitions_by_category(category):
    """Get all transitions in a specific category"""
    return TRANSITION_CATEGORIES.get(category, [])


def get_transition_categories():
    """Get all available transition categories"""
    return list(TRANSITION_CATEGORIES.keys())


def get_transition_info(transition_name):
    """Get information about a specific transition"""
    category_info = {}
    for category, transitions in TRANSITION_CATEGORIES.items():
        if transition_name in transitions:
            category_info = {
                'name': transition_name,
                'category': category,
                'description': get_transition_description(transition_name)
            }
            break
    
    return category_info


def get_transition_description(transition_name):
    """Get a human-readable description of a transition"""
    descriptions = {
        # Basic fades
        'fade': 'Simple crossfade (default)',
        'fadeblack': 'Fade through black',
        'fadewhite': 'Fade through white',
        'fadegrays': 'Fade through grayscale',
        
        # Wipe effects
        'wipeleft': 'Wipe from left to right',
        'wiperight': 'Wipe from right to left',
        'wipeup': 'Wipe from bottom to top',
        'wipedown': 'Wipe from top to bottom',
        'wipetl': 'Wipe from top-left',
        'wipetr': 'Wipe from top-right',
        'wipebl': 'Wipe from bottom-left',
        'wipebr': 'Wipe from bottom-right',
        
        # Slide effects
        'slideleft': 'Slide from left',
        'slideright': 'Slide from right',
        'slideup': 'Slide from bottom',
        'slidedown': 'Slide from top',
        
        # Smooth effects
        'smoothleft': 'Smooth wipe from left',
        'smoothright': 'Smooth wipe from right',
        'smoothup': 'Smooth wipe from bottom',
        'smoothdown': 'Smooth wipe from top',
        
        # Circle effects
        'circlecrop': 'Circular crop transition',
        'circleclose': 'Circle closing',
        'circleopen': 'Circle opening',
        
        # Rectangle effects
        'rectcrop': 'Rectangular crop transition',
        
        # Horizontal/Vertical effects
        'horzclose': 'Horizontal close',
        'horzopen': 'Horizontal open',
        'vertclose': 'Vertical close',
        'vertopen': 'Vertical open',
        
        # Diagonal effects
        'diagbl': 'Diagonal bottom-left',
        'diagbr': 'Diagonal bottom-right',
        'diagtl': 'Diagonal top-left',
        'diagtr': 'Diagonal top-right',
        
        # Slice effects
        'hlslice': 'Horizontal left slice',
        'hrslice': 'Horizontal right slice',
        'vuslice': 'Vertical up slice',
        'vdslice': 'Vertical down slice',
        
        # Special effects
        'dissolve': 'Dissolve effect',
        'pixelize': 'Pixelize effect',
        'radial': 'Radial transition',
        'hblur': 'Horizontal blur',
        'distance': 'Distance effect',
        
        # Squeeze effects
        'squeezev': 'Vertical squeeze',
        'squeezeh': 'Horizontal squeeze',
        
        # Zoom effects
        'zoomin': 'Zoom in transition',
        
        # Wind effects
        'hlwind': 'Horizontal left wind',
        'hrwind': 'Horizontal right wind',
        'vuwind': 'Vertical up wind',
        'vdwind': 'Vertical down wind',
        
        # Cover effects
        'coverleft': 'Cover from left',
        'coverright': 'Cover from right',
        'coverup': 'Cover from bottom',
        'coverdown': 'Cover from top',
        
        # Reveal effects
        'revealleft': 'Reveal from left',
        'revealright': 'Reveal from right',
        'revealup': 'Reveal from bottom',
        'revealdown': 'Reveal from top',
    }
    
    return descriptions.get(transition_name, f'Unknown transition: {transition_name}')


def get_all_transitions():
    """Get all available transitions"""
    return TRANSITIONS.copy()


def get_transition_count():
    """Get the total number of available transitions"""
    return len(TRANSITIONS)
