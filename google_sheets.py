import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICE_ACCOUNT_FILE = os.path.join(
    BASE_DIR,
    "fincoach-project-504320-d546e4e64019.json"
)

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(
    "1QvBHj_kADYAioEfKKp_ULXNlZ4yaEwnF8i71nZ11ZHA"
)

sheet = spreadsheet.sheet1


def log_event(data):

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("username", ""),
        data.get("email", ""),
        data.get("action", ""),
        data.get("status", ""),
        data.get("transaction_type", ""),
        data.get("category", ""),
        data.get("amount", ""),
        data.get("date", ""),
        data.get("note", ""),
        data.get("payment_method", ""),
        data.get("budget_name", ""),
        data.get("budget_amount", ""),
        data.get("budget_period", ""),
        data.get("budget_remaining", ""),
        data.get("goal_name", ""),
        data.get("target_amount", ""),
        data.get("current_amount", ""),
        data.get("goal_deadline", ""),
        data.get("goal_progress", ""),
        data.get("unit", ""),
        data.get("lesson", ""),
        data.get("correct_answers", ""),
        data.get("total_questions", ""),
        data.get("score", ""),
        data.get("points_earned", "")
    ]

    sheet.append_row(row)
