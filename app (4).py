# =========================================================
# FinCoach - app.py
# A Streamlit app that teaches young adults about money
# through a life simulator, an AI-style financial helper,
# a finance tracker, and a full lessons + quiz course.
#
# Everything lives in this ONE file on purpose, so the team
# can read it top to bottom and see how each part works.
# =========================================================

import streamlit as st

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
</style>
""", unsafe_allow_html=True)

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
# School, Company, Store, Bank) collecting info about them,
# then shows a future projection at the end. We show the
# "map" as a simple row of stage icons that light up green
# once finished, since a full animated map needs graphics
# tools beyond plain Streamlit.
# =========================================================

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
    st.caption("Walk through a few real-life stages. At the end, you'll see how your choices might shape your future.")
    sim_progress_map()
    st.divider()

    data = st.session_state.sim_data
    step = st.session_state.sim_step

    # ---- Stage 0: Home / Character creation ----
    if step == 0:
        st.subheader("🏠 Home: Tell us about yourself")
        data["name"] = st.text_input("What's your name?", data.get("name", ""))
        data["age"] = st.slider("How old are you?", 16, 70, data.get("age", 20))
        data["has_family"] = st.radio("Do you currently have a family?", ["No", "Yes"],
                                       index=0 if data.get("has_family", "No") == "No" else 1)
        if data["has_family"] == "Yes":
            data["family_size"] = st.number_input("How many dependents (kids/others) do you support?",
                                                    min_value=0, max_value=10, value=data.get("family_size", 1))
        st.markdown("#### Housing")
        data["housing_type"] = st.selectbox("Do you rent or own?", ["Rent", "Own"],
                                             index=0 if data.get("housing_type", "Rent") == "Rent" else 1)
        data["housing_cost"] = st.number_input("Monthly housing payment ($)", min_value=0,
                                                value=data.get("housing_cost", 1200))
        st.markdown("#### Monthly bills")
        data["groceries"] = st.number_input("Monthly groceries ($)", min_value=0, value=data.get("groceries", 400))
        data["utilities"] = st.number_input("Monthly utilities + internet + phone ($)", min_value=0,
                                             value=data.get("utilities", 250))
        data["other_expenses"] = st.number_input("Other monthly expenses ($) (fun, subscriptions, etc.)",
                                                  min_value=0, value=data.get("other_expenses", 200))
        if st.button("Continue to School ➡️"):
            sim_next()

    # ---- Stage 1: School ----
    elif step == 1:
        st.subheader("🎓 School")
        data["education_level"] = st.selectbox(
            "What is your current education level?",
            ["High School", "Trade School", "College", "Graduate", "Not currently studying"],
            index=["High School", "Trade School", "College", "Graduate", "Not currently studying"].index(
                data.get("education_level", "College"))
        )
        if data["education_level"] in ["College", "Graduate"]:
            data["has_loan"] = st.radio("Do you have a student loan?", ["No", "Yes"],
                                         index=0 if data.get("has_loan", "No") == "No" else 1)
            if data["has_loan"] == "Yes":
                data["loan_amount"] = st.number_input("Total student loan amount ($)", min_value=0,
                                                       value=data.get("loan_amount", 20000))
                data["loan_payment"] = st.number_input("Monthly student loan payment ($)", min_value=0,
                                                        value=data.get("loan_payment", 200))
            else:
                data["loan_amount"] = 0
                data["loan_payment"] = 0
        else:
            data["loan_amount"] = data.get("loan_amount", 0)
            data["loan_payment"] = data.get("loan_payment", 0)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back"):
                sim_back()
        with c2:
            if st.button("Continue to Company ➡️"):
                sim_next()

    # ---- Stage 2: Company / Career ----
    elif step == 2:
        st.subheader("🏢 Company")
        data["employment_status"] = st.selectbox(
            "Employment status",
            ["Student job", "Part-time", "Full-time", "Self-employed", "Unemployed"],
            index=["Student job", "Part-time", "Full-time", "Self-employed", "Unemployed"].index(
                data.get("employment_status", "Full-time"))
        )
        data["job_title"] = st.text_input("Job title", data.get("job_title", "Retail Associate"))
        data["monthly_income"] = st.number_input("Monthly income, after taxes ($)", min_value=0,
                                                  value=data.get("monthly_income", 3000))
        data["retirement_pct"] = st.slider("What % of your income goes to retirement savings?",
                                            0, 30, data.get("retirement_pct", 5))
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back", key="back2"):
                sim_back()
        with c2:
            if st.button("Continue to Bank ➡️", key="next2"):
                sim_next()

    # ---- Stage 3: Bank ----
    elif step == 3:
        st.subheader("🏦 Bank")
        data["savings"] = st.number_input("Current savings balance ($)", min_value=0, value=data.get("savings", 1000))
        data["emergency_fund"] = st.number_input("Emergency fund balance ($)", min_value=0,
                                                  value=data.get("emergency_fund", 500))
        data["credit_card_debt"] = st.number_input("Credit card debt ($)", min_value=0,
                                                     value=data.get("credit_card_debt", 0))
        data["credit_card_payment"] = st.number_input("Monthly credit card payment ($)", min_value=0,
                                                        value=data.get("credit_card_payment", 0))
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back", key="back3"):
                sim_back()
        with c2:
            if st.button("See My Future ➡️", key="next3"):
                sim_next()

    # ---- Stage 4: Future Projection ----
    elif step == 4:
        st.subheader("🔮 Your Future Projection")
        years = st.slider("Look ahead how many years?", 1, 20, 5)

        # --- The math behind the projection (plain English) ---
        # Monthly leftover cash = income - all monthly costs.
        # We assume: income grows a little every year (raises),
        # leftover cash gets saved, and debts slowly shrink as
        # they're paid off.
        income = data.get("monthly_income", 3000)
        housing = data.get("housing_cost", 1200)
        groceries = data.get("groceries", 400)
        utilities = data.get("utilities", 250)
        other = data.get("other_expenses", 200)
        loan_payment = data.get("loan_payment", 0)
        cc_payment = data.get("credit_card_payment", 0)
        retirement_pct = data.get("retirement_pct", 5) / 100

        monthly_costs = housing + groceries + utilities + other + loan_payment + cc_payment
        retirement_contribution = income * retirement_pct
        leftover = income - monthly_costs - retirement_contribution

        savings = float(data.get("savings", 1000))
        emergency = float(data.get("emergency_fund", 500))
        debt = float(data.get("loan_amount", 0)) + float(data.get("credit_card_debt", 0))
        retirement_balance = 0.0

        yearly_income = [income * 12]
        yearly_savings = [savings]
        yearly_debt = [debt]
        yearly_net_worth = [savings + emergency - debt]

        for year in range(1, years + 1):
            income *= 1.03  # a small 3% yearly raise, on average
            monthly_costs_growth = monthly_costs * 1.02  # bills creep up slightly too
            retirement_contribution = income * retirement_pct
            leftover = max(income - monthly_costs_growth - retirement_contribution, 0)

            savings += leftover * 12
            retirement_balance = (retirement_balance + retirement_contribution * 12) * 1.06  # investment growth
            debt = max(debt - (loan_payment + cc_payment) * 12, 0)

            yearly_income.append(income * 12)
            yearly_savings.append(savings)
            yearly_debt.append(debt)
            yearly_net_worth.append(savings + emergency + retirement_balance - debt)

        st.markdown('<div class="fc-banner"><h3>📊 Your Snapshot</h3></div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Monthly leftover cash today", f"${leftover:,.0f}")
        m2.metric(f"Projected net worth in {years} yrs", f"${yearly_net_worth[-1]:,.0f}")
        m3.metric(f"Projected savings in {years} yrs", f"${yearly_savings[-1]:,.0f}")
        m4.metric(f"Remaining debt in {years} yrs", f"${yearly_debt[-1]:,.0f}")

        st.markdown("#### Net worth over time")
        chart_data = {
            "Year": list(range(0, years + 1)),
            "Net Worth": yearly_net_worth,
            "Savings": yearly_savings,
            "Debt": yearly_debt,
        }
        st.line_chart(chart_data, x="Year", y=["Net Worth", "Savings", "Debt"])

        st.markdown("#### What this tells you")
        if leftover < 0:
            st.markdown('<div class="fc-card">⚠️ Right now your monthly costs are higher than your income. '
                        'That means debt or savings will shrink over time unless income goes up or costs come down.</div>',
                        unsafe_allow_html=True)
        elif leftover < 100:
            st.markdown('<div class="fc-card">🟡 You are breaking even most months. Even a small emergency could '
                        'be tough to cover. Building up that emergency fund should be a top priority.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="fc-card">✅ You have positive cash flow every month. Keep automating '
                        'savings and paying down debt, and your net worth should keep climbing.</div>',
                        unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Life update: has anything changed?")
        st.caption("Check anything that applies, then restart to see a new projection with updated info.")
        st.checkbox("Got a raise or new job")
        st.checkbox("Had a child or added a dependent")
        st.checkbox("Paid off a loan or credit card")
        st.checkbox("Bought a home or car")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Back to Bank"):
                sim_back()
        with c2:
            if st.button("🔄 Start Over"):
                st.session_state.sim_step = 0
                st.session_state.sim_data = {}


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
        income = st.number_input("Monthly income ($)", min_value=0, value=3000)
        commitments = st.number_input("Monthly commitments (bills, debt, etc.) ($)", min_value=0, value=1500)
        emergency_savings = st.number_input("Emergency savings ($)", min_value=0, value=1000)

        price = st.number_input(f"Price of the {situation.lower().replace('a ', '').replace('buying ', '')} ($)",
                                 min_value=0, value=20000)
        down_payment = st.number_input("Down payment ($)", min_value=0, value=2000)
        rate = st.number_input("Estimated interest rate (%)", min_value=0.0, value=6.5)
        term_months = st.number_input("Loan term (months)", min_value=1, value=60)

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

    st.markdown("#### Monthly spending by category")
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
    unit_titles = [u["title"] for u in COURSE]
    unit_choice = st.selectbox("Choose a unit", unit_titles)
    unit = COURSE[unit_titles.index(unit_choice)]

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

    st.markdown("Use the sidebar to explore:")
    st.markdown("- 🧭 **Life Simulator** -- see how today's choices shape your future")
    st.markdown("- 🤖 **AI Financial Helper** -- get a clear verdict on a money decision")
    st.markdown("- 📊 **Finance Tracker** -- see your full financial picture in one place")
    st.markdown("- 📚 **Financial Literacy Course** -- lessons, articles, and quizzes")
    st.markdown("- ✉️ **Contact Us** -- reach the FinCoach team")


# =========================================================
# NAVIGATION
# This sidebar menu decides which page function runs.
# =========================================================

st.sidebar.title("💰 FinCoach")
page = st.sidebar.radio("Go to", [
    "Home", "Life Simulator", "AI Financial Helper", "Finance Tracker",
    "Financial Literacy Course", "Contact Us",
])

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
elif page == "Contact Us":
    contact_page()
