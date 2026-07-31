"""
Project-level URL routing.

Beginner note: think of this as the "front desk" that looks at the
web address someone visited and decides which app/page should handle it.
We keep this file short by handing off most routes to each app's own
urls.py (see simulator/urls.py).
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
 
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="simulator:onboarding", permanent=False)),
    path("simulator/", include("simulator.urls")),
    # API and pages for the financial helper and tracker apps (used by iOS client)
    path("helper/", include("financial_helper.urls")),
    path("tracker/", include("tracker.urls")),
]
