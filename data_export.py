"""
FinCoach — SQL data export.

Pulls together every piece of user data currently scattered across the
app's separate JSON stores --

    users.json, profile_data.json, tracker_data.json,
    course_progress.json, sim_data.json, activity_log.json, help_data.json

-- into ONE structured SQLite database, organized into real tables and
columns (username, email, age, amount, etc.) instead of separate JSON
blobs. This is a full rebuild every time it runs, not incremental, so
it always reflects exactly what's currently in the JSON files -- safe
to re-run any time.

Two ways to use this:

1. As a script -- running it directly rebuilds fincoach.db and also
   writes out a plain-text fincoach_export.sql file (full CREATE TABLE +
   INSERT statements, real SQL you can read, hand off, or import into
   any other SQL tool) right next to it:

       python data_export.py

2. As a module, from anywhere else in the app:

       from data_export import build_database, export_sql_file
       build_database()       # just refresh fincoach.db
       export_sql_file()      # refresh fincoach.db AND write the .sql file

Tables created:
    users                   username, email, password
    profiles                username, display_name, bio, email, age, photo_path
    feedback                per-user 1-5 star app ratings + comments
    course_points           username, total quiz points
    course_quiz_results     one row per lesson quiz attempt saved
    transactions            Finance Tracker income/expense entries
    goals                   Finance Tracker savings goals
    simulation_progress     Life Simulation running cash/savings/debt/score
    activity_log            the full action-by-action audit trail
    help_questions          community Q&A
    help_contact_messages   Contact Us submissions
"""
import json
import os
import sqlite3

APP_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(APP_DIR, "users.json")
PROFILE_FILE = os.path.join(APP_DIR, "profile_data.json")
TRACKER_FILE = os.path.join(APP_DIR, "tracker_data.json")
COURSE_PROGRESS_FILE = os.path.join(APP_DIR, "course_progress.json")
SIM_FILE = os.path.join(APP_DIR, "sim_data.json")
ACTIVITY_FILE = os.path.join(APP_DIR, "activity_log.json")
HELP_FILE = os.path.join(APP_DIR, "help_data.json")

DB_PATH = os.path.join(APP_DIR, "fincoach.db")
SQL_EXPORT_PATH = os.path.join(APP_DIR, "fincoach_export.sql")


SCHEMA_SQL = """
CREATE TABLE users (
    username        TEXT PRIMARY KEY,
    email           TEXT,
    password        TEXT
);

CREATE TABLE profiles (
    username        TEXT PRIMARY KEY REFERENCES users(username),
    display_name    TEXT,
    bio             TEXT,
    email           TEXT,
    age             INTEGER,
    photo_path      TEXT
);

CREATE TABLE feedback (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT REFERENCES users(username),
    rating          INTEGER,
    comment         TEXT
);

CREATE TABLE course_points (
    username        TEXT PRIMARY KEY REFERENCES users(username),
    points          INTEGER
);

CREATE TABLE course_quiz_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT REFERENCES users(username),
    unit            INTEGER,
    lesson          TEXT,
    correct         INTEGER,
    total           INTEGER
);

CREATE TABLE transactions (
    id              INTEGER,
    username        TEXT REFERENCES users(username),
    date            TEXT,
    type            TEXT,
    category        TEXT,
    amount          REAL,
    note            TEXT,
    PRIMARY KEY (username, id)
);

CREATE TABLE goals (
    id              INTEGER,
    username        TEXT REFERENCES users(username),
    name            TEXT,
    target          REAL,
    saved           REAL,
    PRIMARY KEY (username, id)
);

CREATE TABLE simulation_progress (
    username            TEXT PRIMARY KEY REFERENCES users(username),
    stage_index         INTEGER,
    cash                REAL,
    savings             REAL,
    debt                REAL,
    score               REAL,
    last_outcome        TEXT,
    awaiting_continue   INTEGER,
    completed           INTEGER
);

CREATE TABLE activity_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT,
    username        TEXT,
    action          TEXT,
    details         TEXT
);

CREATE TABLE help_questions (
    id              INTEGER PRIMARY KEY,
    question        TEXT,
    answer          TEXT,
    asker           TEXT,
    date            TEXT
);

CREATE TABLE help_contact_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT,
    name            TEXT,
    email           TEXT,
    message         TEXT,
    date            TEXT
);
"""


def _load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default


def build_database(db_path=DB_PATH):
    """Rebuild fincoach.db from scratch using whatever is currently in
    the JSON files. Always a full, fresh rebuild -- never incremental --
    so it's safe to call any time and it'll never drift out of sync."""
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)

    users = _load_json(USERS_FILE, {})
    profiles = _load_json(PROFILE_FILE, {})
    tracker = _load_json(TRACKER_FILE, {})
    course = _load_json(COURSE_PROGRESS_FILE, {})
    sim = _load_json(SIM_FILE, {})
    activity = _load_json(ACTIVITY_FILE, [])
    help_data = _load_json(HELP_FILE, {"questions": [], "contact_messages": []})

    # ---- users ----
    for username, u in users.items():
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, u.get("email"), u.get("password")),
        )

    # ---- profiles + feedback (name, age, bio, etc. live here) ----
    for username, p in profiles.items():
        cur.execute(
            "INSERT OR IGNORE INTO profiles "
            "(username, display_name, bio, email, age, photo_path) VALUES (?, ?, ?, ?, ?, ?)",
            (username, p.get("display_name"), p.get("bio"), p.get("email"),
             p.get("age"), p.get("photo_path")),
        )
        for fb in p.get("feedback", []):
            cur.execute(
                "INSERT INTO feedback (username, rating, comment) VALUES (?, ?, ?)",
                (username, fb.get("rating"), fb.get("comment")),
            )

    # ---- course progress ----
    for username, c in course.items():
        cur.execute(
            "INSERT OR IGNORE INTO course_points (username, points) VALUES (?, ?)",
            (username, c.get("points", 0)),
        )
        for q in c.get("quizzes", {}).values():
            cur.execute(
                "INSERT INTO course_quiz_results (username, unit, lesson, correct, total) "
                "VALUES (?, ?, ?, ?, ?)",
                (username, q.get("unit"), q.get("lesson"), q.get("correct"), q.get("total")),
            )

    # ---- finance tracker ----
    for username, t in tracker.items():
        for txn in t.get("transactions", []):
            cur.execute(
                "INSERT OR IGNORE INTO transactions (id, username, date, type, category, amount, note) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (txn.get("id"), username, txn.get("date"), txn.get("type"),
                 txn.get("category"), txn.get("amount"), txn.get("note")),
            )
        for g in t.get("goals", []):
            cur.execute(
                "INSERT OR IGNORE INTO goals (id, username, name, target, saved) VALUES (?, ?, ?, ?, ?)",
                (g.get("id"), username, g.get("name"), g.get("target"), g.get("saved")),
            )

    # ---- life simulation ----
    for username, s in sim.items():
        cur.execute(
            "INSERT OR IGNORE INTO simulation_progress "
            "(username, stage_index, cash, savings, debt, score, last_outcome, "
            "awaiting_continue, completed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (username, s.get("stage_index"), s.get("cash"), s.get("savings"), s.get("debt"),
             s.get("score"), s.get("last_outcome"), int(bool(s.get("awaiting_continue"))),
             int(bool(s.get("completed")))),
        )

    # ---- activity log (the full audit trail) ----
    for entry in activity:
        cur.execute(
            "INSERT INTO activity_log (timestamp, username, action, details) VALUES (?, ?, ?, ?)",
            (entry.get("timestamp"), entry.get("user"), entry.get("action"),
             json.dumps(entry.get("details", {}))),
        )

    # ---- help: community questions + contact messages ----
    for q in help_data.get("questions", []):
        cur.execute(
            "INSERT OR IGNORE INTO help_questions (id, question, answer, asker, date) "
            "VALUES (?, ?, ?, ?, ?)",
            (q.get("id"), q.get("question"), q.get("answer"), q.get("asker"), q.get("date")),
        )
    for m in help_data.get("contact_messages", []):
        cur.execute(
            "INSERT INTO help_contact_messages (username, name, email, message, date) "
            "VALUES (?, ?, ?, ?, ?)",
            (m.get("user"), m.get("name"), m.get("email"), m.get("message"), m.get("date")),
        )

    conn.commit()
    conn.close()
    return db_path


def export_sql_file(sql_path=SQL_EXPORT_PATH, db_path=DB_PATH):
    """Build the database, then dump it as one plain-text .sql file --
    real CREATE TABLE + INSERT statements for every row -- so the data
    can be handed off, version-controlled, or imported into any other
    SQL tool without needing the .db file itself."""
    build_database(db_path)
    conn = sqlite3.connect(db_path)
    with open(sql_path, "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    conn.close()
    return sql_path


if __name__ == "__main__":
    path = export_sql_file()
    print(f"Wrote {DB_PATH}")
    print(f"Wrote {path}")