"""
FinCoach — central user activity log.

Every meaningful thing a user does anywhere in the app — signing up,
logging in/out, answering a quiz, adding a transaction or goal, making a
Life Simulation choice, updating a profile, submitting feedback or a help
question — gets appended here as one JSON record. This is a flat audit
trail (not used to drive any UI): the single place every user action and
every piece of data a user enters shows up, in one file, in one format.

Stored in activity_log.json, next to main.py.
"""
import json
import os
from datetime import datetime
from google_sheets import log_event

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVITY_FILE = os.path.join(APP_DIR, "activity_log.json")


def _load():
    if os.path.exists(ACTIVITY_FILE):
        with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def _save(entries):
    with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, default=str)


def log_action(username, action, details=None):
    _save(entries)
    entries.append(...)

    _save(entries)

    google_row = {
        "username": username,
        "action": action,
    }

    google_row.update(details or {})

    log_event(google_row)
    except Exception:
        pass


def get_user_activity(username, limit=50):
    """Most recent activity for one user, newest first."""
    entries = [e for e in _load() if e.get("user") == username]
    return list(reversed(entries))[:limit]


def get_all_activity(limit=200):
    """Most recent activity across all users, newest first."""
    return list(reversed(_load()))[:limit]
