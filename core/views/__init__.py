"""
Core views module.
"""

from core.views.shift_views import (
    StartWorkShiftAPIView,
    CloseWorkShiftAPIView,
    CurrentWorkShiftAPIView,
    WorkShiftListAPIView,
    WorkShiftStatsAPIView,
)

__all__ = [
    'StartWorkShiftAPIView',
    'CloseWorkShiftAPIView',
    'CurrentWorkShiftAPIView',
    'WorkShiftListAPIView',
    'WorkShiftStatsAPIView',
]

