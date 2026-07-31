# =========================================================
# FinCoach - app.py
# A Streamlit app that teaches young adults about money
# through a life simulator, an AI-style financial helper,
# a finance tracker, and a full lessons + quiz course.
#
# Everything lives in this ONE file on purpose, so the team
# can read it top to bottom and see how each part works.
# =========================================================

import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# This repository now uses a Django backend to serve the iOS app.
# The legacy Streamlit prototype has been moved to `legacy_streamlit_app.py`.
# To run the Django backend locally:
#   cd fincoach_project
#   python manage.py runserver

print("This repository is configured as a Django backend. See fincoach_project/manage.py to run the server.")
# Keep a minimal module surface so importing `app.py` doesn't error for tooling.
PROJECT_ROOT = Path(__file__).resolve().parent
PROJECT_MODULES = {
    "financial_helper": {
        "title": "🧠 Financial Helper Module",
        "summary": "This module groups the helper app files that power the money-advice experience.",
        "files": [
            ("views.py", PROJECT_ROOT / "fincoach_project" / "financial_helper" / "views.py"),
            ("urls.py", PROJECT_ROOT / "fincoach_project" / "financial_helper" / "urls.py"),
            ("template", PROJECT_ROOT / "fincoach_project" / "financial_helper" / "templates" / "financial_helper" / "helper.html"),
        ],
    },
    "simulator": {
        "title": "🎮 Simulator Module",
        "summary": "This module contains the simulator views, routes, and the template used by the 3D experience.",
        "files": [
            ("views.py", PROJECT_ROOT / "fincoach_project" / "simulator" / "views.py"),
            ("urls.py", PROJECT_ROOT / "fincoach_project" / "simulator" / "urls.py"),
            ("template", PROJECT_ROOT / "fincoach_project" / "simulator" / "templates" / "simulator" / "simulator.html"),
        ],
    },
    "tracker": {
        "title": "📈 Tracker Module",
        "summary": "This module is the finance dashboard scaffold, ready to be expanded into a richer tracker.",
        "files": [
            ("views.py", PROJECT_ROOT / "fincoach_project" / "tracker" / "views.py"),
            ("urls.py", PROJECT_ROOT / "fincoach_project" / "tracker" / "urls.py"),
            ("template", PROJECT_ROOT / "fincoach_project" / "tracker" / "templates" / "tracker" / "dashboard.html"),
        ],
    },
}

# ---------------------------------------------------------
# PAGE SETUP
# This runs once and sets the browser tab title/icon and
# tells Streamlit to use the full width of the screen.
# ---------------------------------------------------------
st.set_page_config(page_title="FinCoach", page_icon="💰", layout="wide")

# ---------------------------------------------------------
# BRAND COLORS
# Pulling all your brand colors into one place so every
# part of the app uses the same look.
# ---------------------------------------------------------
COLOR_TEAL = "#4DC49B"
COLOR_DARK_GREEN = "#488C74"
COLOR_WHITE = "#FFFFFF"
COLOR_DEEP_GREEN = "#21815F"
COLOR_LIME = "#9FC35C"
COLOR_TEXT = "#000000"

# ---------------------------------------------------------
# CUSTOM CSS
# This is plain CSS injected through Streamlit's markdown
# tool. It colors the background, sidebar, buttons, and
# forces all text to be dark so it's always readable on
# the light backgrounds we're using.
# ---------------------------------------------------------
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLOR_WHITE};
        color: {COLOR_TEXT};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_DEEP_GREEN};
    }}
    section[data-testid="stSidebar"] * {{
        color: {COLOR_WHITE} !important;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, span, div {{
        color: {COLOR_TEXT};
    }}
    .stButton>button {{
        background-color: {COLOR_TEAL};
        color: {COLOR_WHITE};
        border: none;
        border-radius: 8px;
        padding: 0.5em 1.2em;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background-color: {COLOR_DEEP_GREEN};
        color: {COLOR_WHITE};
    }}
    div[data-testid="stMetric"] {{
        background-color: {COLOR_LIME}33;
        border-radius: 10px;
        padding: 10px;
    }}
    .fc-card {{
        background-color: {COLOR_TEAL}22;
        border-left: 6px solid {COLOR_DEEP_GREEN};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: {COLOR_TEXT};
    }}
    .fc-banner {{
        background-color: {COLOR_DEEP_GREEN};
        color: {COLOR_WHITE} !important;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 16px;
    }}
    .fc-banner * {{
        color: {COLOR_WHITE} !important;
    }}
    .fc-gif-wrap {{
        display: flex;
        justify-content: center;
        margin-bottom: 14px;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SCENE GIFS
#
# How this works for the team: drop a gif file into the
# /gifs folder next to this app, using the exact filename
# listed below for that scene, and it will show up
# automatically the next time the app runs. Nobody needs to
# edit or uncomment any code. If the file isn't there yet,
# the app just skips it and moves on -- so it's always safe
# to run the app before every gif exists.
#
# Example: to add the Home scene walking character, save a
# file as  gifs/home.gif
# ---------------------------------------------------------
GIF_FOLDER = os.path.join(os.path.dirname(__file__), "gifs")

SCENE_GIFS = {
    "home": "home.gif",
    "school": "school.gif",
    "company": "company.gif",
    "bank": "bank.gif",
    "future": "future.gif",
}

def show_scene_gif(scene_key, caption=None, width=260):
    """Shows the walking-character gif for a scene if the file
    exists in /gifs. Safe to call even before the gif is added --
    it just silently does nothing until the file shows up."""
    filename = SCENE_GIFS.get(scene_key)
    if not filename:
        return
    path = os.path.join(GIF_FOLDER, filename)
    if os.path.exists(path):
        st.markdown('<div class="fc-gif-wrap">', unsafe_allow_html=True)
        st.image(path, width=width, caption=caption)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE SETUP
# Streamlit reruns the whole script every time someone
# clicks something. session_state is how we remember
# answers between those reruns (it's like the app's memory).
# ---------------------------------------------------------
def init_state():
    defaults = {
        "sim_step": 0,
        "sim_data": {},
        "helper_stage": "input",
        "quiz_answers": {},
        "quiz_submitted": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# =========================================================
# PART 1: THE LIFE SIMULATOR (Sprint 1 feature)
#
# This walks a user through a set of life stages (Home,
# School, Company, Bank, Future) collecting info about them,
# then shows a future projection at the end. We show the
# "map" as a simple row of stage icons that light up green
# once finished, plus a walking-character gif per scene once
# the team drops one in.
#
# On purpose, this does NOT include: a clickable map with
# roads/avatars, a family builder, an animated 2024-2050
# slider, or achievements -- those were cut to fit the time
# available and aren't needed to teach the money lesson.
# =========================================================

SIMULATOR_HTML_PATH = Path(__file__).resolve().parent / "fincoach_project" / "life_simulator_realistic.html"


def load_simulator_html():
    """Render the HTML-based life simulator inside the Streamlit app."""
    if not SIMULATOR_HTML_PATH.exists():
        st.error(f"Could not find the simulator file at {SIMULATOR_HTML_PATH}")
        return

    html = SIMULATOR_HTML_PATH.read_text(encoding="utf-8")
    components.html(html, height=940, scrolling=False)


SIM_STAGES = ["Home", "School", "Company", "Bank", "Future"]

def sim_progress_map():
    """Draws a simple text-based version of the map, showing
    which stage is done, current, or locked."""
    cols = st.columns(len(SIM_STAGES))
    for i, stage in enumerate(SIM_STAGES):
        with cols[i]:
            if i < st.session_state.sim_step:
                st.markdown(f"✅ **{stage}**")
            elif i == st.session_state.sim_step:
                st.markdown(f"➡️ **{stage}**")
            else:
                st.markdown(f"🔒 {stage}")

def sim_next():
    st.session_state.sim_step += 1

def sim_back():
    if st.session_state.sim_step > 0:
        st.session_state.sim_step -= 1

def life_simulator_page():
    st.header("🧭 Life Simulator")
    st.caption("This view renders the HTML-based life simulator you built so it can run inside Streamlit.")
    st.write("")
    load_simulator_html()


# =========================================================
# PART 2: AI FINANCIAL HELPER
#
# No API key is used here (the instructions say never to
# use secret keys), so instead of calling a real AI model,
# this uses clear, rule-based math and logic to give
# consistent, explainable advice. It still walks through
# the same steps described in the spec: situation -> inputs
# -> verdict -> alternative -> plan.
# =========================================================

def monthly_payment(principal, annual_rate_pct, months):
    """Standard loan payment formula (amortization)."""
    if months <= 0:
        return 0
    monthly_rate = (annual_rate_pct / 100) / 12
    if monthly_rate == 0:
        return principal / months
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

def financial_helper_page():
    st.header("🤖 AI Financial Helper")
    st.caption("Describe a money decision you're weighing, and get a clear, math-based breakdown.")

    if st.session_state.helper_stage == "input":
        situation = st.selectbox("What are you deciding about?", ["Buying a car", "Buying a home", "A general purchase"])

        st.markdown("#### 💵 Your budget")
        i1, i2, i3 = st.columns(3)
        income = i1.number_input("Monthly income ($)", min_value=0, value=3000)
        commitments = i2.number_input("Monthly commitments ($)", min_value=0, value=1500)
        emergency_savings = i3.number_input("Emergency savings ($)", min_value=0, value=1000)

        st.markdown("#### 🛒 The purchase")
        p1, p2 = st.columns(2)
        price = p1.number_input(f"Price of the {situation.lower().replace('a ', '').replace('buying ', '')} ($)",
                                 min_value=0, value=20000)
        down_payment = p2.number_input("Down payment ($)", min_value=0, value=2000)
        r1, r2 = st.columns(2)
        rate = r1.number_input("Estimated interest rate (%)", min_value=0.0, value=6.5)
        term_months = r2.number_input("Loan term (months)", min_value=1, value=60)

        st.write("")
        if st.button("Get My Verdict"):
            loan_amount = max(price - down_payment, 0)
            payment = monthly_payment(loan_amount, rate, term_months)
            total_cost = payment * term_months + down_payment
            budget_after = income - commitments - payment
            ratio = payment / income if income > 0 else 1

            st.session_state.helper_result = {
                "situation": situation, "price": price, "down_payment": down_payment,
                "rate": rate, "term_months": term_months, "payment": payment,
                "total_cost": total_cost, "budget_after": budget_after, "ratio": ratio,
                "emergency_savings": emergency_savings,
            }
            st.session_state.helper_stage = "result"

    elif st.session_state.helper_stage == "result":
        r = st.session_state.helper_result
        st.subheader(f"Verdict: {r['situation']}")

        if r["ratio"] > 0.20 or r["budget_after"] < 0:
            verdict = "⚠️ This stretches your budget. Consider a lower price or bigger down payment."
        elif r["ratio"] > 0.12:
            verdict = "🟡 This is manageable, but leaves less room for savings and surprises."
        else:
            verdict = "✅ This fits comfortably within your budget."

        st.markdown(f'<div class="fc-banner"><h4>{verdict}</h4></div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly payment", f"${r['payment']:,.0f}")
        c2.metric("Budget left after payment", f"${r['budget_after']:,.0f}")
        c3.metric("Total cost over time", f"${r['total_cost']:,.0f}")

        st.markdown("#### Watch out for")
        st.markdown('<div class="fc-card">Interest adds up: you\'ll pay '
                    f"${r['total_cost'] - r['price']:,.0f} more than the sticker price by the end of the loan. "
                    "A shorter term or bigger down payment reduces that.</div>", unsafe_allow_html=True)

        st.markdown("#### Credit impact")
        if r["ratio"] > 0.20:
            st.markdown('<div class="fc-card">Taking on a payment this large relative to income can make it '
                        'harder to keep up with other bills, which risks late payments and credit damage.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="fc-card">Making this payment on time, every time, is one of the best things '
                        'you can do for your credit score.</div>', unsafe_allow_html=True)

        st.markdown("#### Alternatives to consider")
        alt_price = r["price"] * 0.8
        alt_payment = monthly_payment(alt_price - r["down_payment"], r["rate"], r["term_months"])
        st.markdown(f'<div class="fc-card">💡 A similar option priced around <b>${alt_price:,.0f}</b> would bring '
                    f"the payment down to about <b>${alt_payment:,.0f}</b>/month.</div>", unsafe_allow_html=True)

        if st.button("Build My Plan With This Alternative"):
            st.session_state.helper_stage = "plan"
            st.session_state.helper_alt_price = alt_price
            st.session_state.helper_alt_payment = alt_payment

        if st.button("⬅️ Start Over", key="helper_reset"):
            st.session_state.helper_stage = "input"

    elif st.session_state.helper_stage == "plan":
        r = st.session_state.helper_result
        alt_price = st.session_state.helper_alt_price
        alt_payment = st.session_state.helper_alt_payment

        st.subheader("📝 Your Plan")
        st.markdown("**Plan Snapshot**")
        st.write(f"Price: ${alt_price:,.0f} | Down payment: ${r['down_payment']:,.0f} | "
                 f"Term: {r['term_months']} months | Rate: {r['rate']}%")

        st.markdown("**Payment Breakdown**")
        st.write(f"Estimated monthly payment: ${alt_payment:,.0f}")

        st.markdown("**Budget Fit**")
        new_budget_after = r["budget_after"] + (r["payment"] - alt_payment)
        st.write(f"Budget left after this payment: ${new_budget_after:,.0f}/month")

        st.markdown("**Milestone Timeline**")
        st.write(f"- Month 1: First payment made\n- Month {r['term_months']//2}: Halfway paid off\n"
                 f"- Month {r['term_months']}: Fully paid off")

        st.markdown("**Guardrail**")
        st.markdown('<div class="fc-card">Keep at least 3 months of expenses in your emergency fund before '
                    'taking on this payment, so a surprise cost doesn\'t force you to miss a payment.</div>',
                    unsafe_allow_html=True)

        if st.button("⬅️ Start Over", key="plan_reset"):
            st.session_state.helper_stage = "input"


# =========================================================
# PART 3: FINANCE TRACKER
#
# A simple manual dashboard. In a real app this would pull
# from a bank connection, but since we can't use outside
# services or secret keys here, the user types in numbers
# and we calculate everything live.
# =========================================================

def finance_tracker_page():
    st.header("📊 Finance Tracker")
    st.caption("Enter your numbers below to see your full financial picture.")

    c1, c2 = st.columns(2)
    with c1:
        checking = st.number_input("Checking balance ($)", min_value=0, value=800)
        savings = st.number_input("Savings balance ($)", min_value=0, value=2500)
        investments = st.number_input("Investments ($)", min_value=0, value=1000)
    with c2:
        credit_debt = st.number_input("Credit card debt ($)", min_value=0, value=400)
        loans = st.number_input("Loans (student/auto/etc.) ($)", min_value=0, value=8000)
        income = st.number_input("Monthly income ($)", min_value=0, value=3000)

    st.divider()
    st.markdown("#### 🧾 Monthly spending by category")
    cat_cols = st.columns(4)
    rent = cat_cols[0].number_input("Rent/Housing ($)", min_value=0, value=1000)
    food = cat_cols[1].number_input("Food ($)", min_value=0, value=400)
    fun = cat_cols[2].number_input("Entertainment ($)", min_value=0, value=150)
    other = cat_cols[3].number_input("Other ($)", min_value=0, value=200)

    total_balance = checking + savings + investments
    total_liabilities = credit_debt + loans
    net_worth = total_balance - total_liabilities
    total_spent = rent + food + fun + other
    savings_rate = ((income - total_spent) / income * 100) if income > 0 else 0

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Balance", f"${total_balance:,.0f}")
    m2.metric("Net Worth", f"${net_worth:,.0f}")
    m3.metric("Monthly Spending", f"${total_spent:,.0f}")
    m4.metric("Savings Rate", f"{savings_rate:,.1f}%")

    st.markdown("#### Spending breakdown")
    st.bar_chart({"Category": ["Rent", "Food", "Fun", "Other"], "Amount": [rent, food, fun, other]},
                 x="Category", y="Amount")

    st.markdown("#### Liabilities")
    st.write(f"Credit card debt: ${credit_debt:,.0f}  |  Loans: ${loans:,.0f}  |  **Total: ${total_liabilities:,.0f}**")


# =========================================================
# PART 4: FINANCE LITERACY COURSE
#
# COURSE is a plain Python list of "units." Each unit has a
# title and a list of "lessons." Each lesson has a title,
# two article sections, and a quiz (a list of questions).
# This is fully filled in for Unit 1 as a working example.
# To add the rest of the units, your Content Developer can
# copy the Unit 1 pattern below and paste in the article
# text and quiz questions from the full curriculum document
# -- the app will automatically show them once they're added.
# =========================================================

def q_tf(question, answer):
    return {"type": "tf", "question": question, "answer": answer}

def q_mc(question, choices, answer):
    return {"type": "mc", "question": question, "choices": choices, "answer": answer}

COURSE = [
    {
        "title": "Unit 1: Money Mindset & Financial Foundations",
        "lessons": [
            {
                "title": "1.1 Needs vs. Wants vs. Values",
                "part1": (
                    "Every dollar you spend is a decision, but most people never stop to ask why they're "
                    "spending it. Needs are things you must have to live and function: food, shelter, basic "
                    "clothing, transportation, healthcare. Wants make life more enjoyable but aren't required "
                    "for survival -- streaming subscriptions, eating out, a fancier phone than you need. Values "
                    "are different from both: they're what actually matters to you, and they shape which needs "
                    "and wants you prioritize. Two people with the same income can spend completely differently "
                    "because their values differ, and neither is wrong."
                ),
                "part2": (
                    "Knowing the difference is step one; using it before you spend is step two. Run purchases "
                    "through a simple filter: Is this a need (then ask how much to spend, not whether to buy)? "
                    "Is this a want (then check it fits your budget and lines up with something you value)? Does "
                    "this reflect a value or just a mood? The goal isn't perfection, it's awareness -- most people "
                    "who feel 'bad with money' actually just lack a clear sense of what they value, so their "
                    "spending has no compass."
                ),
                "quiz": [
                    q_tf("A 'need' is something required for survival or basic functioning, while a 'want' improves comfort but isn't essential.", True),
                    q_tf("Personal values have no real impact on how people choose to spend money.", False),
                    q_tf("Two people with the same income will always spend money the same way.", False),
                    q_tf("Identifying your values makes budgeting decisions easier because you know what to prioritize.", True),
                    q_mc("Which of these is most likely a 'need'?", ["Streaming subscription", "Rent payment", "Designer shoes", "Concert ticket"], "Rent payment"),
                    q_mc("Why do financial experts recommend identifying personal values before budgeting?", ["It's required by banks", "It helps prioritize spending in a way that feels meaningful", "It increases your credit score", "It removes the need for a budget"], "It helps prioritize spending in a way that feels meaningful"),
                ],
            },
            {
                "title": "1.2 Opportunity Cost & Trade-Offs",
                "part1": (
                    "Opportunity cost means every choice you make means giving up something else you could have "
                    "chosen instead. Money and time are limited, so every 'yes' to spending is automatically a "
                    "'no' to something else -- that 'no' is the real cost of the decision, not the price tag."
                ),
                "part2": (
                    "Before buying something, name the alternative: what's the next most useful thing that money "
                    "could do? Compare value, not just price -- a $50 purchase and a $50 emergency-fund deposit "
                    "cost the same but aren't equal in value. Watch for small trade-offs that add up over a year. "
                    "The goal isn't to eliminate trade-offs, it's to make them on purpose."
                ),
                "quiz": [
                    q_tf("Opportunity cost is the value of the next best alternative given up when making a choice.", True),
                    q_tf("Opportunity cost only applies to large purchases, not small ones.", False),
                    q_mc("Opportunity cost is best described as:", ["The tax on a purchase", "The value of the next best alternative you give up", "The interest earned on savings", "A type of bank fee"], "The value of the next best alternative you give up"),
                ],
            },
            {
                "title": "1.3 Setting Financial Goals (Short/Medium/Long-Term)",
                "part1": (
                    "'I want to save money' is a wish, not a goal. A real goal answers three questions: what "
                    "exactly, how much, and by when. Short-term goals (within a year) usually live in a regular "
                    "savings account. Medium-term goals (1-5 years) often need a dedicated account. Long-term "
                    "goals (5+ years) benefit from time itself through compounding."
                ),
                "part2": (
                    "Make goals specific and measurable, attach a reason, break big goals into smaller "
                    "checkpoints, automate contributions where possible, and revisit goals as life changes. "
                    "Revisiting a goal isn't failure -- it's active management."
                ),
                "quiz": [
                    q_tf("Short-term goals are typically achievable within a year or less.", True),
                    q_tf("Financial goals should never be adjusted once they're set.", False),
                    q_mc("Which is the best example of a short-term financial goal?", ["Retirement savings", "Saving $300 for a trip in two months", "Paying off a 30-year mortgage", "Building generational wealth"], "Saving $300 for a trip in two months"),
                ],
            },
            {
                "title": "1.4 Why Financial Literacy Is a Lifelong Skill",
                "part1": (
                    "Financial literacy isn't a one-time lesson -- it works more like fitness: something you "
                    "maintain and adapt over a lifetime as your circumstances change (first job, loans, a home, "
                    "a family, retirement) and as the financial world itself changes (new rules, new products, "
                    "new scams)."
                ),
                "part2": (
                    "Build the habit of staying engaged: check in with your money regularly, stay curious when "
                    "life changes, treat mistakes as data rather than failure, and reassess goals as your life "
                    "shifts. The real goal isn't mastering everything now -- it's knowing how to keep learning."
                ),
                "quiz": [
                    q_tf("Financial literacy is only useful during young adulthood and becomes irrelevant later in life.", False),
                    q_tf("Financial decisions and knowledge needs evolve as life circumstances change.", True),
                    q_mc("Why is financial literacy considered a 'lifelong' skill?", ["Because financial situations and needs change throughout life", "Because it's only taught once in school", "Because money never changes", "Because it's irrelevant after age 30"], "Because financial situations and needs change throughout life"),
                ],
            },
        ],
        "unit_test": [
            q_tf("A need is essential, while a want improves comfort or enjoyment.", True),
            q_tf("Short-term goals are usually achievable within a year.", True),
            q_tf("Financial literacy needs stop evolving once someone turns 25.", False),
            q_mc("Which best describes opportunity cost?", ["A bank fee", "The next best alternative given up", "A tax rate", "A type of loan"], "The next best alternative given up"),
            q_mc("Why does financial literacy matter across an entire lifetime?", ["Because financial circumstances and products change over time", "Because it's only relevant once", "Because money never changes", "Because it's optional after adulthood"], "Because financial circumstances and products change over time"),
        ],
    },
]

# Placeholder outline for the remaining units so the full course
# structure is visible in the app. Add "lessons" and "unit_test"
# to each of these using the exact same format as Unit 1 above.
REMAINING_UNIT_TITLES = [
    "Unit 2: Budgeting & Cash Flow Management",
    "Unit 3: Banking & Financial Institutions",
    "Unit 4: Saving Strategies & Emergency Funds",
    "Unit 5: Understanding & Building Credit",
    "Unit 6: Debt Management",
    "Unit 7: Student Loans & Financing Education",
    "Unit 8: Taxes Across a Lifetime",
    "Unit 9: Earning, Careers & Income Growth",
    "Unit 10: Investing Fundamentals",
    "Unit 11: Retirement Planning",
    "Unit 12: Insurance & Risk Management",
    "Unit 13: Major Purchases & Big Financial Decisions",
    "Unit 14: Homeownership & Real Estate",
    "Unit 15: Marriage, Family & Household Finances",
    "Unit 16: Small Business & Entrepreneurship Basics",
    "Unit 17: Estate Planning & Generational Wealth",
    "Unit 18: Identity Protection & Financial Fraud",
    "Unit 19: Navigating Financial Setbacks",
    "Unit 20: Capstone - Building a Lifelong Financial Plan",
]
for t in REMAINING_UNIT_TITLES:
    COURSE.append({"title": t, "lessons": [], "unit_test": []})


def run_quiz(quiz_key, questions):
    """Draws a quiz (radio buttons per question) and a submit
    button that grades it and shows the score."""
    if not questions:
        st.info("No quiz questions added for this section yet.")
        return

    answers = st.session_state.quiz_answers.setdefault(quiz_key, {})
    for i, q in enumerate(questions):
        st.markdown(f"**{i+1}. {q['question']}**")
        if q["type"] == "tf":
            choice = st.radio("", ["True", "False"], key=f"{quiz_key}_{i}", label_visibility="collapsed")
            answers[i] = (choice == "True")
        else:
            choice = st.radio("", q["choices"], key=f"{quiz_key}_{i}", label_visibility="collapsed")
            answers[i] = choice

    if st.button("Submit Quiz", key=f"submit_{quiz_key}"):
        score = 0
        for i, q in enumerate(questions):
            if answers.get(i) == q["answer"]:
                score += 1
        st.session_state.quiz_submitted[quiz_key] = score
        st.success(f"You scored {score}/{len(questions)} ✅")


def course_page():
    st.header("📚 Financial Literacy Course")
    st.caption("Pick a unit, then work through its lessons and quizzes at your own pace.")
    unit_titles = [u["title"] for u in COURSE]
    unit_choice = st.selectbox("Choose a unit", unit_titles)
    unit = COURSE[unit_titles.index(unit_choice)]
    st.divider()

    if not unit["lessons"]:
        st.info("This unit's lessons and quiz haven't been added to the app yet. "
                "Copy the Unit 1 format in the code to add this unit's content.")
        return

    lesson_titles = [l["title"] for l in unit["lessons"]] + ["Unit Test"]
    lesson_choice = st.radio("Lesson", lesson_titles)

    if lesson_choice == "Unit Test":
        st.subheader(f"{unit['title']} -- Unit Test")
        run_quiz(f"{unit['title']}_test", unit["unit_test"])
    else:
        lesson = unit["lessons"][lesson_titles.index(lesson_choice)]
        st.subheader(lesson["title"])
        st.markdown("#### Part 1")
        st.write(lesson["part1"])
        st.markdown("#### Part 2")
        st.write(lesson["part2"])
        st.divider()
        st.markdown("#### Quiz")
        run_quiz(f"{unit['title']}_{lesson['title']}", lesson["quiz"])


# =========================================================
# PART 5: CONTACT US
# =========================================================

def contact_page():
    st.header("✉️ Contact Us")
    st.caption("Questions, feedback, or stuck on something? Send us a note and we'll get back to you.")
    with st.form("contact_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        message = st.text_area("What do you need help with?")
        submitted = st.form_submit_button("Send")
        if submitted:
            if name and email and message:
                st.success("Thank you! We will make sure to respond within 24 hours.")
            else:
                st.warning("Please fill in all fields before sending.")


# =========================================================
# HOME PAGE
# =========================================================

def home_page():
    st.markdown(f"""
    <div class="fc-banner">
        <h1>💰 Welcome to FinCoach</h1>
        <p>Helping young adults balance their financial lifestyle and avoid costly mistakes.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("👋 **New here?** Use the sidebar to jump to any tool below -- we suggest starting with the Life Simulator.")
    st.write("")

    features = [
        ("🧭", "Life Simulator", "See how today's choices shape your future"),
        ("🤖", "AI Financial Helper", "Get a clear verdict on a money decision"),
        ("📊", "Finance Tracker", "See your full financial picture in one place"),
        ("📚", "Financial Literacy Course", "Lessons, articles, and quizzes"),
    ]
    row1 = st.columns(2)
    row2 = st.columns(2)
    for col, (icon, title, desc) in zip(row1 + row2, features):
        col.markdown(
            f'<div class="fc-card"><b>{icon} {title}</b><br>{desc}</div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown('<div class="fc-card">✉️ <b>Contact Us</b><br>Reach the FinCoach team anytime.</div>',
                unsafe_allow_html=True)


# =========================================================
# NAVIGATION
# This sidebar menu decides which page function runs.
# =========================================================

def render_project_module_page(module_key):
    module = PROJECT_MODULES[module_key]
    st.header(module["title"])
    st.caption(module["summary"])
    st.divider()

    for label, path in module["files"]:
        with st.expander(label, expanded=True):
            if path.exists():
                st.write(f"Path: {path}")
                text = path.read_text(encoding="utf-8")
                preview = text[:1600]
                if len(text) > 1600:
                    preview += "\n..."
                st.code(preview, language="python" if path.suffix == ".py" else "html")
            else:
                st.warning(f"This file has not been created yet: {path}")


st.sidebar.title("💰 FinCoach")
st.sidebar.caption("Your money coach, in your pocket.")
st.sidebar.divider()
page = st.sidebar.radio("Go to", [
    "🏠 Home", "🧭 Life Simulator", "🤖 AI Financial Helper", "📊 Finance Tracker",
    "📚 Financial Literacy Course", "🧠 Financial Helper Module", "🎮 Simulator Module",
    "📈 Tracker Module", "✉️ Contact Us",
])
page = page.split(" ", 1)[1]  # strip the emoji back off so the rest of the app's logic doesn't need to change

if page == "Home":
    home_page()
elif page == "Life Simulator":
    life_simulator_page()
elif page == "AI Financial Helper":
    financial_helper_page()
elif page == "Finance Tracker":
    finance_tracker_page()
elif page == "Financial Literacy Course":
    course_page()
elif page == "Financial Helper Module":
    render_project_module_page("financial_helper")
elif page == "Simulator Module":
    render_project_module_page("simulator")
elif page == "Tracker Module":
    render_project_module_page("tracker")
elif page == "Contact Us":
    contact_page()


