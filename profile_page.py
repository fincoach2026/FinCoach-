"""
FinCoach — Profile page.

Reached from the person icon in the top bar (not the hamburger menu).
Lets a user set a profile picture, bio, email, display name, and age,
plus leave 1-5 star feedback on the app. Everything is stored per
account in profile_data.json, next to main.py.
"""
import json
import os

import streamlit as st

from activity_log import log_action

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(APP_DIR, "profile_data.json")
PHOTOS_DIR = os.path.join(APP_DIR, "assets", "profile_photos")


def load_profiles():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f)


def get_profile(username):
    profiles = load_profiles()
    if username not in profiles:
        profiles[username] = {
            "display_name": username, "bio": "", "email": "",
            "age": None, "photo_path": None, "feedback": [],
        }
        save_profiles(profiles)
    return profiles[username]


def update_profile(username, profile):
    profiles = load_profiles()
    profiles[username] = profile
    save_profiles(profiles)


def render_profile():
    username = st.session_state.user
    profile = get_profile(username)

    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>PROFILE</span>"
        f"<h1>{profile['display_name'] or username}</h1></div>",
        unsafe_allow_html=True,
    )

    col_pic, col_form = st.columns([1, 2])

    with col_pic:
        if profile.get("photo_path") and os.path.exists(profile["photo_path"]):
            st.image(profile["photo_path"], width=180)
        else:
            st.markdown(
                "<div class='fc-card' style='width:180px; height:180px; "
                "display:flex; align-items:center; justify-content:center; "
                "font-size:3.5rem;'>🙂</div>",
                unsafe_allow_html=True,
            )
        new_photo = st.file_uploader("Change picture", type=["png", "jpg", "jpeg"])
        if new_photo is not None:
            os.makedirs(PHOTOS_DIR, exist_ok=True)
            ext = os.path.splitext(new_photo.name)[1] or ".png"
            photo_path = os.path.join(PHOTOS_DIR, f"{username}{ext}")
            with open(photo_path, "wb") as f:
                f.write(new_photo.getbuffer())
            profile["photo_path"] = photo_path
            update_profile(username, profile)
            st.rerun()

    with col_form:
        with st.form("profile_form"):
            display_name = st.text_input("Display name", value=profile.get("display_name", username))
            bio = st.text_area("Bio", value=profile.get("bio", ""), placeholder="Tell us a bit about yourself...")
            email = st.text_input("Email", value=profile.get("email", ""))
            age = st.number_input(
                "Age", min_value=13, max_value=100, step=1,
                value=profile.get("age") or 18,
            )
            saved = st.form_submit_button("Save changes", use_container_width=True)
        if saved:
            profile.update({
                "display_name": display_name.strip() or username,
                "bio": bio.strip(), "email": email.strip(), "age": int(age),
            })
            update_profile(username, profile)
            log_action(username, "profile_updated", {
                "display_name": profile["display_name"], "email": profile["email"], "age": profile["age"],
            })
            st.success("Profile updated.")
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ---- Feedback: rate the app 1-5 ----
    st.markdown(
        "<div class='fc-card' style='background:var(--fc-card-bg);'>"
        "<h4>Rate FinCoach</h4>"
        "<p style='opacity:0.75; margin-top:-6px;'>Your past ratings are kept "
        "here on your profile.</p></div>",
        unsafe_allow_html=True,
    )
    if "feedback_rating" not in st.session_state:
        st.session_state.feedback_rating = 5

    st.caption("Tap a star to rate")
    star_cols = st.columns(5)
    for i in range(5):
        with star_cols[i]:
            label = "⭐" if i < st.session_state.feedback_rating else "☆"
            if st.button(label, key=f"star_{i}", use_container_width=True):
                st.session_state.feedback_rating = i + 1
                st.rerun()

    comment_key = f"feedback_comment_{st.session_state.get('feedback_comment_gen', 0)}"
    comment = st.text_input("Comment (optional)", key=comment_key)
    if st.button("Submit feedback", use_container_width=True):
        rating = st.session_state.feedback_rating
        profile["feedback"].append({"rating": rating, "comment": comment.strip()})
        update_profile(username, profile)
        log_action(username, "app_feedback_submitted", {"rating": rating, "comment": comment.strip()})
        st.session_state.feedback_comment_gen = st.session_state.get("feedback_comment_gen", 0) + 1
        st.success("Thanks for the feedback!")
        st.rerun()

    if profile["feedback"]:
        st.markdown("##### Your past ratings")
        for fb in reversed(profile["feedback"][-5:]):
            stars = "⭐" * fb["rating"] + "☆" * (5 - fb["rating"])
            line = stars if not fb["comment"] else f"{stars} — {fb['comment']}"
            st.markdown(f"<p style='margin:2px 0;'>{line}</p>", unsafe_allow_html=True)