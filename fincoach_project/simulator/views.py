"""
Views for the Life Simulator.

Beginner note: a "view" in Django is just a Python function that takes
a web request and returns a web response (an HTML page or, here, JSON
data for our Three.js frontend to use).

Flow for one simulation run:
  1. User visits "/simulator/" -> start_simulation() creates a
     SimulationRun tied to their browser session, renders the page
     with the 3D canvas.
  2. The Three.js JavaScript code calls /api/current-scenario/ to find
     out what scenario to show next (which location, what situation,
     what choice buttons to render).
  3. When the user clicks a choice, the JavaScript calls
     /api/submit-choice/, which updates the running totals in the
     database and logs the decision.
  4. Once there are no more scenarios, the frontend redirects to
     /simulator/results/, which shows the final summary + chart.
"""

import json
from decimal import Decimal

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_sameorigin
from pathlib import Path

from .forms import SignUpForm
from .models import Scenario, Choice, SimulationRun, DecisionLog


def _get_or_create_run(request) -> SimulationRun:
    """
    Finds the in-progress SimulationRun for this browser session, or
    creates a new one. This is how we track a user's progress without
    requiring login.
    """
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    run = (
        SimulationRun.objects.filter(session_key=session_key, completed_at__isnull=True)
        .order_by("-started_at")
        .first()
    )
    if run is None:
        run = SimulationRun.objects.create(session_key=session_key)
    return run


def onboarding(request):
    """Render the welcome onboarding flow before login/signup."""
    return render(request, "simulator/onboarding.html")


def signup(request):
    """Render and handle the signup screen."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("simulator:home"))
    else:
        form = SignUpForm()
    return render(request, "simulator/signup.html", {"form": form})


def meet(request):
    """Render the public product overview page."""
    return render(request, "simulator/meet.html")


def why_us(request):
    """Render the why-us page with FinCoach value props."""
    return render(request, "simulator/why_us.html")


def reset_password(request):
    """Render and handle a simple reset password request screen."""
    sent = False
    email = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            sent = True
    return render(request, "simulator/reset_password.html", {"sent": sent, "email": email})


@ensure_csrf_cookie  # makes sure the browser gets a CSRF cookie so our
                     # JavaScript can safely make POST requests later
@login_required
def start_simulation(request):
    """
    Renders the simulator inside the app shell.
    """
    run = _get_or_create_run(request)
    return render(request, "simulator/phone.html", {"run_id": run.id, "active": "simulate"})


@login_required
def home(request):
    """Render the home screen for the mobile app shell."""
    return render(request, "simulator/home.html", {"active": "home"})


@login_required
def tracker_app(request):
    """Render the tracker screen in the mobile app shell."""
    return render(request, "simulator/tracker_app.html", {"active": "tracker"})


@login_required
def lessons_app(request):
    """Render the lessons screen in the mobile app shell."""
    return render(request, "simulator/lessons.html", {"active": "lessons"})


@login_required
def helper_app(request):
    """Render the financial helper screen in the mobile app shell."""
    return render(request, "simulator/helper_app.html", {"active": "helper"})


def api_current_scenario(request):
    """
    Returns the next scenario (situation + choices) as JSON for the
    frontend to display. Returns {"done": true} once every scenario
    has been answered.
    """
    run = _get_or_create_run(request)

    answered_scenario_ids = DecisionLog.objects.filter(run=run).values_list(
        "scenario_id", flat=True
    )
    next_scenario = (
        Scenario.objects.exclude(id__in=answered_scenario_ids).order_by("order").first()
    )

    if next_scenario is None:
        return JsonResponse({"done": True})

    choices = [
        {"id": c.id, "label": c.label}
        for c in next_scenario.choices.all()
    ]

    return JsonResponse(
        {
            "done": False,
            "scenario_id": next_scenario.id,
            "title": next_scenario.title,
            "description": next_scenario.description,
            "location_tag": next_scenario.location_tag,
            "choices": choices,
        }
    )


def api_submit_choice(request):
    """
    Applies the effects of a chosen Choice to the SimulationRun's
    running totals, logs the decision, and returns the updated numbers
    plus feedback text.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    body = json.loads(request.body or "{}")
    choice_id = body.get("choice_id")
    choice = get_object_or_404(Choice, id=choice_id)

    run = _get_or_create_run(request)

    # Apply this choice's financial effects to the running totals.
    run.current_savings = run.current_savings - Decimal(choice.immediate_cost)
    run.current_debt = run.current_debt + Decimal(choice.debt_added)
    run.current_monthly_expenses = run.current_monthly_expenses + Decimal(choice.monthly_impact)
    run.save()

    DecisionLog.objects.create(run=run, scenario=choice.scenario, choice=choice)

    return JsonResponse(
        {
            "feedback": choice.feedback,
            "current_savings": float(run.current_savings),
            "current_debt": float(run.current_debt),
            "current_monthly_expenses": float(run.current_monthly_expenses),
        }
    )


def results(request):
    """
    Shows the final text summary + chart after the simulation ends.
    Marks the run as completed the first time this page is viewed.
    """
    run = _get_or_create_run(request)
    if run.completed_at is None:
        from django.utils import timezone
        run.completed_at = timezone.now()
        run.save()

    decisions = run.decisions.select_related("scenario", "choice").order_by("made_at")

    return render(
        request,
        "simulator/results.html",
        {
            "run": run,
            "decisions": decisions,
        },
    )


@xframe_options_sameorigin
def embedded_simulator(request):
    """Serve the standalone `life_simulator_realistic.html` so you can
    preview the Three.js prototype inside the Django site (useful for
    mobile device emulation in the browser).
    """
    base = Path(__file__).resolve().parents[1]
    html_file = base / "life_simulator_realistic.html"
    if not html_file.exists():
        return HttpResponse("Simulator HTML not found", status=404)
    return HttpResponse(html_file.read_text(encoding="utf-8"), content_type="text/html")
