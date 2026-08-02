# FinCoach — Streamlit App

Built so far: **Landing experience → Login/Signup → Dashboard → Finance
Literacy Course → Life Simulation → Finance Tracker → Help → Profile.**

## Run it locally

```bash
pip install -r requirements.txt
streamlit run main.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## What's included

- **Landing flow**: welcome screen → mission → "why us" (4 cards) → login/signup, each with fade/slide-in animation.
- **Login/Signup**: split-layout auth screen with tabs. Accounts are stored in `users.json` (created automatically) — this is a simple local store for prototype purposes, not production-grade auth.
  - **Contrast, guaranteed**: the login/signup panel always renders as pure black-on-white (light mode) or white-on-black (dark mode) — never the brand green tones — so text is always legible. Buttons follow the brand: **light mode** = dark green button (`#21815F`) with white text; **dark mode** = light green button (`#9FC35C`) with black text.
  - The language picker has been removed — the app is English-only for now.
- **Dashboard** *(new landing page after login/signup)*: the first thing a user sees once they're in.
  - A circular progress ring showing **% of the full 20-unit course completed** (based on saved quiz results).
  - **Quiz points earned** (see below), shown as a big number.
  - The **top 3 most urgent items** from Finance Tracker — a negative balance, the goals furthest behind, or a category that's eating an outsized share of income — each flagged high/medium/low urgency.
  - A large **Life Simulation call-to-action** card that adapts its message depending on whether the user hasn't started, is mid-way through, or has finished.
- **Finance Literacy Course**: unit picker (dropdown, no sidebar list) covers all 20 units. Unit 1 (all 4 lessons) has full articles, flip flashcards, a **working embedded video tutorial** per lesson, and a graded quiz. Every other unit shows its lesson list with a "content coming soon" note so the structure is ready to fill in.
  - **Quizzes are submit-based**: pick an answer for every question, then hit **Submit Answers** to see results all at once (instead of grading each question the instant you click it).
  - **2 points per correct answer.** Points are saved the moment you submit and persist across logins — retaking a quiz can only raise your saved score for that lesson, never double-count points.
  - Your best score per lesson is shown at the top of the Quiz tab if you've already taken it, so progress is always visible.
- **Life Simulation**: a turn-based sequence of 9 realistic financial decision scenarios. Every choice nudges a running cash / savings / debt / financial-score total, and progress is saved per account in `sim_data.json`.
- **Finance Tracker**: a manual income/expense tracker with an Add tab, a transaction list (with delete), category and balance-over-time charts, and savings goals with progress bars. Stored per account in `tracker_data.json`.
- **Help**: a ~5 minute video slot (shows a "coming soon" card until a file is placed at `assets/help_video.mp4`, then plays automatically), a searchable community area (recent Q&A you can also post to, plus short how-to articles — one search box filters both), and a Contact Us form that saves to `help_data.json` and also lists **contact2026@gmail.com** directly.
- **Profile**: reached via the person icon in the top bar. Upload a picture, set a display name/bio/email/age, and leave a 1–5 star app rating with an optional comment. Stored per account in `profile_data.json`, photos in `assets/profile_photos/`.
- **Top bar**: logo and a large **"Welcome back, [name]"** message sit directly next to each other on the left (no longer a small line of text off to the side), and three icon buttons on the right —
  - 🌙 / ☀️ dark-mode toggle (single icon that flips depending on the current mode)
  - 👤 profile icon → Profile page
  - ☰ hamburger → opens a real left-hand Streamlit sidebar with Dashboard / Course / Life Simulation / Finance Tracker / Help / Log out. Click ☰ again (or Streamlit's own »/« arrow) to collapse it.
- **Dark mode**: uses only the brand palette (inverted tones). Body text is forced to pure black in light mode / white in dark mode across all Streamlit-native elements. The logo (`assets/logo.png`) has a transparent background, so it sits cleanly on the dark background too.
- **Activity log**: every meaningful action a user takes anywhere in the app — signup, login/logout, quiz submissions, transactions and goals added, Life Simulation choices, profile edits, feedback, help questions/contact messages — is appended as one JSON record to `activity_log.json`, with a timestamp, the username, the action name, and the data involved. This is a flat audit trail, not something shown in the UI.

## File structure

```
main.py                  # app entry point, routing, top bar
dashboard.py              # post-login landing page: progress ring, points, urgent finance cases, sim CTA
course_data.py             # course outline (20 units) + full Unit 1 content + video links
course_progress.py          # quiz results, points (2/correct), % course completion — per user
activity_log.py              # single JSON activity/action log for every user action across the app
life_simulation.py            # Life Simulation scenarios + game logic
finance_tracker.py             # Finance Tracker transactions/goals logic + urgent-case detection
help.py                          # Help page: video slot, community Q&A/articles, contact form
profile_page.py                   # Profile page: picture, bio, email, age, app rating
styles.py                          # brand CSS (colors, cards, buttons, animations, dark mode, icon buttons, dashboard, auth contrast)
assets/logo.png                     # transparent-background logo
assets/help_video.mp4                # drop the real ~5 min walkthrough here when ready (not included yet)
assets/profile_photos/                # created on first profile picture upload
users.json                             # created on first signup — local user store
sim_data.json                           # created on first Life Simulation visit — per-user progress
tracker_data.json                        # created on first Finance Tracker visit — per-user data
help_data.json                            # created on first Help visit — community Q&A + contact messages
profile_data.json                          # created on first Profile visit — per-user profile data
course_progress.json                        # created on first quiz submit — per-user quiz results + points
activity_log.json                            # created on first user action — flat log of every action across the app
```

## Notes on the video tutorial links

Unit 1's four lessons each have one real, working video link wired in (Khan Academy videos matched to
that lesson's topic) so the Video Tutorials tab is fully functional today, not a placeholder. Swap the
`video_urls` list for any lesson in `course_data.py` for your own links whenever you're ready — the tab
supports more than one video per lesson, it'll just play them in order.

## Next up

Once you've reviewed this, the next feature in the full spec is the AI Financial Helper —
happy to build that next whenever you're ready.
