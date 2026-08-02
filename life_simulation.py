"""
FinCoach — Life Simulation page.

This module is intentionally minimal and only serves as a placeholder for the
HTML-based simulator page.
"""
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).resolve().parent
SIMULATOR_HTML = APP_DIR / "life_simulator_realistic.html"


def render_life_sim():
    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>LIFE SIMULATION</span>"
        "<h1>Interactive Financial Life Simulator</h1>"
        "<p>Open the embedded world below to explore the simulator.</p></div>",
        unsafe_allow_html=True,
    )

    html = SIMULATOR_HTML.read_text(encoding="utf-8")
    components.html(html, height=950, scrolling=False)
