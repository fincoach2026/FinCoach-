"""
FinCoach — Finance Tracker feature.

Manual income/expense tracking plus savings goals, persisted per user in
tracker_data.json (same folder as main.py). Each account is seeded with a
little demo data on first visit so the dashboard isn't empty on day one —
there's a one-click option to clear it and start fresh.
"""
import json
import os
from collections import defaultdict
from datetime import date

import pandas as pd
import streamlit as st

from activity_log import log_action

APP_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKER_FILE = os.path.join(APP_DIR, "tracker_data.json")

INCOME_CATEGORIES = ["Paycheck", "Side Hustle", "Gift", "Refund", "Other Income"]
EXPENSE_CATEGORIES = [
    "Rent", "Groceries", "Transportation", "Utilities", "Subscriptions",
    "Dining Out", "Entertainment", "Debt Payment", "Other Expense",
]

DEMO_TRANSACTIONS = [
    {"id": 1, "date": "2026-06-01", "type": "income", "category": "Paycheck", "amount": 1800, "note": "Monthly paycheck"},
    {"id": 2, "date": "2026-06-02", "type": "expense", "category": "Rent", "amount": 850, "note": "June rent"},
    {"id": 3, "date": "2026-06-05", "type": "expense", "category": "Groceries", "amount": 145, "note": ""},
    {"id": 4, "date": "2026-06-10", "type": "expense", "category": "Subscriptions", "amount": 32, "note": "Streaming + music"},
    {"id": 5, "date": "2026-06-15", "type": "income", "category": "Side Hustle", "amount": 220, "note": "Freelance design"},
    {"id": 6, "date": "2026-06-18", "type": "expense", "category": "Transportation", "amount": 90, "note": "Gas + transit pass"},
]
DEMO_GOALS = [
    {"id": 1, "name": "Emergency Fund", "target": 1000, "saved": 350},
    {"id": 2, "name": "Concert Trip", "target": 300, "saved": 120},
]


def load_data():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f)


def get_user_data(username):
    data = load_data()
    if username not in data:
        data[username] = {
            "transactions": [dict(t) for t in DEMO_TRANSACTIONS],
            "goals": [dict(g) for g in DEMO_GOALS],
            "next_txn_id": len(DEMO_TRANSACTIONS) + 1,
            "next_goal_id": len(DEMO_GOALS) + 1,
        }
        save_data(data)
    return data[username]


def update_user_data(username, user_data):
    data = load_data()
    data[username] = user_data
    save_data(data)


def clear_demo_data(username):
    data = load_data()
    data[username] = {"transactions": [], "goals": [], "next_txn_id": 1, "next_goal_id": 1}
    save_data(data)


def get_urgent_cases(username):
    """Return up to 3 of the most important/urgent items from a user's
    finance tracking, most urgent first — a negative balance, goals
    furthest behind, and any expense category eating an outsized share
    of income. Used by the dashboard's finance summary card."""
    udata = get_user_data(username)
    txns = udata["transactions"]
    goals = udata["goals"]

    total_income = sum(t["amount"] for t in txns if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in txns if t["type"] == "expense")
    balance = total_income - total_expenses

    cases = []

    if balance < 0:
        cases.append({
            "level": "high", "icon": "🚨",
            "title": "Your balance is negative",
            "detail": f"Expenses are ${abs(balance):,.0f} more than income right now.",
        })

    behind_goals = sorted(
        (g for g in goals if g.get("target", 0) > 0),
        key=lambda g: g["saved"] / g["target"],
    )
    for g in behind_goals:
        pct = g["saved"] / g["target"] * 100
        if pct < 100:
            cases.append({
                "level": "high" if pct < 25 else "medium", "icon": "🎯",
                "title": f"“{g['name']}” is only {pct:.0f}% funded",
                "detail": f"${g['target'] - g['saved']:,.0f} left to reach ${g['target']:,.0f}.",
            })

    if txns:
        by_cat = defaultdict(float)
        for t in txns:
            if t["type"] == "expense":
                by_cat[t["category"]] += t["amount"]
        if by_cat:
            top_cat, top_amt = max(by_cat.items(), key=lambda kv: kv[1])
            if total_income > 0 and (top_amt / total_income) > 0.25:
                cases.append({
                    "level": "medium", "icon": "📈",
                    "title": f"High spending in {top_cat}",
                    "detail": f"${top_amt:,.0f} spent here — over 25% of total income.",
                })

    if not cases:
        cases.append({
            "level": "low", "icon": "✅",
            "title": "Nothing urgent right now",
            "detail": "Your balance and goals are on track — keep it up.",
        })

    order = {"high": 0, "medium": 1, "low": 2}
    cases.sort(key=lambda c: order.get(c["level"], 3))
    return cases[:3]


def render_tracker():
    st.markdown(
        "<div class='fc-fade'><span class='fc-badge'>FINANCE TRACKER</span>"
        "<h1>Your Money, At a Glance</h1></div>",
        unsafe_allow_html=True,
    )

    username = st.session_state.user
    udata = get_user_data(username)
    txns = udata["transactions"]

    total_income = sum(t["amount"] for t in txns if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in txns if t["type"] == "expense")
    balance = total_income - total_expenses
    total_saved = sum(g["saved"] for g in udata["goals"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Income", f"${total_income:,.0f}")
    c2.metric("💸 Total Expenses", f"${total_expenses:,.0f}")
    c3.metric("📈 Balance", f"${balance:,.0f}")
    c4.metric("🎯 Saved Toward Goals", f"${total_saved:,.0f}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    tab_add, tab_txns, tab_charts, tab_goals = st.tabs(
        ["➕ Add", "📋 Transactions", "📊 Charts", "🎯 Goals"]
    )

    # ---- Add transaction ----
    with tab_add:
        with st.form("add_txn_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                txn_type = st.radio(
                    "Type", ["income", "expense"], horizontal=True,
                    format_func=lambda x: "Income" if x == "income" else "Expense",
                )
                txn_date = st.date_input("Date", value=date.today())
            with col2:
                categories = INCOME_CATEGORIES if txn_type == "income" else EXPENSE_CATEGORIES
                category = st.selectbox("Category", categories)
                amount = st.number_input("Amount ($)", min_value=0.0, step=1.0)
            note = st.text_input("Note (optional)")
            submitted = st.form_submit_button("Add transaction", use_container_width=True)
        if submitted:
            if amount <= 0:
                st.error("Enter an amount greater than $0.")
            else:
                new_id = udata.get("next_txn_id", len(txns) + 1)
                txns.append({
                    "id": new_id, "date": str(txn_date), "type": txn_type,
                    "category": category, "amount": amount, "note": note,
                })
                udata["next_txn_id"] = new_id + 1
                update_user_data(username, udata)
                log_action(username, "tracker_transaction_added", {
                    "type": txn_type, "category": category,
                    "amount": amount, "date": str(txn_date), "note": note,
                })
                st.success("Transaction added.")
                st.rerun()

    # ---- Transaction list ----
    with tab_txns:
        if not txns:
            st.markdown(
                "<div class='fc-card'><p>No transactions yet — add your first "
                "one in the <b>Add</b> tab.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            df = pd.DataFrame(sorted(txns, key=lambda t: t["date"], reverse=True))
            df_display = df[["date", "type", "category", "amount", "note"]].copy()
            df_display["type"] = df_display["type"].map({"income": "💰 Income", "expense": "💸 Expense"})
            df_display["amount"] = df_display["amount"].map(lambda a: f"${a:,.2f}")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            del_options = {
                f"{t['date']} — {t['category']} — ${t['amount']:,.2f}": t["id"] for t in txns
            }
            to_delete = st.selectbox("Remove a transaction", ["—"] + list(del_options.keys()))
            if to_delete != "—" and st.button("🗑️ Delete selected transaction"):
                udata["transactions"] = [t for t in txns if t["id"] != del_options[to_delete]]
                update_user_data(username, udata)
                st.rerun()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("Clear all demo/sample data"):
                clear_demo_data(username)
                st.rerun()

    # ---- Charts ----
    with tab_charts:
        if not txns:
            st.markdown(
                "<div class='fc-card'><p>Add some transactions to see your "
                "charts.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            df = pd.DataFrame(txns)

            st.markdown("#### Spending by category")
            expense_df = df[df["type"] == "expense"]
            if not expense_df.empty:
                by_cat = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
                st.bar_chart(by_cat)
            else:
                st.caption("No expenses logged yet.")

            st.markdown("#### Balance over time")
            df_sorted = df.sort_values("date").copy()
            df_sorted["signed"] = df_sorted.apply(
                lambda r: r["amount"] if r["type"] == "income" else -r["amount"], axis=1
            )
            df_sorted["running_balance"] = df_sorted["signed"].cumsum()
            trend = df_sorted.set_index("date")["running_balance"]
            st.line_chart(trend)

    # ---- Goals ----
    with tab_goals:
        goals = udata["goals"]
        if not goals:
            st.markdown(
                "<div class='fc-card'><p>No goals yet — add one below.</p></div>",
                unsafe_allow_html=True,
            )
        for g in goals:
            pct = min(1.0, g["saved"] / g["target"]) if g["target"] > 0 else 0
            st.markdown(f"**{g['name']}** — ${g['saved']:,.0f} of ${g['target']:,.0f}")
            st.progress(pct)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.expander("➕ Add money to a goal"):
            if goals:
                goal_names = {g["name"]: g["id"] for g in goals}
                sel = st.selectbox("Goal", list(goal_names.keys()), key="goal_add_sel")
                add_amt = st.number_input("Amount to add ($)", min_value=0.0, step=1.0, key="goal_add_amt")
                if st.button("Add to goal", key="goal_add_btn"):
                    if add_amt > 0:
                        for g in goals:
                            if g["id"] == goal_names[sel]:
                                g["saved"] += add_amt
                        update_user_data(username, udata)
                        log_action(username, "tracker_goal_funded", {"goal": sel, "amount": add_amt})
                        st.rerun()
            else:
                st.caption("Create a goal first.")

        with st.expander("🎯 Create a new goal"):
            new_name = st.text_input("Goal name", key="new_goal_name")
            new_target = st.number_input("Target amount ($)", min_value=1.0, step=1.0, key="new_goal_target")
            if st.button("Create goal", key="create_goal_btn"):
                if new_name.strip():
                    new_id = udata.get("next_goal_id", len(goals) + 1)
                    goals.append({"id": new_id, "name": new_name.strip(), "target": new_target, "saved": 0})
                    udata["next_goal_id"] = new_id + 1
                    update_user_data(username, udata)
                    log_action(username, "tracker_goal_created", {"name": new_name.strip(), "target": new_target})
                    st.success("Goal created.")
                    st.rerun()
                else:
                    st.error("Give your goal a name.")
