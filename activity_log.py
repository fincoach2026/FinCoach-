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
    """
    Save activity locally and mirror it to Google Sheets.
    Logging should never interrupt the app if something fails.
    """
    try:
        details = details or {}

        entries = _load()

        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": username,
            "action": action,
            "details": details,
        }

        entries.append(entry)
        _save(entries)

        google_data = {
            "username": username,
            "action": action,
        }

        google_data.update(details)

        log_event(google_data)

    except Exception:
        # Never let logging crash the app
        pass


def get_user_activity(username, limit=50):
    """Most recent activity for one user, newest first."""
    entries = [e for e in _load() if e.get("user") == username]
    return list(reversed(entries))[:limit]


def get_all_activity(limit=200):
    """Most recent activity across all users, newest first."""
    return list(reversed(_load()))[:limit]
