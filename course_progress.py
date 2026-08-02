"""
FinCoach — Finance Literacy Course progress + points.

Tracks quiz results per user so progress survives logging out and back
in again. Every correct quiz answer is worth POINTS_PER_CORRECT (2)
points. Retaking a quiz can only ever raise your saved score for that
lesson (and therefore your points) — it never lets points double up
from repeat attempts of the same quiz.

Stored in course_progress.json, next to main.py.
"""
import json
import os

from course_data import COURSE_UNITS

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(APP_DIR, "course_progress.json")

POINTS_PER_CORRECT = 2

# Total lessons across the whole 20-unit curriculum (used as the
# denominator for "% of course completed" on the dashboard) — this is
# fixed by the curriculum outline, not just the units with content
# written so far, so the percentage stays accurate as more units are filled in.
TOTAL_LESSONS = sum(len(u["lessons"]) for u in COURSE_UNITS)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)


def get_user_progress(username):
    data = load_progress()
    if username not in data:
        data[username] = {"quizzes": {}, "points": 0}
        save_progress(data)
    return data[username]


def _lesson_key(unit_num, lesson_title):
    return f"{unit_num}::{lesson_title}"


def record_quiz_result(username, unit_num, lesson_title, correct, total):
    """Save a quiz attempt. Points = 2 x correct answers, summed across
    each lesson's *best* attempt so far, and persisted immediately."""
    data = load_progress()
    udata = data.setdefault(username, {"quizzes": {}, "points": 0})
    key = _lesson_key(unit_num, lesson_title)
    prev_correct = udata["quizzes"].get(key, {}).get("correct", -1)
    if correct > prev_correct:
        udata["quizzes"][key] = {
            "unit": unit_num, "lesson": lesson_title,
            "correct": correct, "total": total,
        }
    udata["points"] = sum(q["correct"] for q in udata["quizzes"].values()) * POINTS_PER_CORRECT
    save_progress(data)
    return udata


def get_total_points(username):
    return get_user_progress(username).get("points", 0)


def get_lesson_result(username, unit_num, lesson_title):
    key = _lesson_key(unit_num, lesson_title)
    return get_user_progress(username).get("quizzes", {}).get(key)


def get_completed_lesson_count(username):
    return len(get_user_progress(username).get("quizzes", {}))


def get_course_completion_pct(username):
    completed = get_completed_lesson_count(username)
    if TOTAL_LESSONS == 0:
        return 0
    return round(min(100, completed / TOTAL_LESSONS * 100))
