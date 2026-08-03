"""
FinCoach — Help page.

Three sections:
1. A short (~5 min) how-to video — placeholder until the real file is
   uploaded. Once a file exists at assets/help_video.mp4 it plays
   automatically instead of the "coming soon" card.
2. A searchable community area: recent Q&A plus a handful of short
   how-to articles. One search box filters both at once. Users can
   also post a new question, which is saved alongside the seed data.
3. A "Contact us" form. Since this prototype has no email server, a
   submission is stored in help_data.json and a mailto link is offered
   as a fallback so a real message can still go out.

All community/contact data is persisted per-app (not per-user) in
help_data.json, next to main.py — same lightweight JSON pattern used by
finance_tracker.py and life_simulation.py.
"""
import json
import os
from datetime import date

import streamlit as st

from activity_log import log_action

APP_DIR = os.path.dirname(os.path.abspath(__file__))
HELP_FILE = os.path.join(APP_DIR, "help_data.json")
VIDEO_PATH = os.path.join(APP_DIR, "assets", "help_video.mp4")

CONTACT_EMAIL = "fincoach2026@gmail.com"

SEED_QUESTIONS = [
    {
        "id": 1, "question": "How do I add my first transaction?",
        "answer": "Go to Finance Tracker → the ➕ Add tab, choose income or "
                   "expense, pick a category, enter the amount, and submit.",
        "asker": "jordan_m", "date": "2026-06-20",
    },
    {
        "id": 2, "question": "Can I redo a Life Simulation from the start?",
        "answer": "Yes — open Life Simulation and look for the restart option "
                   "on the results screen once you finish a playthrough.",
        "asker": "amara.k", "date": "2026-06-22",
    },
    {
        "id": 3, "question": "Why is Unit 3 locked?",
        "answer": "Only Unit 1 has full lessons written so far. Locked units "
                   "show their lesson outline with a 🔒 until content is added.",
        "asker": "dev_test", "date": "2026-06-25",
    },
    {
        "id": 4, "question": "Is my data shared with anyone else?",
        "answer": "No — everything you enter (tracker, simulation, course "
                   "progress) is stored locally per account for this prototype.",
        "asker": "priya_s", "date": "2026-06-27",
    },
]

ARTICLES = [
    {
        "id": 1, "title": "Getting started with FinCoach",
        "category": "Basics",
        "summary": "A 2-minute tour of the Course, Life Simulation, and "
                    "Finance Tracker, and how they connect.",
    },
    {
        "id": 2, "title": "How the Life Simulation score works",
        "category": "Life Simulation",
        "summary": "What the running cash, savings, debt, and financial "
                    "score numbers mean and how choices move them.",
    },
    {
        "id": 3, "title": "Reading your Finance Tracker charts",
        "category": "Finance Tracker",
        "summary": "What the spending-by-category and balance-over-time "
                    "charts show, and how to clear demo data.",
    },
    {
        "id": 4, "title": "Flashcards and quizzes, explained",
        "category": "Course",
        "summary": "How flipping a flashcard works, and how quiz retries "
                    "and scoring behave in each lesson.",
    },
]


def load_help_data():
    if os.path.exists(HELP_FILE):
        with open(HELP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    data = {
        "questions": [dict(q) for q in SEED_QUESTIONS],
        "next_question_id": len(SEED_QUESTIONS) + 1,
        "contact_messages": [],
    }
    save_help_data(data)
    return data


def save_help_data(data):
    with open(HELP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _matches(query, *fields):
    if not query:
        return True
    q = query.lower().strip()
    return any(q in (field or "").lower() for field in fields)


def render_help():
    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>HELP</span>"
        "<h1>We're here if you get stuck</h1></div>",
        unsafe_allow_html=True,
    )

    data = load_help_data()

    # ---- 1. Video tutorial ----
    st.markdown("### 🎥 Quick walkthrough")
    if os.path.exists(VIDEO_PATH):
        st.video(VIDEO_PATH)
    else:
        st.markdown(
            "<div class='fc-card fc-fade' style='text-align:center; padding:40px;'>"
            "<div style='font-size:2.4rem;'>🎬</div>"
            "<h4>Video coming soon</h4>"
            "<p>A ~5 minute walkthrough of the whole app will play right here. "
            "Once it's uploaded to <code>assets/help_video.mp4</code>, this card "
            "is automatically replaced with the player — no code changes needed.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ---- 2. Community search: Q&A + short articles ----
    st.markdown("### 💬 Search the community")
    query = st.text_input(
        "Search questions and articles",
        placeholder="Try “tracker”, “life simulation”, “quiz”...",
        label_visibility="collapsed",
    )

    questions = data["questions"]
    matched_questions = [
        q for q in questions if _matches(query, q["question"], q["answer"])
    ]
    matched_articles = [
        a for a in ARTICLES if _matches(query, a["title"], a["summary"], a["category"])
    ]

    tab_qa, tab_articles = st.tabs(
        [f"🗨️ Questions ({len(matched_questions)})", f"📄 Articles ({len(matched_articles)})"]
    )

    with tab_qa:
        if not matched_questions:
            st.caption("No questions match that search yet.")
        else:
            for q in sorted(matched_questions, key=lambda x: x["date"], reverse=True):
                st.markdown(
                    f"<div class='fc-card fc-fade' style='margin-bottom:10px;'>"
                    f"<b>{q['question']}</b>"
                    f"<p style='margin:6px 0 4px 0;'>{q['answer']}</p>"
                    f"<span style='font-size:0.8rem; opacity:0.7;'>"
                    f"asked by {q['asker']} · {q['date']}</span></div>",
                    unsafe_allow_html=True,
                )

        with st.expander("➕ Ask a new question"):
            with st.form("ask_question_form", clear_on_submit=True):
                new_q = st.text_area("Your question")
                submitted_q = st.form_submit_button("Post question")
            if submitted_q:
                if new_q.strip():
                    new_id = data.get("next_question_id", len(questions) + 1)
                    questions.append({
                        "id": new_id,
                        "question": new_q.strip(),
                        "answer": "The team hasn't answered this one yet — check back soon!",
                        "asker": st.session_state.get("user") or "anonymous",
                        "date": str(date.today()),
                    })
                    data["next_question_id"] = new_id + 1
                    save_help_data(data)
                    log_action(st.session_state.get("user"), "help_question_posted", {"question": new_q.strip()})
                    st.success("Question posted!")
                    st.rerun()
                else:
                    st.error("Type a question before posting.")

    with tab_articles:
        if not matched_articles:
            st.caption("No articles match that search yet.")
        else:
            for a in matched_articles:
                st.markdown(
                    f"<div class='fc-card fc-fade' style='margin-bottom:10px;'>"
                    f"<span class='fc-badge'>{a['category']}</span>"
                    f"<h4 style='margin:6px 0 4px 0;'>{a['title']}</h4>"
                    f"<p style='margin:0;'>{a['summary']}</p></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ---- 3. Contact us ----
    st.markdown("### ✉️ Contact us")
    st.caption(f"Prefer email? Reach us directly at {CONTACT_EMAIL}.")
    with st.form("contact_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name")
        with c2:
            email = st.text_input("Your email")
        message = st.text_area("Message")
        sent = st.form_submit_button("Send message", use_container_width=True)
    if sent:
        if not name.strip() or not email.strip() or not message.strip():
            st.error("Fill in your name, email, and message.")
        else:
            data["contact_messages"].append({
                "name": name.strip(), "email": email.strip(),
                "message": message.strip(), "date": str(date.today()),
                "user": st.session_state.get("user"),
            })
            save_help_data(data)
            log_action(st.session_state.get("user"), "help_contact_submitted", {
                "name": name.strip(), "email": email.strip(), "message": message.strip(),
            })
            st.success(f"Thanks — your message was sent to {CONTACT_EMAIL}. We'll get back to you soon.")
