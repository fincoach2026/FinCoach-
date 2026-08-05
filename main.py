"""
FinCoach — Streamlit app
Feature set: Landing experience, Login/Signup, Finance Literacy Course,
Life Simulation, Finance Tracker, Help, Profile.
Run locally with:  streamlit run main.py
"""
import email
import json
from google_sheets import log_event
import os
import time
from pathlib import Path
import bcrypt


import streamlit as st
import streamlit.components.v1 as components

from styles import get_css
from assets_logo import LOGO_B64, LOGO_BYTES
from course_data import COURSE_UNITS, UNIT_CONTENT, get_unit_progress
from course_progress import (
    POINTS_PER_CORRECT, get_lesson_result, record_quiz_result,
)
from finance_tracker import render_tracker
from finny import render_finny_page
from help import render_help
from profile_page import render_profile
from dashboard import render_dashboard
from activity_log import log_action

APP_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(APP_DIR, "users.json")

# NOTE: the logo itself is now embedded directly in assets_logo.py (base64)
# so it always renders regardless of whether this path exists on disk.
SIMULATOR_HTML = Path(APP_DIR) / "life_simulator_realistic.html"

# ---------------------------------------------------------------------------
# Session state defaults.
# NOTE ON THE SIDEBAR: there's no supported Streamlit API to
# programmatically open/close the sidebar after the app's initial load
# (see https://github.com/streamlit/streamlit/issues/4483) -- an
# earlier version of this file tried to fake it with a session_state
# flag driving initial_sidebar_state on every rerun, but that value is
# only honored on first load, so the ☰ button worked inconsistently.
# The fix (see the ☰ button in top_bar() below) is to have our button
# click Streamlit's OWN real collapse/expand control via a tiny bit of
# injected JS, instead of trying to recreate that toggle ourselves.
# ---------------------------------------------------------------------------
defaults = {
    "page": "welcome",
    "dark_mode": False,
    "user": None,
    "auth_mode": "login",
    "selected_unit": 1,
    "selected_lesson": None,
    "flip_states": {},
    "quiz_answers": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.set_page_config(
    page_title="FinCoach", page_icon="💰", layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tiny local "database" so signup/login actually persists between runs.
# Not real security — fine for a student project prototype.
# ---------------------------------------------------------------------------
def render_life_sim():
    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>LIFE SIMULATION</span>"
        "<h1>Interactive Financial Life Simulator</h1>"
        "<p>Use the world below to explore the simulator directly.</p></div>",
        unsafe_allow_html=True,
    )

    html = SIMULATOR_HTML.read_text(encoding="utf-8")
    components.html(html, height=950, scrolling=False)


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)


def goto(page):
    st.session_state.page = page
    st.rerun()


# ---------------------------------------------------------------------------
# Shared chrome: top bar with logo, dark-mode icon, language picker, profile
# icon, and a ☰ button that opens a real Streamlit sidebar for navigation.
# The sidebar is a genuine left-hand panel (not custom-built HTML), so it
# slides in over the page the same way Streamlit's own sidebar always does
# — clicking ☰ expands it, clicking it again (or the built-in » arrow)
# collapses it back.
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("🏠 Dashboard", "dashboard"),
    ("📚 Finance Literacy Course", "course"),
    ("🎮 Life Simulation", "life_sim"),
    ("🤖 Finny — AI Helper", "finny"),
    ("📊 Finance Tracker", "tracker"),
    ("❓ Help", "help"),
]


def render_sidebar():
    with st.sidebar:
        st.image(LOGO_BYTES, width=120)
        st.markdown("#### Menu")
        for label, target in NAV_ITEMS:
            disabled = st.session_state.page == target
            if st.button(label, key=f"sidebar_nav_{target}", use_container_width=True, disabled=disabled):
                goto(target)
        st.markdown("<hr style='border-color:var(--fc-card-border);'>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", key="sidebar_logout_btn", use_container_width=True):
            log_action(st.session_state.user, "logout")
            st.session_state.user = None
            goto("welcome")


# Clicking our ☰ triggers Streamlit's OWN native sidebar collapse/expand
# control via a little injected JS, rather than trying to recreate that
# toggle ourselves (there's no supported Python API for it -- see the
# NOTE above the session-state defaults at the top of this file). This
# fires only on the single rerun where the button was actually clicked
# (see the `if st.button(...)` below), not on every rerun, so it won't
# fight with the user manually using Streamlit's own arrow either --
# it IS that same arrow, just clicked programmatically.
#
# NOTE ON REPEAT CLICKS: components.html() renders an iframe whose
# content Streamlit only reloads when that content actually changes.
# Since this script was byte-for-byte identical on every click, the
# browser reused the very first iframe and never re-ran the script
# after the first toggle -- so ☰ opened the sidebar once but couldn't
# close it again. A tiny per-click nonce (an HTML comment, invisible
# and inert) makes each injection unique so the iframe -- and the
# script inside it -- is genuinely recreated every time, letting ☰
# open AND close the sidebar over and over.
_SIDEBAR_TOGGLE_JS = """
<script>
(function() {
    const doc = window.parent.document;
    const selectors = [
        '[data-testid="stSidebarCollapseButton"] button',
        '[data-testid="stSidebarCollapsedControl"] button',
        '[data-testid="collapsedControl"] button',
    ];
    for (const sel of selectors) {
        const btn = doc.querySelector(sel);
        if (btn) { btn.click(); break; }
    }
})();
</script>
<!-- nonce: __NONCE__ -->
"""


def top_bar(show_nav=True, show_menu=False):
    if show_menu and st.session_state.user:
        render_sidebar()

    col_brand, col_icons = st.columns([6, 3])

    with col_brand:
        welcome_html = ""
        if show_nav and st.session_state.user:
            from profile_page import get_profile
            display_name = get_profile(st.session_state.user).get("display_name") or st.session_state.user
            welcome_html = (
                f"<span class='fc-welcome-text fc-fade'>Welcome back, "
                f"<b>{display_name}</b> 👋</span>"
            )
        st.markdown(
            f"<div class='fc-topbar-brand'>"
            f"<img src='data:image/png;base64,{LOGO_B64}' class='fc-topbar-logo'/>"
            f"{welcome_html}</div>",
            unsafe_allow_html=True,
        )

    with col_icons:
        n_icons = 2 + (1 if show_menu else 0)
        icon_cols = st.columns(n_icons)
        i = 0

        # Dark mode: single icon that flips between moon (go dark) and sun (go light)
        # NOTE: st.container(key=...) is used (not two separate st.markdown calls)
        # because Streamlit renders each st.markdown as its own sibling element —
        # an opening "<div>" in one st.markdown and a closing "</div>" in another
        # never actually wraps the widget rendered in between. st.container(key=...)
        # is a real DOM container (class "st-key-<key>") that genuinely wraps its
        # children, which is what lets the .fc-icon-btn CSS below actually apply.
        with icon_cols[i]:
            with st.container(key="fc_icon_dark"):
                icon = "☀️" if st.session_state.dark_mode else "🌙"
                if st.button(icon, key="dark_toggle_btn"):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()
        i += 1

        # Profile icon — only once logged in
        with icon_cols[i]:
            with st.container(key="fc_icon_profile"):
                if st.session_state.user:
                    if st.button("👤", key="profile_btn", disabled=(st.session_state.page == "profile")):
                        goto("profile")
        i += 1

        # ☰ clicks Streamlit's own real sidebar arrow for us (see
        # _SIDEBAR_TOGGLE_JS above) instead of faking the toggle.
        if show_menu:
            with icon_cols[i]:
                with st.container(key="fc_icon_menu"):
                    if st.button("☰", key="hamburger_btn"):
                        st.session_state.hamburger_clicks = st.session_state.get("hamburger_clicks", 0) + 1
                        toggle_js = _SIDEBAR_TOGGLE_JS.replace(
                            "__NONCE__", str(st.session_state.hamburger_clicks)
                        )
                        components.html(toggle_js, height=0)

    st.markdown("<hr style='border-color: var(--fc-card-border); margin-top:0;'>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# STEP 1 — Welcome / loading screen
# ---------------------------------------------------------------------------
def render_welcome():
    st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
    col = st.columns([1, 2, 1])[1]
    with col:
        with st.container(key="fc_logo_pulse"):
            st.image(LOGO_BYTES, width=260)
        st.markdown(
            "<h2 class='fc-fade fc-fade-delay-1 fc-typing' "
            "style='text-align:center; color:var(--fc-accent);'>Welcome to FinCoach</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='fc-fade fc-fade-delay-2' style='text-align:center;'>"
            "Your guide to financial confidence, one decision at a time.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='fc-fade fc-fade-delay-3'>", unsafe_allow_html=True)
        st.progress(100)
        if st.button("Get Started →", use_container_width=True):
            goto("mission")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# STEP 2 — Mission page
# ---------------------------------------------------------------------------
def render_mission():
    top_bar(show_nav=False)
    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(
            "<div class='fc-fade'>"
            "<span class='fc-badge'>OUR MISSION</span>"
            "<h1>Helping young adults build a financial life they're proud of.</h1>"
            "<p style='font-size:1.05rem;'>FinCoach helps young adults balance their "
            "financial lifestyle and avoid costly mistakes — through lessons, an "
            "interactive life simulator, and games that make financial literacy feel "
            "like something you actually want to engage with, not a chore.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='fc-fade fc-fade-delay-2'>", unsafe_allow_html=True)
        if st.button("Continue →"):
            goto("why_us")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='fc-fade fc-fade-delay-1 fc-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("### 🌱")
        st.markdown("Financial confidence, one small decision at a time.")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# STEP 3 — Why Us (4 cards)
# ---------------------------------------------------------------------------
WHY_US_CARDS = [
    ("🎮", "Learn by living it", "An interactive life simulation turns real financial decisions into a story, not a worksheet."),
    ("🤖", "An AI helper in your corner", "Ask about any real purchase or decision and get a clear verdict, budget impact, and alternatives."),
    ("📚", "A real curriculum", "20 units and 83 lessons covering everything from budgeting to retirement, built for real life."),
    ("📊", "See the whole picture", "A finance tracker dashboard keeps net worth, spending, and goals all in one place."),
]


def render_why_us():
    top_bar(show_nav=False)
    st.markdown(
        "<div class='fc-fade' style='text-align:center; margin-bottom:20px;'>"
        "<span class='fc-badge'>WHY FINCOACH</span>"
        "<h1>Four reasons students choose FinCoach</h1></div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(WHY_US_CARDS):
        with cols[i]:
            st.markdown(
                f"<div class='fc-card fc-fade fc-fade-delay-{min(i, 3)}' style='min-height:220px;'>"
                f"<div style='font-size:2rem;'>{icon}</div>"
                f"<h4>{title}</h4><p style='font-size:0.9rem;'>{desc}</p></div>",
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    col = st.columns([2, 1, 2])[1]
    with col:
        if st.button("Continue to Sign Up →", use_container_width=True):
            goto("auth")


# ---------------------------------------------------------------------------
# STEP 4 — Login / Signup (split layout)
# ---------------------------------------------------------------------------
def render_auth():
    top_bar(show_nav=False)

    with st.container(key="fc_auth_page"):
        left, right = st.columns([1, 1])

        with left:
            st.markdown(
                "<div class='fc-fade fc-card' style='height:100%; "
                "background:linear-gradient(135deg, var(--fc-primary), var(--fc-secondary)); color:white;'>"
                "<h2 style='color:white;'>Start building your financial future today.</h2>"
                "<p style='color:white;'>Join FinCoach and turn financial literacy into something you actually "
                "look forward to.</p></div>",
                unsafe_allow_html=True,
            )

        with right:
            st.markdown("<div class='fc-fade fc-fade-delay-1'>", unsafe_allow_html=True)

            tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

            with tab_login:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Log In", use_container_width=True)

                if submitted:
                    users = load_users()

                    stored_hash = users[username]["password"]

                    if bcrypt.checkpw(
                        password.encode("utf-8"),
                        stored_hash.encode("utf-8")
                    ):
                        st.session_state.user = username

                        # Google Sheets logging
                        log_event({
                            "username": username,
                            "action": "Login",
                            "status": "Success"
                        })

                        log_action(username, "login")
                        goto("dashboard")

                    else:
                        st.error("Incorrect username or password.")

            with tab_signup:
                with st.form("signup_form"):
                    new_username = st.text_input("Choose a username")
                    new_email = st.text_input("Email")
                    new_password = st.text_input("Choose a password", type="password")
                    submitted_su = st.form_submit_button(
                        "Create Account",
                        use_container_width=True
                    )

                if submitted_su:
                    users = load_users()

                    if not new_username or not new_password:
                        st.error("Username and password are required.")

                    elif new_username in users:
                        st.error("That username is already taken.")

                    else:
                        hashed_password = bcrypt.hashpw(
                            new_password.encode("utf-8"),
                            bcrypt.gensalt()
                        ).decode("utf-8")

                        users[new_username] = {
                            "password": hashed_password,
                            "email": new_email
                        }

                        save_users(users)

                        # Google Sheets logging
                        log_event({
                            "username": new_username,
                            "email": new_email,
                            "action": "Signup",
                            "status": "Success"
                        })

                        st.session_state.user = new_username

                        log_action(
                            new_username,
                            "signup",
                            {"email": new_email}
                        )

                        st.success("Account created! Taking you in...")
                        time.sleep(0.6)
                        goto("dashboard")

            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Finance Literacy Course
# ---------------------------------------------------------------------------
def render_course():
    top_bar(show_nav=True, show_menu=True)

    unit_labels = []
    for u in COURSE_UNITS:
        label = f"Unit {u['num']}: {u['title']}"
        if get_unit_progress(u["num"]) == "coming_soon":
            label += " 🔒"
        unit_labels.append(label)

    current_index = st.session_state.selected_unit - 1
    chosen_label = st.selectbox(
        "📚 Choose a unit", unit_labels, index=current_index, key="unit_select",
    )
    chosen_num = int(chosen_label.split(":")[0].replace("Unit", "").strip())
    if chosen_num != st.session_state.selected_unit:
        st.session_state.selected_unit = chosen_num
        st.session_state.selected_lesson = None
        st.rerun()

    unit = next(u for u in COURSE_UNITS if u["num"] == st.session_state.selected_unit)
    st.markdown(f"<div class='fc-fade'><span class='fc-badge'>UNIT {unit['num']}</span>"
                f"<h1>{unit['title']}</h1></div>", unsafe_allow_html=True)

    if get_unit_progress(unit["num"]) == "coming_soon":
        st.markdown(
            "<div class='fc-card fc-fade'>"
            "<h4>📝 Content coming soon</h4>"
            "<p>This unit's lessons are outlined below — full articles, flashcards, "
            "and quizzes for this unit are still being written.</p></div>",
            unsafe_allow_html=True,
        )
        for lesson in unit["lessons"]:
            st.markdown(f"- {lesson}")
        return

    lesson_titles = list(UNIT_CONTENT[unit["num"]].keys())
    if st.session_state.selected_lesson not in lesson_titles:
        st.session_state.selected_lesson = lesson_titles[0]

    selected_lesson = st.radio(
        "Choose a lesson", lesson_titles,
        index=lesson_titles.index(st.session_state.selected_lesson),
        horizontal=False,
    )
    st.session_state.selected_lesson = selected_lesson
    lesson = UNIT_CONTENT[unit["num"]][selected_lesson]

    tab_article, tab_flash, tab_video, tab_quiz = st.tabs(
        ["📖 Article", "🗂️ Flashcards", "🎥 Video Tutorials", "❓ Quiz"]
    )

    # ---- Article ----
    with tab_article:
        art = lesson["article"]
        st.markdown(f"<div class='fc-fade'><h3>{art['part1_title']}</h3></div>", unsafe_allow_html=True)
        st.markdown(art["part1_body"])
        st.markdown(f"<div class='fc-fade'><h3>{art['part2_title']}</h3></div>", unsafe_allow_html=True)
        st.markdown(art["part2_body"])

    # ---- Flashcards ----
    with tab_flash:
        st.caption("Click a card to flip it.")
        cards = lesson["flashcards"]
        cols = st.columns(2)
        for i, card in enumerate(cards):
            key = f"{unit['num']}_{selected_lesson}_{i}"
            flipped = st.session_state.flip_states.get(key, False)
            with cols[i % 2]:
                cls = "fc-flip-container flipped" if flipped else "fc-flip-container"
                st.markdown(
                    f"<div class='{cls}'><div class='fc-flip-inner'>"
                    f"<div class='fc-flip-front'>{card['front']}</div>"
                    f"<div class='fc-flip-back'>{card['back']}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
                if st.button("Flip", key=f"flip_btn_{key}", use_container_width=True):
                    st.session_state.flip_states[key] = not flipped
                    st.rerun()

    # ---- Video tutorials ----
    with tab_video:
        video_urls = lesson.get("video_urls", [])
        if video_urls:
            for v_url in video_urls:
                st.video(v_url)
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div class='fc-fade fc-card'>"
                "<p>Video tutorials will be linked here for this lesson once "
                "the team finalizes them. This tab is wired up and ready to hold "
                "real links.</p></div>",
                unsafe_allow_html=True,
            )

    # ---- Quiz ----
    with tab_quiz:
        quiz = lesson["quiz"]
        username = st.session_state.user
        unit_num = unit["num"]

        prev_result = get_lesson_result(username, unit_num, selected_lesson)
        if prev_result:
            st.markdown(
                f"<div class='fc-card fc-fade'>✅ Best saved score: "
                f"<b>{prev_result['correct']}/{prev_result['total']}</b> correct — "
                f"<b>{prev_result['correct'] * POINTS_PER_CORRECT} points</b> earned from this quiz. "
                f"You can retake it any time to try to improve your score.</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        quiz_key_prefix = f"{unit_num}_{selected_lesson}"
        with st.form(f"quiz_form_{quiz_key_prefix}"):
            selections = {}
            for qi, q in enumerate(quiz):
                st.markdown(f"**{qi + 1}. {q['question']}**")
                selections[qi] = st.radio(
                    "Select one:", q["options"],
                    key=f"quiz_{quiz_key_prefix}_{qi}", index=None,
                    label_visibility="collapsed",
                )
                st.markdown("---")
            submitted_quiz = st.form_submit_button("Submit Answers", use_container_width=True)

        if submitted_quiz:
            if any(v is None for v in selections.values()):
                st.error("Answer every question before submitting.")
            else:
                correct = 0
                for qi, q in enumerate(quiz):
                    chosen_index = q["options"].index(selections[qi])
                    if chosen_index == q["answer_index"]:
                        st.success(f"✅ Q{qi + 1}: Correct! {q['explanation']}")
                        correct += 1
                    else:
                        st.error(f"❌ Q{qi + 1}: Not quite. {q['explanation']}")

                earned = correct * POINTS_PER_CORRECT
                record_quiz_result(username, unit_num, selected_lesson, correct, len(quiz))
                log_action(username, "quiz_submitted", {
                    "unit": unit_num, "lesson": selected_lesson,
                    "correct": correct, "total": len(quiz), "points_earned": earned,
                })
                st.markdown(
                    f"<div class='fc-card fc-fade'><h4 style='margin-top:0;'>"
                    f"You scored {correct}/{len(quiz)} — +{earned} points 🎉</h4>"
                    f"<p style='margin-bottom:0;'>Saved to your progress — it'll still be here "
                    f"next time you log in.</p></div>",
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
page = st.session_state.page
if page == "welcome":
    render_welcome()
elif page == "mission":
    render_mission()
elif page == "why_us":
    render_why_us()
elif page == "auth":
    render_auth()
elif page == "dashboard":
    if st.session_state.user is None:
        goto("auth")
    else:
        top_bar(show_nav=True, show_menu=True)
        render_dashboard()
elif page == "course":
    if st.session_state.user is None:
        goto("auth")
    else:
        render_course()
elif page == "life_sim":
    if st.session_state.user is None:
        goto("auth")
    else:
        top_bar(show_nav=True, show_menu=True)
        render_life_sim()
elif page == "finny":
    if st.session_state.user is None:
        goto("auth")
    else:
        top_bar(show_nav=True, show_menu=True)
        render_finny_page()
elif page == "tracker":
    if st.session_state.user is None:
        goto("auth")
    else:
        top_bar(show_nav=True, show_menu=True)
        render_tracker()
elif page == "help":
    if st.session_state.user is None:
        goto("auth")
    else:
        top_bar(show_nav=True, show_menu=True)
        render_help()
elif page == "profile":
    if st.session_state.user is None:
        goto("auth")
    else:
        top_bar(show_nav=True, show_menu=True)
        render_profile()
