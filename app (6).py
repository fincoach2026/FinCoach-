import streamlit as st
import time

# ============================================================
# PAGE SETUP
# This section sets the browser tab title/icon and makes the
# page use the full width of the screen.
# ============================================================
st.set_page_config(page_title="FinCoach - Life Simulator", page_icon="💰", layout="centered")

# ============================================================
# BRAND COLORS
# These are FinCoach's official colors. We store them in
# variables so we can reuse them anywhere in the code instead
# of retyping the hex codes every time.
# ============================================================
COLOR_MAIN_GREEN = "#4DC49B"
COLOR_DARK_GREEN = "#488C74"
COLOR_WHITE = "#FFFFFF"
COLOR_DEEP_GREEN = "#21815F"
COLOR_LIME_GREEN = "#9FC35C"
COLOR_TEXT = "#000000"

# ============================================================
# CUSTOM STYLING
# This block injects a little bit of CSS (page styling code)
# so buttons, headers, and cards match FinCoach's brand colors.
# This is the only "non-Streamlit" trick we use, and it's just
# styling, not a new library.
# ============================================================
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLOR_WHITE};
        color: {COLOR_TEXT};
    }}
    h1, h2, h3 {{
        color: {COLOR_DEEP_GREEN};
    }}
    /* Style the bordered "card" containers so each step feels
       like its own clean panel, matching our app mockups. */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 14px;
        border: 1px solid {COLOR_MAIN_GREEN} !important;
        padding: 0.5em;
    }}
    div.stButton > button {{
        background-color: {COLOR_MAIN_GREEN};
        color: {COLOR_WHITE};
        border-radius: 8px;
        border: none;
        padding: 0.6em 1.2em;
        font-weight: bold;
        width: 100%;
    }}
    div.stButton > button:hover {{
        background-color: {COLOR_DARK_GREEN};
        color: {COLOR_WHITE};
    }}
    /* Make the progress bar use our lime-green brand color
       instead of Streamlit's default red. */
    div[data-testid="stProgress"] > div > div > div {{
        background-color: {COLOR_LIME_GREEN};
    }}
    </style>
""", unsafe_allow_html=True)

# ============================================================
# APP MEMORY (SESSION STATE)
# Streamlit reruns the whole script every time the user clicks
# something. "session_state" is Streamlit's way of remembering
# information between those reruns, like a notebook that stays
# open. Here we set up that notebook the first time the app
# loads, with a starting "step" number and an empty answers box.
# ============================================================
if "step" not in st.session_state:
    st.session_state.step = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

# ============================================================
# HELPER FUNCTIONS
# These are small reusable tools we call later in the code.
# ============================================================

def go_to_next_step():
    """Moves the simulation forward one step."""
    st.session_state.step += 1

def go_to_previous_step():
    """Moves the simulation back one step, so users can fix answers."""
    st.session_state.step -= 1

def animated_reveal(text):
    """Shows text with a short typing-style animation for a fun feel."""
    placeholder = st.empty()
    shown = ""
    for letter in text:
        shown += letter
        placeholder.markdown(f"### {shown}")
        time.sleep(0.01)

# ============================================================
# HEADER
# This shows on every screen so users always know what app
# they're in. We added a one-line instruction under the title
# so first-time users immediately know what to do.
# ============================================================
st.title("💰 FinCoach")
st.caption("Your Interactive Life Simulator")
st.write("Answer a few quick questions below to see a personalized 10-year money projection.")

# ============================================================
# PROGRESS BAR
# This shows the user how far along they are in the simulation,
# out of 5 total steps (0 through 4). We added a small text
# label above the bar so the numbers make sense at a glance.
# ============================================================
total_steps = 5
st.caption(f"Step {min(st.session_state.step, total_steps)} of {total_steps}")
st.progress(min(st.session_state.step / total_steps, 1.0))
st.write("")  # a little breathing room before the step content

# ============================================================
# STEP 0: WELCOME SCREEN
# Introduces the simulation before asking any questions.
# ============================================================
if st.session_state.step == 0:
    with st.container(border=True):
        animated_reveal("Welcome to your Future Life Simulation! 🚀")
        st.write(
            "In the next few steps, you'll answer some questions about "
            "yourself, your education, your career path, and your money "
            "habits. At the end, we'll show you a personalized projection "
            "of what your financial future could look like."
        )
        st.write("")
        if st.button("Start My Simulation ➡️"):
            go_to_next_step()
            st.rerun()

# ============================================================
# STEP 1: PERSONAL INFORMATION
# Collects basic info about the user.
# ============================================================
elif st.session_state.step == 1:
    with st.container(border=True):
        st.header("🧑 Step 1: About You")
        name = st.text_input("What's your first name?", value=st.session_state.answers.get("name", ""))
        age = st.slider("How old are you?", 14, 30, value=st.session_state.answers.get("age", 18))

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                go_to_previous_step()
                st.rerun()
        with col2:
            if st.button("Next ➡️"):
                st.session_state.answers["name"] = name
                st.session_state.answers["age"] = age
                go_to_next_step()
                st.rerun()

# ============================================================
# STEP 2: EDUCATION
# Asks about the user's education plans, since this affects
# future career options and salary in our projection.
# ============================================================
elif st.session_state.step == 2:
    with st.container(border=True):
        st.header("🎓 Step 2: Your Education Path")
        education = st.radio(
            "What's your education plan after high school?",
            ["Start working right away", "Trade or certificate program", "2-year college degree", "4-year college degree"],
            index=["Start working right away", "Trade or certificate program", "2-year college degree", "4-year college degree"].index(
                st.session_state.answers.get("education", "Start working right away")
            )
        )

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                go_to_previous_step()
                st.rerun()
        with col2:
            if st.button("Next ➡️"):
                st.session_state.answers["education"] = education
                go_to_next_step()
                st.rerun()

# ============================================================
# STEP 3: CAREER
# Asks which career field the user is interested in. Each
# field has a rough starting salary we use later in the math.
# ============================================================
elif st.session_state.step == 3:
    with st.container(border=True):
        st.header("💼 Step 3: Your Career Path")

        # This dictionary maps a career field to a rough starting
        # yearly salary. These are simplified estimates for the
        # simulation, not real financial advice.
        career_salaries = {
            "Healthcare": 45000,
            "Technology": 55000,
            "Skilled Trade (electrician, plumber, etc.)": 42000,
            "Business / Finance": 48000,
            "Creative Arts / Media": 35000,
            "Education": 38000,
        }

        career = st.selectbox("What career field interests you most?", list(career_salaries.keys()))

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                go_to_previous_step()
                st.rerun()
        with col2:
            if st.button("Next ➡️"):
                st.session_state.answers["career"] = career
                st.session_state.answers["starting_salary"] = career_salaries[career]
                go_to_next_step()
                st.rerun()

# ============================================================
# STEP 4: FINANCIAL HABITS
# Asks about money habits, which shape how fast savings grow
# or how debt builds up in the projection.
# ============================================================
elif st.session_state.step == 4:
    with st.container(border=True):
        st.header("💵 Step 4: Your Money Habits")

        savings_rate = st.slider(
            "What percent of your income do you think you'll save each month?",
            0, 50, value=st.session_state.answers.get("savings_rate", 10)
        )

        has_debt = st.radio(
            "Do you expect to have student loans or other debt?",
            ["No debt", "Some debt (like a car loan)", "A lot of debt (like student loans)"]
        )

        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                go_to_previous_step()
                st.rerun()
        with col2:
            if st.button("See My Future ➡️"):
                st.session_state.answers["savings_rate"] = savings_rate
                st.session_state.answers["debt_level"] = has_debt
                go_to_next_step()
                st.rerun()

# ============================================================
# STEP 5: THE PROJECTION (RESULTS SCREEN)
# This is the payoff step. We take everything the user told us
# and run a simple year-by-year money calculation to estimate
# how their savings could grow over the next 10 years.
# ============================================================
elif st.session_state.step == 5:
    answers = st.session_state.answers
    name = answers.get("name", "Friend")

    st.balloons()
    st.header(f"🔮 {name}'s 10-Year Financial Future")

    # ---- Pull in the answers we collected earlier ----
    salary = answers.get("starting_salary", 40000)
    savings_rate = answers.get("savings_rate", 10) / 100
    debt_level = answers.get("debt_level", "No debt")
    education = answers.get("education", "Start working right away")

    # ---- Extra years of school can delay full-time income ----
    # We use this to decide how many "low income" years happen
    # before the full starting salary kicks in.
    if education == "4-year college degree":
        delay_years = 4
    elif education == "2-year college degree":
        delay_years = 2
    elif education == "Trade or certificate program":
        delay_years = 1
    else:
        delay_years = 0

    # ---- Debt reduces how much money is left to save each year ----
    if debt_level == "A lot of debt (like student loans)":
        debt_payment = 4000
    elif debt_level == "Some debt (like a car loan)":
        debt_payment = 2000
    else:
        debt_payment = 0

    # ---- Run the year-by-year simulation ----
    # We assume savings grow a small amount each year from
    # interest (like a savings account), using a simple 3% rate.
    interest_rate = 0.03
    years = 10
    total_savings = 0
    yearly_totals = []

    for year in range(1, years + 1):
        # During "delay years" (still in school), income is lower
        if year <= delay_years:
            yearly_income = salary * 0.3
        else:
            yearly_income = salary

        yearly_savings_amount = (yearly_income * savings_rate) - debt_payment
        if yearly_savings_amount < 0:
            yearly_savings_amount = 0

        # Add this year's savings, then apply interest growth
        total_savings += yearly_savings_amount
        total_savings = total_savings * (1 + interest_rate)

        yearly_totals.append(round(total_savings, 2))

    # ---- Show the results ----
    st.subheader("📈 Your Estimated Savings Growth")
    st.line_chart({"Estimated Savings ($)": yearly_totals})

    st.subheader("📋 Summary")

    # Four quick-glance number cards instead of plain text lines,
    # so the key results are easier to scan at a glance.
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Estimated starting salary", f"${salary:,}")
        st.metric("Savings rate", f"{int(savings_rate * 100)}%")
    with col2:
        st.metric("10-year estimated savings", f"${yearly_totals[-1]:,.2f}")
        st.metric("Debt situation", debt_level)

    st.write("")
    st.write(f"**Career path:** {answers.get('career', 'N/A')}")
    st.write(f"**Education plan:** {education}")

    st.info(
        "This is a simplified estimate to help you think about your choices. "
        "Real life includes more variables like raises, emergencies, and market changes!"
    )

    st.write("")
    if st.button("🔁 Start Over"):
        st.session_state.step = 0
        st.session_state.answers = {}
        st.rerun()
