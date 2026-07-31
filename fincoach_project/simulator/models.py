"""
Data models for the Life Simulator feature.

Beginner note: each class below becomes a database table. Each field
becomes a column. Django handles turning these into real SQL for us —
we never write SQL directly.

There's no login system yet (per our decision), so a SimulationRun
isn't tied to a specific logged-in user yet — it's tracked by a
session key instead. When we add accounts later, we can add a
`user = models.ForeignKey(...)` field without breaking anything.
"""

from django.conf import settings
from django.db import models


class Scenario(models.Model):
    """
    One 'stop' in the life simulation — e.g. "Your car breaks down"
    or "You just graduated and need your first apartment."

    'order' controls what sequence scenarios appear in during the
    simulation (1st, 2nd, 3rd...).
    """

    title = models.CharField(max_length=120)
    description = models.TextField(
        help_text="The situation text shown to the user, e.g. "
        "'Your car won't start and the mechanic says it needs a new transmission.'"
    )
    order = models.PositiveIntegerField(
        help_text="Position in the simulation sequence (1 = first scenario)."
    )
    location_tag = models.CharField(
        max_length=50,
        help_text="Which 3D scene/location this happens at, e.g. 'mechanic_shop', "
        "'bank', 'apartment'. The Three.js frontend uses this to know which "
        "environment to load.",
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title}"


class Choice(models.Model):
    """
    One option a user can pick in response to a Scenario.
    Example: for "car breaks down", choices might be
    "Pay for repair in full", "Take out a loan", "Buy a used car instead".
    """

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=120, help_text="Short text shown on the choice button.")

    # These numbers get applied to the user's running totals when chosen.
    # Positive = money gained, negative = money spent. Keeping this simple
    # (one-time cost) for v1 — recurring costs can be added later.
    immediate_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="One-time cost of this choice (enter as a positive number)."
    )
    monthly_impact = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Ongoing monthly cost (positive) or savings (negative) from this choice."
    )
    debt_added = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Any new debt this choice creates (e.g. taking a loan)."
    )
    feedback = models.TextField(
        blank=True,
        help_text="Short explanation shown after picking this, e.g. why it was "
        "a smart or risky move."
    )

    def __str__(self):
        return f"{self.scenario.title} -> {self.label}"


class SimulationRun(models.Model):
    """
    One complete playthrough of the Life Simulator by a user.
    Tracks their starting numbers and running totals as they
    move through scenarios.
    """

    session_key = models.CharField(
        max_length=40,
        help_text="Identifies which browser session this run belongs to, "
        "since we don't have logins yet.",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Starting financial snapshot, collected before the simulation begins.
    starting_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    starting_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Running totals, updated as the user makes choices.
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_monthly_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Run {self.id} ({'completed' if self.completed_at else 'in progress'})"


class DecisionLog(models.Model):
    """
    A record of one choice a user made during a specific SimulationRun.
    Keeping this history lets the results screen show a full recap,
    not just the final numbers.
    """

    run = models.ForeignKey(SimulationRun, on_delete=models.CASCADE, related_name="decisions")
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    made_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Run {self.run_id}: {self.choice.label}"
