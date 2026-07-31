"""
Django admin registration.

Beginner note: this is what unlocks the built-in Django admin site
(usually at /admin/) where your team can add and edit Scenarios and
Choices through a web form — no Python code needed. This is how your
content-writing teammates can add scenarios themselves.
"""

from django.contrib import admin
from .models import Scenario, Choice, SimulationRun, DecisionLog


class ChoiceInline(admin.TabularInline):
    """Lets choices be added directly on the Scenario edit page,
    instead of needing to visit a separate page for each one."""
    model = Choice
    extra = 1  # show 1 blank choice row ready to fill in


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "location_tag")
    ordering = ["order"]
    inlines = [ChoiceInline]


@admin.register(SimulationRun)
class SimulationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "session_key", "started_at", "completed_at", "current_savings", "current_debt")
    readonly_fields = [f.name for f in SimulationRun._meta.fields]


@admin.register(DecisionLog)
class DecisionLogAdmin(admin.ModelAdmin):
    list_display = ("run", "scenario", "choice", "made_at")
