"""Visualization functions for eye tracking data."""

from .display import map, scanpath

# Create show object for backward compatibility
show = type('show', (), {'map': map, 'scanpath': scanpath})()

__all__ = ['map', 'scanpath', 'show']