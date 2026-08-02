"""
FinCoach — Dashboard.

The landing page a user sees right after logging in / creating an
account. Pulls together a summary of progress across the rest of the
app so there's always a clear "where am I, what's next" view:

- Course completion — % of the full 20-unit curriculum with a saved
  (submitted) quiz result, shown as a circular progress ring.
- Quiz points earned (2 points per correct quiz answer).
- The top 3 most important/urgent items from Finance Tracker.
- A prominent call-to-action into the Life Simulation.
"""
import streamlit as st

from course_progress import get_course_completion_pct, get_total_points
from finance_tracker import get_urgent_cases

URGENCY_COLORS = {
    "high": "var(--fc-accent)",
    "medium": "var(--fc-highlight)",
    "low": "var(--fc-primary)",
}


def render_dashboard():
    username = st.session_state.user
    from profile_page import get_profile
    display_name = get_profile(username).get("display_name") or username

    st.markdown(
        f"<div class='fc-fade'><span class='fc-badge'>DASHBOARD</span>"
        f"<h1>Welcome back, {display_name} 👋</h1>"
        f"<p>Here's where things stand across your course, your finances, "
        f"and your Life Simulation.</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_course, col_points = st.columns([1, 1])

    # ---- Course completion ring ----
    with col_course:
        pct = get_course_completion_pct(username)
        st.markdown(
            f"<div class='fc-card fc-fade' style='text-align:center;'>"
            f"<h4 style='margin-top:0;'>📚 Course Progress</h4>"
            f"<div class='fc-progress-ring' style='--pct:{pct};'>"
            f"<div class='fc-progress-ring-inner'>{pct}%</div></div>"
            f"<p style='margin-bottom:0;'>of the full course completed</p></div>",
            unsafe_allow_html=True,
        )

    # ---- Quiz points ----
    with col_points:
        points = get_total_points(username)
        st.markdown(
            f"<div class='fc-card fc-fade fc-fade-delay-1' "
            f"style='text-align:center; display:flex; flex-direction:column; "
            f"justify-content:center; height:100%;'>"
            f"<h4 style='margin-top:0;'>🏆 Quiz Points</h4>"
            f"<div class='fc-points-number'>{points}</div>"
            f"<p style='margin-bottom:0;'>2 points for every quiz question you get right</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col_finance, col_cta = st.columns([1, 1])

    # ---- Top 3 urgent finance cases ----
    with col_finance:
        st.markdown("<h4>📊 Needs Your Attention</h4>", unsafe_allow_html=True)
        cases = get_urgent_cases(username)
        for c in cases:
            color = URGENCY_COLORS.get(c["level"], "var(--fc-primary)")
            st.markdown(
                f"<div class='fc-card fc-fade' style='margin-bottom:12px; "
                f"border-left: 5px solid {color};'>"
                f"<b>{c['icon']} {c['title']}</b>"
                f"<p style='margin:4px 0 0 0;'>{c['detail']}</p></div>",
                unsafe_allow_html=True,
            )
        if st.button("Open Finance Tracker →", key="dash_open_tracker", use_container_width=True):
            st.session_state.page = "tracker"
            st.rerun()

    # ---- Life Simulation CTA ----
    with col_cta:
        st.markdown("<h4>🎮 Live Simulation</h4>", unsafe_allow_html=True)
        st.markdown(
            "<div class='fc-fade fc-fade-delay-1 fc-cta-card'>"
            "<h2 style='color:white; margin-top:0;'>Ready to see your future?</h2>"
            "<p style='color:white;'>Step into the interactive world and make financial choices that shape what comes next.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Start Life Simulation →", key="dash_open_sim", use_container_width=True, type="primary"):
            st.session_state.page = "life_sim"
            st.rerun()
