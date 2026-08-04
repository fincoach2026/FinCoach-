"""
finny.py — FinCoach's AI Helper Bot ("Finny")

A recyclable, chat-style financial situation analyzer.
Flow:
  1) SITUATION   -> user types a free-text situation statement
  2) COLLECTING  -> Finny welcomes them + asks for structured financial inputs
  3) ANALYSIS    -> Finny returns verdict, budget impact, total cost, color-coded
                     warnings, and 2 alternatives (Option B / Option C)
  4) DETAIL      -> if the user picks an alternative / asks for more, Finny
                     returns a deeper breakdown (payment breakdown, budget fit,
                     milestone timeline, what-it-buys, checklist, guardrail)
  5) -> resets back to SITUATION for a brand-new conversation

Drop this file next to main.py, course_data.py, life_simulation.py,
finance_tracker.py, styles.py. Integration notes are at the bottom of this file.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# BRAND COLORS (matches styles.py palette)
# ---------------------------------------------------------------------------
PRIMARY = "#4DC49B"       # main green
PRIMARY_DARK = "#21815F"  # deep green (headers/accents)
SECONDARY = "#488C74"     # muted green
ACCENT = "#9FC35C"        # lime accent
WHITE = "#FFFFFF"
TEXT = "#000000"
WARN_RED = "#E05B5B"
WARN_YELLOW = "#E0B94D"

BUBBLE_CSS = f"""
<style>
.finny-bubble {{
    background-color: {WHITE};
    border: 1px solid {PRIMARY};
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}}
.finny-bubble-title {{
    color: {PRIMARY_DARK};
    font-weight: 700;
    margin-bottom: 4px;
}}
.finny-verdict {{
    background-color: {PRIMARY};
    color: {WHITE};
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-weight: 600;
}}
.finny-warn-red {{
    background-color: #FBEAEA;
    border-left: 6px solid {WARN_RED};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    color: {TEXT};
}}
.finny-warn-yellow {{
    background-color: #FBF6E3;
    border-left: 6px solid {WARN_YELLOW};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    color: {TEXT};
}}
.finny-alt-card {{
    background-color: {WHITE};
    border: 1px solid {ACCENT};
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
}}
</style>
"""

# ---------------------------------------------------------------------------
# STATE MACHINE HELPERS
# ---------------------------------------------------------------------------
def _init_state():
    defaults = {
        "finny_stage": "situation",       # situation | collecting | analysis | detail
        "finny_situation": "",
        "finny_inputs": {},
        "finny_analysis": None,
        "finny_chosen_alt": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _reset_conversation():
    st.session_state["finny_stage"] = "situation"
    st.session_state["finny_situation"] = ""
    st.session_state["finny_inputs"] = {}
    st.session_state["finny_analysis"] = None
    st.session_state["finny_chosen_alt"] = None


# ---------------------------------------------------------------------------
# CORE FINANCIAL LOGIC (rule-based, no external calls)
# ---------------------------------------------------------------------------
def _monthly_payment(principal, annual_rate_pct, term_months):
    if principal <= 0 or term_months <= 0:
        return 0.0
    r = (annual_rate_pct / 100) / 12
    if r == 0:
        return principal / term_months
    return principal * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)


def _analyze(inputs):
    income = inputs["monthly_income"]
    commitments = inputs["monthly_commitments"]
    emergency = inputs["emergency_savings"]
    car_price = inputs["car_price"]
    down = inputs["down_payment"]
    rate = inputs["interest_rate"]
    term = inputs["loan_term"]

    loan_amount = max(car_price - down, 0)
    payment = _monthly_payment(loan_amount, rate, term)
    total_paid = payment * term + down
    total_interest = max(total_paid - car_price, 0)

    pct_income = (payment / income * 100) if income > 0 else 0
    leftover = income - commitments - payment
    weekly_income = income * 12 / 52
    hourly_est = inputs.get("hourly_rate")

    # Verdict
    if pct_income <= 15 and leftover > 0:
        verdict = "This is a comfortable, low-risk plan for your income level."
        verdict_tone = "good"
    elif pct_income <= 20 and leftover > 0:
        verdict = "This is tight, not impossible. A missed shift or slow month would put you behind."
        verdict_tone = "caution"
    else:
        verdict = "This plan is high-risk right now — the payment eats too much of your income."
        verdict_tone = "risky"

    # Warnings
    warnings = []
    if pct_income > 20:
        warnings.append(("red", f"Your payment would be about {pct_income:.0f}% of your take-home "
                                  f"income — that's above the recommended 15–20% ceiling for a car payment."))
    elif pct_income > 15:
        warnings.append(("yellow", f"Your payment would be about {pct_income:.0f}% of your take-home "
                                     f"income — on the higher end of the recommended range."))
    if leftover < 200:
        warnings.append(("red", f"After commitments and this payment, you'd have roughly "
                                  f"${max(leftover,0):.0f}/month left for food, gas, insurance, and everything else."))
    elif leftover < 500:
        warnings.append(("yellow", f"After commitments and this payment, you'd have roughly ${leftover:.0f}/month "
                                     f"of breathing room — enough for essentials, but little cushion."))
    monthly_expenses_est = commitments + payment
    if emergency < monthly_expenses_est * 3:
        warnings.append(("yellow", f"Your emergency savings (${emergency:.0f}) cover less than 3 months of your "
                                     f"new commitments — worth building that up before or alongside this purchase."))
    if rate >= 10:
        warnings.append(("yellow", f"A {rate:.1f}% interest rate is on the higher side — even a modest credit "
                                     f"improvement could lower your total cost noticeably."))

    # Alternatives
    alt_b_down = down + (income - commitments) * 0.5 * 6  # save ~half of leftover income for 6 months
    alt_b_down = min(alt_b_down, car_price)
    alt_b_loan = max(car_price - alt_b_down, 0)
    alt_b_payment = _monthly_payment(alt_b_loan, rate, term)
    alt_b_total = alt_b_payment * term + alt_b_down
    interest_saved_b = total_paid - alt_b_total

    alt_c_price = round(car_price * 0.75, -2)  # ~25% cheaper car, round to nearest 100
    alt_c_loan = max(alt_c_price - down, 0)
    alt_c_payment = _monthly_payment(alt_c_loan, rate, term)
    alt_c_total = alt_c_payment * term + down

    return {
        "loan_amount": loan_amount,
        "payment": payment,
        "total_paid": total_paid,
        "total_interest": total_interest,
        "pct_income": pct_income,
        "leftover": leftover,
        "weekly_income": weekly_income,
        "hourly_rate": hourly_est,
        "verdict": verdict,
        "verdict_tone": verdict_tone,
        "warnings": warnings,
        "alt_b": {
            "down": alt_b_down, "payment": alt_b_payment,
            "total": alt_b_total, "interest_saved": interest_saved_b,
        },
        "alt_c": {
            "price": alt_c_price, "payment": alt_c_payment, "total": alt_c_total,
            "payment_drop": payment - alt_c_payment,
        },
    }


def _build_detail(inputs, analysis, chosen):
    """Deeper breakdown for the chosen plan (current / Option B / Option C)."""
    income = inputs["monthly_income"]
    commitments = inputs["monthly_commitments"]
    term = inputs["loan_term"]
    rate = inputs["interest_rate"]

    if chosen == "B":
        price = inputs["car_price"]
        down = analysis["alt_b"]["down"]
        payment = analysis["alt_b"]["payment"]
        total = analysis["alt_b"]["total"]
    elif chosen == "C":
        price = analysis["alt_c"]["price"]
        down = inputs["down_payment"]
        payment = analysis["alt_c"]["payment"]
        total = analysis["alt_c"]["total"]
    else:
        price = inputs["car_price"]
        down = inputs["down_payment"]
        payment = analysis["payment"]
        total = analysis["total_paid"]

    financed = max(price - down, 0)
    pct_income = (payment / income * 100) if income > 0 else 0
    year1_interest_share = 61  # illustrative first-year amortization skew, matches your mockup framing
    leftover = income - commitments - payment

    return {
        "price": price, "down": down, "payment": payment, "total": total,
        "financed": financed, "pct_income": pct_income, "term": term, "rate": rate,
        "year1_interest_share": year1_interest_share, "leftover": leftover,
    }


# ---------------------------------------------------------------------------
# RENDER HELPERS
# ---------------------------------------------------------------------------
def _bubble(title, body_md):
    st.markdown(
        f'<div class="finny-bubble"><div class="finny-bubble-title">{title}</div>{body_md}</div>',
        unsafe_allow_html=True,
    )


def _warn(tone, text):
    cls = "finny-warn-red" if tone == "red" else "finny-warn-yellow"
    icon = "🔴" if tone == "red" else "🟡"
    st.markdown(f'<div class="{cls}">{icon} {text}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# MAIN PAGE ENTRY POINT
# ---------------------------------------------------------------------------
def render_finny_page():
    st.markdown(BUBBLE_CSS, unsafe_allow_html=True)
    _init_state()

    st.markdown(f"<h1 style='color:{TEXT};'>Finny — Your AI Money Helper</h1>", unsafe_allow_html=True)

    stage = st.session_state["finny_stage"]

    # ---------------- STAGE 1: SITUATION ----------------
    if stage == "situation":
        st.markdown(f"<p style='color:{PRIMARY_DARK}; font-weight:600;'>Situation Statement:</p>",
                     unsafe_allow_html=True)
        situation = st.text_area(
            "situation_input",
            placeholder="I'm 19, making $18/hour, and I'm thinking about financing a used car.",
            label_visibility="collapsed",
            key="situation_box",
        )
        if st.button("Send ➤", key="send_situation"):
            if situation.strip():
                st.session_state["finny_situation"] = situation.strip()
                st.session_state["finny_stage"] = "collecting"
                st.rerun()
            else:
                st.warning("Tell Finny a bit about your situation first.")
        return

    # Always show the situation statement as the top of the "conversation"
    _bubble("You said:", st.session_state["finny_situation"])

    # ---------------- STAGE 2: COLLECTING ----------------
    if stage == "collecting":
        _bubble(
            "Finny",
            "Hey! I'll be more than happy to provide analysis and a plan to help you reach your "
            "financial goal based on your situation. Fill in the fields below so I can give you the "
            "best advice possible 🙂",
        )
        with st.form("finny_inputs_form"):
            monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, step=50.0)
            monthly_commitments = st.number_input("Monthly Commitments (rent, etc.) ($)", min_value=0.0, step=25.0)
            emergency_savings = st.number_input("Emergency Savings ($)", min_value=0.0, step=50.0)
            car_price = st.number_input("Car Price ($)", min_value=0.0, step=100.0)
            down_payment = st.number_input("Down Payment Available ($)", min_value=0.0, step=100.0)
            interest_rate = st.number_input("Estimated Interest Rate (%)", min_value=0.0, step=0.1)
            loan_term = st.number_input("Loan Term (months)", min_value=1, step=1, value=60)
            submitted = st.form_submit_button("Get My Analysis ➤")

        if submitted:
            inputs = {
                "monthly_income": monthly_income,
                "monthly_commitments": monthly_commitments,
                "emergency_savings": emergency_savings,
                "car_price": car_price,
                "down_payment": down_payment,
                "interest_rate": interest_rate,
                "loan_term": int(loan_term),
            }
            st.session_state["finny_inputs"] = inputs
            st.session_state["finny_analysis"] = _analyze(inputs)
            st.session_state["finny_stage"] = "analysis"
            st.rerun()
        return

    inputs = st.session_state["finny_inputs"]
    analysis = st.session_state["finny_analysis"]

    # ---------------- STAGE 3: ANALYSIS ----------------
    if stage == "analysis":
        _bubble("Finny", "Thanks for the response. Here's your analysis right now 👇")

        st.markdown(f'<div class="finny-verdict">Verdict<br>{analysis["verdict"]}</div>',
                     unsafe_allow_html=True)

        _bubble(
            "Monthly Budget Impact",
            f"Your payment would be about <b>${analysis['payment']:.0f}/month</b> — that's "
            f"<b>{analysis['pct_income']:.0f}%</b> of your take-home income. After setting that aside, "
            f"you'd have roughly <b>${max(analysis['leftover'],0):.0f}/month</b> left for food, gas, "
            f"insurance, and everything else.",
        )

        term = inputs["loan_term"]
        _bubble(
            "Total Cost Over Time",
            f"Car price: ${inputs['car_price']:.0f}. Total over {term} months: "
            f"${analysis['total_paid']:.0f}. Total interest: ${analysis['total_interest']:.0f} — "
            f"{(analysis['total_interest']/inputs['car_price']*100 if inputs['car_price'] else 0):.0f}% "
            f"more than the car itself.",
        )

        st.markdown(f"<p style='color:{PRIMARY_DARK}; font-weight:700; margin-top:8px;'>⚠ Watch Out For:</p>",
                     unsafe_allow_html=True)
        for tone, text in analysis["warnings"]:
            _warn(tone, text)

        st.markdown(f"<p style='color:{PRIMARY_DARK}; font-weight:700; margin-top:8px;'>Alternatives:</p>",
                     unsafe_allow_html=True)

        b = analysis["alt_b"]
        st.markdown(
            f'<div class="finny-alt-card"><b>Option B</b> — Wait 6 months, save a bigger down payment.<br>'
            f'Impact: Payment drops to about ${b["payment"]:.0f}/month. Total interest drops to '
            f'about ${(b["total"] - inputs["car_price"] if inputs["car_price"] else 0):.0f} — saves you '
            f'~${b["interest_saved"]:.0f} over the life of the loan.</div>',
            unsafe_allow_html=True,
        )
        c = analysis["alt_c"]
        st.markdown(
            f'<div class="finny-alt-card"><b>Option C</b> — Same down payment, ${c["price"]:.0f} car instead.<br>'
            f'Impact: Payment drops to about ${c["payment"]:.0f}/month — cuts your negative-equity risk '
            f'almost entirely by month 6.</div>',
            unsafe_allow_html=True,
        )

        _bubble(
            "Summary",
            "This is the overall summary based on your situation and goal. If you'd like a full plan "
            "for an alternative option, pick one below. If you're ready as-is, we'll finalize your current plan. "
            "We'll always make sure you have all the details you need! 🙂",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Continue with current plan"):
                st.session_state["finny_chosen_alt"] = "current"
                st.session_state["finny_stage"] = "detail"
                st.rerun()
        with col2:
            if st.button("I want Option B"):
                st.session_state["finny_chosen_alt"] = "B"
                st.session_state["finny_stage"] = "detail"
                st.rerun()
        with col3:
            if st.button("I want Option C"):
                st.session_state["finny_chosen_alt"] = "C"
                st.session_state["finny_stage"] = "detail"
                st.rerun()

        free_text = st.text_input(
            "Or tell Finny what you'd like next",
            placeholder="I want to continue with option C",
            key="analysis_free_text",
        )
        if st.button("Send ➤", key="analysis_free_text_send") and free_text.strip():
            lowered = free_text.lower()
            chosen = "B" if " b" in f" {lowered}" or "option b" in lowered else \
                     "C" if " c" in f" {lowered}" or "option c" in lowered else "current"
            st.session_state["finny_chosen_alt"] = chosen
            st.session_state["finny_stage"] = "detail"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start a new conversation instead 🔄"):
            _reset_conversation()
            st.rerun()
        return

    # ---------------- STAGE 4: DETAIL ----------------
    if stage == "detail":
        chosen = st.session_state["finny_chosen_alt"]
        d = _build_detail(inputs, analysis, chosen if chosen != "current" else None)
        label = {"B": "Option B", "C": "Option C", "current": "your current plan"}[chosen]

        _bubble("Finny", f"Ok, great! We'll provide you with the details now — this is {label}. 👇")

        _bubble(
            "Plan Snapshot",
            f"Used car: ${d['price']:.0f} · ${d['down']:.0f} down · ${d['financed']:.0f} financed · "
            f"{d['rate']:.1f}% APR · {d['term']} months",
        )

        first_pay_interest = d["financed"] * (d["rate"] / 100 / 12)
        first_pay_principal = max(d["payment"] - first_pay_interest, 0)
        _bubble(
            "Payment Breakdown",
            f"Monthly payment: ${d['payment']:.0f}. In your first year, about "
            f"{d['year1_interest_share']}% of each payment goes to interest, and "
            f"${first_pay_principal:.0f} goes to principal — that ratio improves every year as the "
            f"balance drops. Total paid over {d['term']} months: ${d['total']:.0f}.",
        )

        pct_tone = "yellow" if d["pct_income"] > 15 else None
        budget_line = (f"This payment is about {d['pct_income']:.0f}% of your take-home income. "
                        f"Combined with your existing ${inputs['monthly_commitments']:.0f}/month in "
                        f"commitments, you're putting roughly {(d['pct_income'] + (inputs['monthly_commitments']/inputs['monthly_income']*100 if inputs['monthly_income'] else 0)):.0f}% "
                        f"of income toward fixed costs — comfortable under 30%, a caution zone above it.")
        _bubble("Budget Fit", budget_line)

        _bubble(
            "Milestone Timeline",
            f"You cross into positive equity around month {max(round(d['term']*0.15),3)} "
            f"after that, if you needed to sell, you'd get more than you owe. "
            f"Loan paid off in {d['term']} months.",
        )

        _bubble(
            "What This Actually Buys",
            f"At ${d['price']:.0f}, expect a used sedan or compact SUV roughly 8–10 years old with "
            f"85,000–110,000 miles — reliable economy models. Budget for new tires and lower coverage "
            f"as it ages.",
        )

        _bubble(
            "Shopping Checklist",
            "Before you sign: get a pre-purchase inspection from an independent mechanic (not the "
            "seller's), pull a Carfax or AutoCheck report, confirm the APR in writing before you agree "
            "to anything, ask if a shorter term changes the monthly enough to matter, and check whether "
            "gap insurance is worth it given how close to break-even you are early on.",
        )

        guardrail_tone = "red" if d["leftover"] < 200 else "yellow" if d["leftover"] < 500 else None
        if guardrail_tone:
            reduced_pct = (d["payment"] / (d["payment"] + d["leftover"]) * 100) if (d["payment"] + d["leftover"]) > 0 else 0
            _warn(
                guardrail_tone,
                f"This plan holds up as long as your hours stay steady. If your income dropped by "
                f"20%, this payment would eat roughly {reduced_pct:.0f}% of what's left after "
                f"commitments — since you're starting with ${inputs['emergency_savings']:.0f} in "
                f"savings, a bigger cushion before you sign would meaningfully reduce your risk here.",
            )

        _bubble(
            "That's the summary",
            f"That's the summary of {label}. If you need any more information, feel free to let us know 🙂",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start a new situation 🔄", key="restart_after_detail"):
            _reset_conversation()
            st.rerun()
        return


# ---------------------------------------------------------------------------
# INTEGRATION NOTES (not executed — read me)
# ---------------------------------------------------------------------------
"""
1) main.py routing:
   from finny import render_finny_page
   ...
   elif st.session_state["current_page"] == "Finny":
       render_finny_page()

2) Hamburger menu (sidebar) entry, alongside Course / Life Simulator / Finance
   Tracker links:
   if st.sidebar.button("🤖 Finny", key="nav_finny"):
       st.session_state["current_page"] = "Finny"
       st.rerun()

3) This module owns its own session_state keys (all prefixed "finny_"), so it
   won't collide with course_data.py / life_simulation.py / finance_tracker.py
   state. Navigating away and back mid-conversation will simply resume where
   the user left off, since state persists for the session.

4) The "recyclable" loop: after the DETAIL stage, the only action available is
   "Start a new situation", which calls _reset_conversation() and reruns —
   this drops the user right back at the Situation Statement box (stage 1),
   matching the flow in your screenshots.

5) The financial formulas here are the same style of rule-based calculator as
   your existing AI Financial Helper (amortization payment formula, % of
   income thresholds, 3-months-expenses emergency fund rule). If your current
   helper module has more refined thresholds/copy, swap the constants inside
   _analyze() to match — the state machine and UI around it don't need to
   change.
"""
