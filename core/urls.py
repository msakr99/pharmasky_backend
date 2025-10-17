"""
URL configuration for core app.
"""

from django.urls import path
from core import views


app_name = "core"

urlpatterns = [
    # Work Shift URLs
    path(
        "shifts/start/",
        views.StartWorkShiftAPIView.as_view(),
        name="shift-start",
    ),
    path(
        "shifts/close/",
        views.CloseWorkShiftAPIView.as_view(),
        name="shift-close",
    ),
    path(
        "shifts/current/",
        views.CurrentWorkShiftAPIView.as_view(),
        name="shift-current",
    ),
    path(
        "shifts/",
        views.WorkShiftListAPIView.as_view(),
        name="shifts-list",
    ),
    path(
        "shifts/stats/",
        views.WorkShiftStatsAPIView.as_view(),
        name="shifts-stats",
    ),
]

