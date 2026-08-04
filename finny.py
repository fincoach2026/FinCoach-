"""
finny.py — FinCoach's AI Helper Bot ("Finny")

A recyclable, chat-style financial situation analyzer. Uses the app's
existing brand CSS (fc-card / fc-badge / fc-fade, --fc-* vars from
styles.py) so it matches dark mode and every other page automatically.

Flow:
  1) SITUATION   -> user types a free-text situation statement
  2) COLLECTING  -> Finny welcomes them + asks for structured financial inputs
  3) ANALYSIS    -> Finny returns verdict, budget impact, total cost, color-coded
                     warnings, and 2 alternatives (Option B / Option C)
  4) DETAIL      -> if the user picks an alternative / asks for more, Finny
                     returns a deeper breakdown (payment breakdown, budget fit,
                     milestone timeline, what-it-buys, checklist, guardrail)
  5) -> resets back to SITUATION for a brand-new conversation

Called from main.py's router the same way render_tracker() / render_help() /
render_profile() are — top_bar() is invoked by the router before this runs,
not inside this file, to match that convention.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Scoped CSS: everything here rides on the --fc-* vars already injected by
# styles.get_css(), so it inherits dark mode for free. Only the warning tint
# colors (red/yellow) are new — they're functional alert colors, not brand
# chrome, so they sit outside the strict palette on purpose.
# ---------------------------------------------------------------------------
FINNY_CSS = """
<style>
.fc-finny-verdict {
    background: linear-gradient(135deg, var(--fc-primary), var(--fc-secondary));
    color: #ffffff !important;
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
.fc-finny-verdict p, .fc-finny-verdict b, .fc-finny-verdict div {
    color: #ffffff !important;
}
.fc-finny-warn-red {
    background: rgba(224,91,91,0.14);
    border-left: 5px solid #E05B5B;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.fc-finny-warn-yellow {
    background: rgba(224,185,77,0.16);
    border-left: 5px solid #E0B94D;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.fc-finny-warn-red p, .fc-finny-warn-yellow p {
    margin: 0;
    color: var(--fc-text) !important;
}
.fc-finny-alt-card {
    background: var(--fc-card-bg);
    border: 1.5px solid var(--fc-highlight);
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.fc-finny-alt-card b, .fc-finny-alt-card p {
    color: var(--fc-text) !important;
}
</style>
"""


# ---------------------------------------------------------------------------
# STATE MACHINE HELPERS (all keys prefixed finny_ so they never collide with
# course/tracker/life-sim state)
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
# CORE FINANCIAL LOGIC (rule-based, no external calls — same style as your
# other calculators: amortization payment formula, % of income thresholds,
# 3-months-expenses emergency fund rule)
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

    # Verdict
    if pct_income <= 15 and leftover > 0:
        verdict = "This is a comfortable, low-risk plan for your income level."
    elif pct_income <= 20 and leftover > 0:
        verdict = "This is tight, not impossible. A missed shift or slow month would put you behind."
    else:
        verdict = "This plan is high-risk right now — the payment eats too much of your income."

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
                                  f"${max(leftover, 0):.0f}/month left for food, gas, insurance, and "
                                  f"everything else."))
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
    alt_b_down = min(down + (income - commitments) * 0.5 * 6, car_price)  # save ~half of leftover for 6mo
    alt_b_loan = max(car_price - alt_b_down, 0)
    alt_b_payment = _monthly_payment(alt_b_loan, rate, term)
    alt_b_total = alt_b_payment * term + alt_b_down
    interest_saved_b = total_paid - alt_b_total

    alt_c_price = round(car_price * 0.75, -2)  # ~25% cheaper car
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
        "verdict": verdict,
        "warnings": warnings,
        "alt_b": {"down": alt_b_down, "payment": alt_b_payment, "total": alt_b_total,
                   "interest_saved": interest_saved_b},
        "alt_c": {"price": alt_c_price, "payment": alt_c_payment, "total": alt_c_total,
                   "payment_drop": payment - alt_c_payment},
    }


def _build_detail(inputs, analysis, chosen):
    """Deeper breakdown for the chosen plan (current / Option B / Option C)."""
    income = inputs["monthly_income"]
    commitments = inputs["monthly_commitments"]
    term = inputs["loan_term"]
    rate = inputs["interest_rate"]

    if chosen == "B":
        price, down = inputs["car_price"], analysis["alt_b"]["down"]
        payment, total = analysis["alt_b"]["payment"], analysis["alt_b"]["total"]
    elif chosen == "C":
        price, down = analysis["alt_c"]["price"], inputs["down_payment"]
        payment, total = analysis["alt_c"]["payment"], analysis["alt_c"]["total"]
    else:
        price, down = inputs["car_price"], inputs["down_payment"]
        payment, total = analysis["payment"], analysis["total_paid"]

    financed = max(price - down, 0)
    pct_income = (payment / income * 100) if income > 0 else 0
    leftover = income - commitments - payment

    return {
        "price": price, "down": down, "payment": payment, "total": total,
        "financed": financed, "pct_income": pct_income, "term": term, "rate": rate,
        "leftover": leftover,
    }


# ---------------------------------------------------------------------------
# RENDER HELPERS
# ---------------------------------------------------------------------------
def _bubble(title, body_html):
    st.markdown(
        f"<div class='fc-card fc-fade' style='margin-bottom:12px;'>"
        f"<h4 style='margin-top:0;'>{title}</h4><p style='margin-bottom:0;'>{body_html}</p></div>",
        unsafe_allow_html=True,
    )


def _warn(tone, text):
    cls = "fc-finny-warn-red" if tone == "red" else "fc-finny-warn-yellow"
    icon = "🔴" if tone == "red" else "🟡"
    st.markdown(f"<div class='{cls}'><p>{icon} {text}</p></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# MAIN PAGE ENTRY POINT
# main.py's router should call: top_bar(show_nav=True, show_menu=True); render_finny_page()
# (same pattern as render_tracker() / render_help() / render_profile())
# ---------------------------------------------------------------------------
def render_finny_page():
    st.markdown(FINNY_CSS, unsafe_allow_html=True)
    _init_state()

    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>AI HELPER</span>"
        "<h1>Finny — Your AI Money Helper</h1></div>",
        unsafe_allow_html=True,
    )

    stage = st.session_state["finny_stage"]

    # ---------------- STAGE 1: SITUATION ----------------
    if stage == "situation":
        st.markdown("<p style='font-weight:600;'>Situation Statement:</p>", unsafe_allow_html=True)
        situation = st.text_area(
            "situation_input",
            placeholder="I'm 19, making $18/hour, and I'm thinking about financing a used car.",
            label_visibility="collapsed",
            key="finny_situation_box",
        )
        if st.button("Send ➤", key="finny_send_situation"):
            if situation.strip():
                st.session_state["finny_situation"] = situation.strip()
                st.session_state["finny_stage"] = "collecting"
                st.rerun()
            else:
                st.warning("Tell Finny a bit about your situation first.")
        return

    # Show the situation statement as the top of the "conversation"
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
            submitted = st.form_submit_button("Get My Analysis ➤", use_container_width=True)

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

        st.markdown(
            f"<div class='fc-finny-verdict'><b>Verdict</b><p>{analysis['verdict']}</p></div>",
            unsafe_allow_html=True,
        )

        _bubble(
            "Monthly Budget Impact",
            f"Your payment would be about <b>${analysis['payment']:.0f}/month</b> — that's "
            f"<b>{analysis['pct_income']:.0f}%</b> of your take-home income. After setting that aside, "
            f"you'd have roughly <b>${max(analysis['leftover'], 0):.0f}/month</b> left for food, gas, "
            f"insurance, and everything else.",
        )

        term = inputs["loan_term"]
        _bubble(
            "Total Cost Over Time",
            f"Car price: ${inputs['car_price']:.0f}. Total over {term} months: "
            f"${analysis['total_paid']:.0f}. Total interest: ${analysis['total_interest']:.0f} — "
            f"{(analysis['total_interest'] / inputs['car_price'] * 100 if inputs['car_price'] else 0):.0f}% "
            f"more than the car itself.",
        )

        st.markdown("<p style='font-weight:700; margin-top:8px;'>⚠ Watch Out For:</p>", unsafe_allow_html=True)
        for tone, text in analysis["warnings"]:
            _warn(tone, text)

        st.markdown("<p style='font-weight:700; margin-top:8px;'>Alternatives:</p>", unsafe_allow_html=True)

        b = analysis["alt_b"]
        st.markdown(
            f"<div class='fc-finny-alt-card'><b>Option B</b> — Wait 6 months, save a bigger down payment.<br>"
            f"Impact: Payment drops to about ${b['payment']:.0f}/month. Total interest drops to about "
            f"${(b['total'] - inputs['car_price'] if inputs['car_price'] else 0):.0f} — saves you "
            f"~${b['interest_saved']:.0f} over the life of the loan.</div>",
            unsafe_allow_html=True,
        )
        c = analysis["alt_c"]
        st.markdown(
            f"<div class='fc-finny-alt-card'><b>Option C</b> — Same down payment, ${c['price']:.0f} car "
            f"instead.<br>Impact: Payment drops to about ${c['payment']:.0f}/month — cuts your "
            f"negative-equity risk almost entirely by month 6.</div>",
            unsafe_allow_html=True,
        )

        _bubble(
            "Summary",
            "This is the overall summary based on your situation and goal. If you'd like a full plan "
            "for an alternative option, pick one below. If you're ready as-is, we'll finalize your "
            "current plan. We'll always make sure you have all the details you need! 🙂",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Continue with current plan", key="finny_pick_current", use_container_width=True):
                st.session_state["finny_chosen_alt"] = "current"
                st.session_state["finny_stage"] = "detail"
                st.rerun()
        with col2:
            if st.button("I want Option B", key="finny_pick_b", use_container_width=True):
                st.session_state["finny_chosen_alt"] = "B"
                st.session_state["finny_stage"] = "detail"
                st.rerun()
        with col3:
            if st.button("I want Option C", key="finny_pick_c", use_container_width=True):
                st.session_state["finny_chosen_alt"] = "C"
                st.session_state["finny_stage"] = "detail"
                st.rerun()

        free_text = st.text_input(
            "Or tell Finny what you'd like next",
            placeholder="I want to continue with option C",
            key="finny_analysis_free_text",
        )
        if st.button("Send ➤", key="finny_analysis_free_text_send") and free_text.strip():
            lowered = f" {free_text.lower()} "
            chosen = "B" if "option b" in lowered or " b " in lowered else \
                     "C" if "option c" in lowered or " c " in lowered else "current"
            st.session_state["finny_chosen_alt"] = chosen
            st.session_state["finny_stage"] = "detail"
            st.rerun()

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("Start a new conversation instead 🔄", key="finny_restart_from_analysis"):
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
            f"Monthly payment: ${d['payment']:.0f}. Early in the loan, more of each payment goes to "
            f"interest (about ${first_pay_interest:.0f} of your first payment) than principal (about "
            f"${first_pay_principal:.0f}) — that ratio improves every year as the balance drops. "
            f"Total paid over {d['term']} months: ${d['total']:.0f}.",
        )

        combined_pct = d["pct_income"] + (
            inputs["monthly_commitments"] / inputs["monthly_income"] * 100 if inputs["monthly_income"] else 0
        )
        _bubble(
            "Budget Fit",
            f"This payment is about {d['pct_income']:.0f}% of your take-home income. Combined with your "
            f"existing ${inputs['monthly_commitments']:.0f}/month in commitments, you're putting roughly "
            f"{combined_pct:.0f}% of income toward fixed costs — comfortable under 30%, a caution zone "
            f"above it.",
        )

        _bubble(
            "Milestone Timeline",
            f"You cross into positive equity around month {max(round(d['term'] * 0.15), 3)} — after "
            f"that, if you needed to sell, you'd get more than you owe. Loan paid off in {d['term']} months.",
        )

        _bubble(
            "What This Actually Buys",
            f"At ${d['price']:.0f}, expect a used sedan or compact SUV roughly 8–10 years old with "
            f"85,000–110,000 miles — reliable economy models. Budget for new tires and a bit more "
            f"maintenance as it ages.",
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

        _bubble("That's the summary", f"That's the summary of {label}. If you need any more information, feel free to let us know 🙂")

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("Start a new situation 🔄", key="finny_restart_from_detail"):
            _reset_conversation()
            st.rerun()
        return
