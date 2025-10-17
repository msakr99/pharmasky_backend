"""
URL configuration for core app.
"""

from django.urls import path
from core.views import shift_views


app_name = "core"

urlpatterns = [
    # Work Shift URLs
    path(
        "shifts/start/",
        shift_views.StartWorkShiftAPIView.as_view(),
        name="shift-start",
    ),
    path(
        "shifts/close/",
        shift_views.CloseWorkShiftAPIView.as_view(),
        name="shift-close",
    ),
    path(
        "shifts/current/",
        shift_views.CurrentWorkShiftAPIView.as_view(),
        name="shift-current",
    ),
    path(
        "shifts/",
        shift_views.WorkShiftListAPIView.as_view(),
        name="shifts-list",
    ),
    path(
        "shifts/stats/",
        shift_views.WorkShiftStatsAPIView.as_view(),
        name="shifts-stats",
    ),
]

