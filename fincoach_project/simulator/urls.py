"""
URL routes for the simulator app.

Beginner note: each `path()` line maps a URL pattern to a Python
function in views.py. For example, visiting "/simulator/" runs the
`start_simulation` function.
"""

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "simulator"

urlpatterns = [
    path("", views.onboarding, name="onboarding"),
    path("meet/", views.meet, name="meet"),
    path("why-us/", views.why_us, name="why_us"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="simulator/login.html"), name="login"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("home/", views.home, name="home"),
    path("simulate/", views.start_simulation, name="start"),
    path("tracker/", views.tracker_app, name="tracker_app"),
    path("lessons/", views.lessons_app, name="lessons_app"),
    path("helper/", views.helper_app, name="helper_app"),

    # JSON API the Three.js frontend calls to know what scenario is next.
    path("api/current-scenario/", views.api_current_scenario, name="api_current_scenario"),

    # JSON API the frontend calls when the user picks a choice.
    path("api/submit-choice/", views.api_submit_choice, name="api_submit_choice"),

    # Results page shown after the simulation ends.
    path("results/", views.results, name="results"),
    # Embedded standalone HTML prototype (Three.js) — useful for mobile preview
    path("embedded/", views.embedded_simulator, name="embedded"),
]
