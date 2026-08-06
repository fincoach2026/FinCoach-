"""
finny.py — FinCoach's AI Helper Bot ("Finny")

A recyclable, chat-style financial situation analyzer, now with:
  - a mini sidebar (left column) listing every saved conversation, a
    "+ New chat" button, and a delete button per conversation
  - inputs you can skip ("✕ Skip") if you don't have that number handy —
    skipped fields disappear from THIS conversation's form, but every new
    conversation always starts with every field showing again
  - an actual LLM understanding layer (see finny_llm.py): Finny checks
    whether your situation statement is real before it ever shows you the
    input form, and reads your free-text replies with real comprehension
    instead of `"option b" in text` string matching

Uses the app's existing brand CSS (fc-card / fc-badge / fc-fade, --fc-*
vars from styles.py) so it matches dark mode and every other page
automatically.

Flow:
  1) SITUATION   -> user types a free-text situation statement
  2) CLARIFY     -> only if Finny can't make sense of it yet (e.g. "bla bla
                     bla") — Finny asks a short follow-up instead of guessing
  3) COLLECTING  -> Finny welcomes them + asks for structured financial
                     inputs (any of which can be skipped)
  4) ANALYSIS    -> Finny returns verdict, budget impact, total cost,
                     color-coded warnings, and 2 alternatives (Option B / C)
  5) DETAIL      -> if the user picks an alternative / asks for more, Finny
                     returns a deeper breakdown
  6) -> "+ New chat" starts a brand-new conversation alongside the old one
        in the sidebar (nothing is overwritten)

Persistence: every conversation is saved to finny_data.json (same pattern
as tracker_data.json / sim_data.json) so the sidebar survives a refresh or
app restart, not just a single session.

Called from main.py's router the same way render_tracker() / render_help()
/ render_profile() are — top_bar() is invoked by the router before this
runs, not inside this file, to match that convention.
"""

import json
import os
import uuid
from datetime import datetime, timezone

import streamlit as st

from finny_llm import ask_finny_json

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
.fc-finny-sidebar {
    background: var(--fc-card-bg);
    border: 1.5px solid var(--fc-highlight);
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 12px;
}
.fc-finny-sidebar-list {
    max-height: 60vh;
    overflow-y: auto;
    margin-top: 8px;
}
.fc-finny-sidebar-empty {
    color: var(--fc-text);
    opacity: 0.6;
    font-size: 0.85rem;
    padding: 6px 2px;
}
.fc-finny-skip-chip {
    background: var(--fc-card-bg);
    border: 1.5px dashed var(--fc-highlight);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    color: var(--fc-text);
    opacity: 0.75;
    font-size: 0.9rem;
}
</style>
"""

FINNY_DATA_PATH = "finny_data.json"

# Every structured input field Finny can ask for. `skippable=False` fields
# (just car price) are required because there's nothing to analyze without
# them; everything else can be skipped with "✕ Skip" and Finny will note
# the assumption it made instead.
FIELDS = [
    {"key": "monthly_income", "label": "Monthly Income ($)", "step": 50.0, "skippable": True},
    {"key": "monthly_commitments", "label": "Monthly Commitments (rent, etc.) ($)", "step": 25.0, "skippable": True},
    {"key": "emergency_savings", "label": "Emergency Savings ($)", "step": 50.0, "skippable": True},
    {"key": "car_price", "label": "Car Price ($)", "step": 100.0, "skippable": False},
    {"key": "down_payment", "label": "Down Payment Available ($)", "step": 100.0, "skippable": True},
    {"key": "interest_rate", "label": "Estimated Interest Rate (%)", "step": 0.1, "skippable": True},
    {"key": "loan_term", "label": "Loan Term (months)", "step": 1, "skippable": True, "default": 60, "is_int": True},
]

DEFAULT_WELCOME = (
    "Hey! I'll be more than happy to provide analysis and a plan to help you "
    "reach your financial goal based on your situation. Fill in the fields "
    "below so I can give you the best advice possible 🙂"
)


# ---------------------------------------------------------------------------
# LLM UNDERSTANDING LAYER
# These two functions are Finny's "brain" for free text. Both call the
# Claude API (via finny_llm.ask_finny_json) and fall back to a simple
# rule-based heuristic if no API key is configured — see finny_llm.py.
# ---------------------------------------------------------------------------
SITUATION_SYSTEM_PROMPT = """You are Finny, the AI money helper inside FinCoach, an app that teaches \
young adults about personal finance. A user just typed a free-text "situation statement" describing a \
financial decision they're facing (usually about financing/buying a used car, but treat it generally). \
Your ONLY job right now is to decide whether you understand it well enough to ask for numbers next — \
you are not analyzing anything yet, and you are not giving advice yet.

Reply with ONLY a JSON object, no other text, in exactly this shape:
{
  "understood": true or false,
  "welcome_message": "a warm 1-2 sentence welcome that references something specific they said" or null,
  "clarify_question": "one short, friendly follow-up question asking for the missing context" or null
}

Rules:
- If the text is gibberish, keysmashing, empty of real content, or otherwise gives you nothing to work
  with (e.g. "bla bla bla", "asdkjf", a single unrelated word), set understood=false, welcome_message=null,
  and ask ONE short clarifying question in clarify_question.
- If the text describes a real (even vague or incomplete) financial situation or decision, set
  understood=true, write a specific welcome_message that shows you actually read what they wrote, and
  set clarify_question=null.
- Never lecture and never give financial advice here — that comes later. Keep welcome_message to 1-2
  sentences.
- Output valid JSON only. No markdown code fences, no commentary before or after."""


def understand_situation(text):
    result = ask_finny_json(SITUATION_SYSTEM_PROMPT, text)
    if isinstance(result, dict) and "understood" in result:
        result.setdefault("welcome_message", None)
        result.setdefault("clarify_question", None)
        return result
    return _fallback_understand_situation(text)


def _fallback_understand_situation(text):
    """Used only when no ANTHROPIC_API_KEY is configured. Deliberately
    conservative: needs a handful of distinct real words before it'll treat
    the statement as understood, so "bla bla bla" / keysmashes still get
    caught even without the LLM."""
    words = [w.strip(".,!?;:").lower() for w in text.split() if w.strip(".,!?;:")]
    unique_words = set(words)
    looks_real = len(words) >= 4 and len(unique_words) >= 3 and any(c.isalpha() for c in text)
    if looks_real:
        return {"understood": True, "welcome_message": DEFAULT_WELCOME, "clarify_question": None}
    return {
        "understood": False,
        "welcome_message": None,
        "clarify_question": (
            "I want to make sure I get this right before we dive into numbers — can you tell me a bit "
            "more? For example, your age or income, and what you're thinking about buying or financing."
        ),
    }


def interpret_choice(text, analysis):
    system_prompt = f"""You are Finny, an AI money helper. The user was just shown three options after \
seeing a car-financing analysis:
- "current": their original plan, payment about ${analysis['payment']:.0f}/month
- "B": wait & save a bigger down payment, payment about ${analysis['alt_b']['payment']:.0f}/month
- "C": a cheaper car (about ${analysis['alt_c']['price']:.0f}), payment about ${analysis['alt_c']['payment']:.0f}/month

The user just typed a free-text reply. Classify it and reply with ONLY this JSON, no other text:
{{
  "choice": "current" or "B" or "C" or "other",
  "reply": "a short, direct, genuinely helpful response" or null
}}

Use "other" if they're asking a question, raising a new constraint, or anything that isn't clearly \
picking one of the three options. When choice is "other", write a short, actually helpful reply in \
"reply" that responds to what they said (don't just repeat the three buttons at them unless that really \
is the most helpful response). When choice is current/B/C, set "reply" to null.
Output valid JSON only. No markdown code fences."""
    result = ask_finny_json(system_prompt, text)
    if isinstance(result, dict) and result.get("choice") in ("current", "B", "C", "other"):
        result.setdefault("reply", None)
        return result
    return _fallback_interpret_choice(text)


def _fallback_interpret_choice(text):
    lowered = f" {text.lower()} "
    if "option b" in lowered or " b " in lowered:
        return {"choice": "B", "reply": None}
    if "option c" in lowered or " c " in lowered:
        return {"choice": "C", "reply": None}
    if any(w in lowered for w in (" current ", " keep ", " stick ", "as-is", "as is")):
        return {"choice": "current", "reply": None}
    return {
        "choice": "other",
        "reply": (
            "I'm not totally sure which way you want to go — tap one of the three buttons above "
            "(current plan, Option B, or Option C), or tell me a bit more about what you're thinking."
        ),
    }


# ---------------------------------------------------------------------------
# CONVERSATION STORE (persisted to finny_data.json, mirrored in
# st.session_state while the app is running)
# ---------------------------------------------------------------------------
def _load_store():
    if "finny_store" not in st.session_state:
        store = {"conversations": {}, "active_id": None}
        if os.path.exists(FINNY_DATA_PATH):
            try:
                with open(FINNY_DATA_PATH, "r") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict) and "conversations" in loaded:
                    store = loaded
            except Exception:
                pass
        st.session_state["finny_store"] = store
    return st.session_state["finny_store"]


def _save_store(store):
    st.session_state["finny_store"] = store
    try:
        with open(FINNY_DATA_PATH, "w") as f:
            json.dump(store, f, indent=2)
    except Exception:
        # Non-fatal — some hosts have a read-only filesystem. The
        # conversation still works for the rest of this session either way.
        pass


def _new_conversation_dict():
    return {
        "id": str(uuid.uuid4()),
        "title": "New chat",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stage": "situation",
        "situation": "",
        "welcome_message": None,
        "clarify_question": None,
        "inputs": {},
        "skipped_fields": [],  # always starts empty for a new conversation
        "analysis": None,
        "chosen_alt": None,
        "free_text_note": None,
    }


def _make_title(text):
    first_line = text.strip().split("\n")[0].strip()
    return (first_line[:42] + "…") if len(first_line) > 42 else (first_line or "New chat")


def _create_new_chat(store):
    conv = _new_conversation_dict()
    store["conversations"][conv["id"]] = conv
    store["active_id"] = conv["id"]
    _save_store(store)
    return conv


def _delete_chat(store, conv_id):
    store["conversations"].pop(conv_id, None)
    if store.get("active_id") == conv_id:
        remaining = sorted(store["conversations"].values(), key=lambda c: c["created_at"], reverse=True)
        store["active_id"] = remaining[0]["id"] if remaining else None
    _save_store(store)


# ---------------------------------------------------------------------------
# CORE FINANCIAL LOGIC (rule-based, no external calls — same style as your
# other calculators: amortization payment formula, % of income thresholds,
# 3-months-expenses emergency fund rule). Every input is now optional except
# car_price, so this is written to degrade gracefully when a field is None.
# ---------------------------------------------------------------------------
def _monthly_payment(principal, annual_rate_pct, term_months):
    if principal <= 0 or term_months <= 0:
        return 0.0
    r = (annual_rate_pct / 100) / 12
    if r == 0:
        return principal / term_months
    return principal * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)


def _analyze(inputs):
    income = inputs.get("monthly_income")
    commitments = inputs.get("monthly_commitments")
    emergency = inputs.get("emergency_savings")
    car_price = inputs.get("car_price") or 0
    down = inputs.get("down_payment") or 0

    rate = inputs.get("interest_rate")
    rate_assumed = rate is None
    if rate_assumed:
        rate = 8.0  # typical used-auto-loan rate, used only as a placeholder

    term = inputs.get("loan_term") or 60

    loan_amount = max(car_price - down, 0)
    payment = _monthly_payment(loan_amount, rate, term)
    total_paid = payment * term + down
    total_interest = max(total_paid - car_price, 0)

    pct_income = (payment / income * 100) if income else None
    leftover = (income - (commitments or 0) - payment) if income is not None else None

    # Verdict
    if pct_income is None:
        verdict = "Finny can only give you a partial picture without your income — here's the math on the loan itself."
    elif pct_income <= 15 and (leftover is None or leftover > 0):
        verdict = "This is a comfortable, low-risk plan for your income level."
    elif pct_income <= 20 and (leftover is None or leftover > 0):
        verdict = "This is tight, not impossible. A missed shift or slow month would put you behind."
    else:
        verdict = "This plan is high-risk right now — the payment eats too much of your income."

    # Warnings
    warnings = []
    if pct_income is not None:
        if pct_income > 20:
            warnings.append(("red", f"Your payment would be about {pct_income:.0f}% of your take-home "
                                      f"income — that's above the recommended 15–20% ceiling for a car payment."))
        elif pct_income > 15:
            warnings.append(("yellow", f"Your payment would be about {pct_income:.0f}% of your take-home "
                                         f"income — on the higher end of the recommended range."))
    if leftover is not None:
        if leftover < 200:
            warnings.append(("red", f"After commitments and this payment, you'd have roughly "
                                      f"${max(leftover, 0):.0f}/month left for food, gas, insurance, and "
                                      f"everything else."))
        elif leftover < 500:
            warnings.append(("yellow", f"After commitments and this payment, you'd have roughly ${leftover:.0f}/month "
                                         f"of breathing room — enough for essentials, but little cushion."))
    if emergency is not None:
        monthly_expenses_est = (commitments or 0) + payment
        if emergency < monthly_expenses_est * 3:
            warnings.append(("yellow", f"Your emergency savings (${emergency:.0f}) cover less than 3 months of your "
                                         f"new commitments — worth building that up before or alongside this purchase."))
    if not rate_assumed and rate >= 10:
        warnings.append(("yellow", f"A {rate:.1f}% interest rate is on the higher side — even a modest credit "
                                     f"improvement could lower your total cost noticeably."))

    # Notes about anything the user skipped, so Finny is upfront about what
    # it had to assume rather than quietly pretending it has full context.
    if rate_assumed:
        warnings.append(("yellow", "You skipped interest rate, so Finny assumed a typical 8% used-auto rate "
                                     "for this estimate — your real number could raise or lower the payment."))
    if income is None:
        warnings.append(("yellow", "You skipped monthly income, so Finny can't tell you what share of your "
                                     "income this payment eats or confirm it's really affordable."))
    if commitments is None and income is not None:
        warnings.append(("yellow", "You skipped monthly commitments, so the leftover-money estimate above only "
                                     "accounts for this payment, not your rent or other bills."))
    if emergency is None:
        warnings.append(("yellow", "You skipped emergency savings, so Finny couldn't check your safety cushion "
                                     "against this new payment."))

    # Alternatives — fall back to a flat assumption when income is unknown
    # so these still produce something useful either way.
    if income is not None:
        extra_savings = max((income - (commitments or 0)), 0) * 0.5 * 6  # ~half of leftover for 6mo
    else:
        extra_savings = car_price * 0.10  # generic fallback: ~10% of price saved over 6mo

    alt_b_down = min(down + extra_savings, car_price)
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
        "rate_used": rate,
        "rate_assumed": rate_assumed,
        "alt_b": {"down": alt_b_down, "payment": alt_b_payment, "total": alt_b_total,
                   "interest_saved": interest_saved_b},
        "alt_c": {"price": alt_c_price, "payment": alt_c_payment, "total": alt_c_total,
                   "payment_drop": payment - alt_c_payment},
    }


def _build_detail(inputs, analysis, chosen):
    """Deeper breakdown for the chosen plan (current / Option B / Option C)."""
    income = inputs.get("monthly_income")
    commitments = inputs.get("monthly_commitments") or 0
    term = inputs.get("loan_term") or 60
    rate = analysis["rate_used"]

    if chosen == "B":
        price, down = inputs.get("car_price") or 0, analysis["alt_b"]["down"]
        payment, total = analysis["alt_b"]["payment"], analysis["alt_b"]["total"]
    elif chosen == "C":
        price, down = analysis["alt_c"]["price"], inputs.get("down_payment") or 0
        payment, total = analysis["alt_c"]["payment"], analysis["alt_c"]["total"]
    else:
        price, down = inputs.get("car_price") or 0, inputs.get("down_payment") or 0
        payment, total = analysis["payment"], analysis["total_paid"]

    financed = max(price - down, 0)
    pct_income = (payment / income * 100) if income else None
    leftover = (income - commitments - payment) if income is not None else None

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
# SIDEBAR
# ---------------------------------------------------------------------------
def _render_finny_sidebar(store):
    st.markdown("<div class='fc-finny-sidebar'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; margin:0 0 6px 0;'>Conversations</p>", unsafe_allow_html=True)

    if st.button("＋ New chat", key="finny_new_chat_btn", use_container_width=True):
        _create_new_chat(store)
        st.rerun()

    st.markdown("<div class='fc-finny-sidebar-list'>", unsafe_allow_html=True)
    convs = sorted(store["conversations"].values(), key=lambda c: c["created_at"], reverse=True)

    if not convs:
        st.markdown("<p class='fc-finny-sidebar-empty'>No conversations yet</p>", unsafe_allow_html=True)

    for conv in convs:
        is_active = conv["id"] == store.get("active_id")
        row1, row2 = st.columns([5, 1])
        with row1:
            if st.button(
                ("👉 " if is_active else "") + conv["title"],
                key=f"finny_switch_{conv['id']}",
                use_container_width=True,
            ):
                store["active_id"] = conv["id"]
                _save_store(store)
                st.rerun()
        with row2:
            if st.button("🗑", key=f"finny_delete_{conv['id']}", help="Delete this conversation"):
                _delete_chat(store, conv["id"])
                st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# STAGE RENDERERS
# ---------------------------------------------------------------------------
def _stage_situation(store, conv):
    st.markdown("<p style='font-weight:600;'>Situation Statement:</p>", unsafe_allow_html=True)
    situation = st.text_area(
        "situation_input",
        placeholder="I'm 19, making $18/hour, and I'm thinking about financing a used car.",
        label_visibility="collapsed",
        key=f"finny_situation_box_{conv['id']}",
    )
    if st.button("Send ➤", key=f"finny_send_situation_{conv['id']}"):
        if not situation.strip():
            st.warning("Tell Finny a bit about your situation first.")
            return
        with st.spinner("Finny is reading your situation..."):
            understanding = understand_situation(situation.strip())
        conv["situation"] = situation.strip()
        conv["title"] = _make_title(situation.strip())
        if understanding["understood"]:
            conv["stage"] = "collecting"
            conv["welcome_message"] = understanding["welcome_message"]
        else:
            conv["stage"] = "clarify"
            conv["clarify_question"] = understanding["clarify_question"]
        _save_store(store)
        st.rerun()


def _stage_clarify(store, conv):
    _bubble("You said:", conv["situation"])
    _bubble("Finny", conv["clarify_question"])

    reply = st.text_input(
        "Your reply",
        placeholder="Add a bit more detail...",
        label_visibility="collapsed",
        key=f"finny_clarify_reply_{conv['id']}",
    )
    col1, col2 = st.columns([3, 1])
    send = col1.button("Send ➤", key=f"finny_clarify_send_{conv['id']}", use_container_width=True)
    restart = col2.button("Start over 🔄", key=f"finny_clarify_restart_{conv['id']}", use_container_width=True)

    if restart:
        conv["stage"] = "situation"
        conv["situation"] = ""
        conv["clarify_question"] = None
        _save_store(store)
        st.rerun()

    if send and reply.strip():
        combined = f"{conv['situation']}\n\nMore detail: {reply.strip()}"
        with st.spinner("Finny is reading..."):
            understanding = understand_situation(combined)
        conv["situation"] = combined
        conv["title"] = _make_title(combined)
        if understanding["understood"]:
            conv["stage"] = "collecting"
            conv["welcome_message"] = understanding["welcome_message"]
        else:
            conv["clarify_question"] = understanding["clarify_question"]
        _save_store(store)
        st.rerun()


def _stage_collecting(store, conv):
    _bubble("Finny", conv.get("welcome_message") or DEFAULT_WELCOME)

    skipped = set(conv.get("skipped_fields", []))
    values = dict(conv.get("inputs", {}))

    for field in FIELDS:
        key = field["key"]

        if key in skipped:
            chip_col, undo_col = st.columns([5, 1])
            with chip_col:
                st.markdown(f"<div class='fc-finny-skip-chip'>{field['label']} — skipped</div>",
                            unsafe_allow_html=True)
            with undo_col:
                if st.button("+ Add back", key=f"finny_addback_{conv['id']}_{key}"):
                    skipped.discard(key)
                    conv["skipped_fields"] = list(skipped)
                    _save_store(store)
                    st.rerun()
            continue

        input_col, skip_col = st.columns([5, 1])
        with input_col:
            if field.get("is_int"):
                val = st.number_input(
                    field["label"], min_value=1, step=int(field["step"]),
                    value=int(values.get(key) or field.get("default", 1)),
                    key=f"finny_field_{conv['id']}_{key}",
                )
            else:
                val = st.number_input(
                    field["label"], min_value=0.0, step=field["step"],
                    value=float(values.get(key) or 0.0),
                    key=f"finny_field_{conv['id']}_{key}",
                )
        values[key] = val

        if field["skippable"]:
            with skip_col:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("✕ Skip", key=f"finny_skip_{conv['id']}_{key}", help="I don't have this info"):
                    skipped.add(key)
                    conv["skipped_fields"] = list(skipped)
                    conv["inputs"] = values
                    _save_store(store)
                    st.rerun()

    conv["inputs"] = values
    _save_store(store)

    if st.button("Get My Analysis ➤", key=f"finny_submit_inputs_{conv['id']}", use_container_width=True):
        final_inputs = {
            f["key"]: (values.get(f["key"]) if f["key"] not in skipped else None) for f in FIELDS
        }
        if not final_inputs.get("car_price"):
            st.warning("Finny needs at least the car price to run any numbers.")
            return
        conv["inputs"] = final_inputs
        conv["analysis"] = _analyze(final_inputs)
        conv["stage"] = "analysis"
        _save_store(store)
        st.rerun()


def _stage_analysis(store, conv, inputs, analysis):
    _bubble("Finny", "Thanks for the response. Here's your analysis right now 👇")

    st.markdown(
        f"<div class='fc-finny-verdict'><b>Verdict</b><p>{analysis['verdict']}</p></div>",
        unsafe_allow_html=True,
    )

    if analysis["pct_income"] is not None:
        budget_body = (
            f"Your payment would be about <b>${analysis['payment']:.0f}/month</b> — that's "
            f"<b>{analysis['pct_income']:.0f}%</b> of your take-home income. "
        )
        if analysis["leftover"] is not None:
            budget_body += (
                f"After setting that aside, you'd have roughly "
                f"<b>${max(analysis['leftover'], 0):.0f}/month</b> left for food, gas, insurance, and "
                f"everything else."
            )
    else:
        budget_body = (
            f"Your payment would be about <b>${analysis['payment']:.0f}/month</b>. Finny couldn't check "
            f"this against your income since that field was skipped — see the note below."
        )
    _bubble("Monthly Budget Impact", budget_body)

    term = inputs.get("loan_term") or 60
    car_price = inputs.get("car_price") or 0
    _bubble(
        "Total Cost Over Time",
        f"Car price: ${car_price:.0f}. Total over {term} months: "
        f"${analysis['total_paid']:.0f}. Total interest: ${analysis['total_interest']:.0f} — "
        f"{(analysis['total_interest'] / car_price * 100 if car_price else 0):.0f}% "
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
        f"${(b['total'] - car_price if car_price else 0):.0f} — saves you "
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
        if st.button("Continue with current plan", key=f"finny_pick_current_{conv['id']}", use_container_width=True):
            conv["chosen_alt"] = "current"
            conv["stage"] = "detail"
            _save_store(store)
            st.rerun()
    with col2:
        if st.button("I want Option B", key=f"finny_pick_b_{conv['id']}", use_container_width=True):
            conv["chosen_alt"] = "B"
            conv["stage"] = "detail"
            _save_store(store)
            st.rerun()
    with col3:
        if st.button("I want Option C", key=f"finny_pick_c_{conv['id']}", use_container_width=True):
            conv["chosen_alt"] = "C"
            conv["stage"] = "detail"
            _save_store(store)
            st.rerun()

    free_text = st.text_input(
        "Or tell Finny what you'd like next",
        placeholder="I want to continue with option C",
        key=f"finny_analysis_free_text_{conv['id']}",
    )
    if st.button("Send ➤", key=f"finny_analysis_free_text_send_{conv['id']}") and free_text.strip():
        with st.spinner("Finny is thinking..."):
            decision = interpret_choice(free_text.strip(), analysis)
        if decision["choice"] in ("current", "B", "C"):
            conv["chosen_alt"] = decision["choice"]
            conv["stage"] = "detail"
            conv["free_text_note"] = None
        else:
            conv["free_text_note"] = decision["reply"]
        _save_store(store)
        st.rerun()

    if conv.get("free_text_note"):
        _bubble("Finny", conv["free_text_note"])

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if st.button("Start a new conversation instead 🔄", key=f"finny_restart_from_analysis_{conv['id']}"):
        _create_new_chat(store)
        st.rerun()


def _stage_detail(store, conv, inputs, analysis):
    chosen = conv["chosen_alt"]
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

    if d["pct_income"] is not None:
        commitments = inputs.get("monthly_commitments") or 0
        income = inputs.get("monthly_income")
        combined_pct = d["pct_income"] + (commitments / income * 100 if income else 0)
        _bubble(
            "Budget Fit",
            f"This payment is about {d['pct_income']:.0f}% of your take-home income. Combined with your "
            f"existing ${commitments:.0f}/month in commitments, you're putting roughly "
            f"{combined_pct:.0f}% of income toward fixed costs — comfortable under 30%, a caution zone "
            f"above it.",
        )
    else:
        _bubble(
            "Budget Fit",
            "Finny can't score this against your budget since monthly income was skipped — add it back "
            "in a new conversation any time you want that check.",
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

    if d["leftover"] is not None:
        guardrail_tone = "red" if d["leftover"] < 200 else "yellow" if d["leftover"] < 500 else None
        if guardrail_tone:
            reduced_pct = (d["payment"] / (d["payment"] + d["leftover"]) * 100) if (d["payment"] + d["leftover"]) > 0 else 0
            emergency = inputs.get("emergency_savings")
            savings_note = f"${emergency:.0f}" if emergency is not None else "an unknown amount of"
            _warn(
                guardrail_tone,
                f"This plan holds up as long as your hours stay steady. If your income dropped by "
                f"20%, this payment would eat roughly {reduced_pct:.0f}% of what's left after "
                f"commitments — since you're starting with {savings_note} in savings, a bigger "
                f"cushion before you sign would meaningfully reduce your risk here.",
            )

    _bubble("That's the summary", f"That's the summary of {label}. If you need any more information, feel free to let us know 🙂")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if st.button("Start a new situation 🔄", key=f"finny_restart_from_detail_{conv['id']}"):
        _create_new_chat(store)
        st.rerun()


# ---------------------------------------------------------------------------
# MAIN PAGE ENTRY POINT
# main.py's router should call: top_bar(show_nav=True, show_menu=True); render_finny_page()
# (same pattern as render_tracker() / render_help() / render_profile())
# ---------------------------------------------------------------------------
def render_finny_page():
    st.markdown(FINNY_CSS, unsafe_allow_html=True)
    store = _load_store()

    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>AI HELPER</span>"
        "<h1>Finny — Your AI Money Helper</h1></div>",
        unsafe_allow_html=True,
    )

    if not store["conversations"]:
        _create_new_chat(store)
        st.rerun()
        return

    if not store.get("active_id") or store["active_id"] not in store["conversations"]:
        store["active_id"] = sorted(store["conversations"].values(), key=lambda c: c["created_at"])[-1]["id"]
        _save_store(store)

    sidebar_col, main_col = st.columns([1, 3], gap="medium")
    with sidebar_col:
        _render_finny_sidebar(store)

    with main_col:
        conv = store["conversations"][store["active_id"]]
        stage = conv["stage"]

        if stage == "situation":
            _stage_situation(store, conv)
            return
        if stage == "clarify":
            _stage_clarify(store, conv)
            return

        _bubble("You said:", conv["situation"])

        if stage == "collecting":
            _stage_collecting(store, conv)
            return

        inputs = conv["inputs"]
        analysis = conv["analysis"]

        if stage == "analysis":
            _stage_analysis(store, conv, inputs, analysis)
            return
        if stage == "detail":
            _stage_detail(store, conv, inputs, analysis)
            return
