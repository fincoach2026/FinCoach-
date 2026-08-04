import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

SPREADSHEET_KEY = "1QvBHj_kADYAioEfKKp_ULXNlZ4yaEwnF8i71nZ11ZHA"

# Credentials now come from Streamlit's secrets manager (st.secrets),
# not from a JSON file on disk. This works identically on Streamlit
# Cloud and locally (via a local .streamlit/secrets.toml — see the
# setup notes at the bottom of this file), and avoids ever committing
# a real credential file to the repo.
_creds_dict = dict(st.secrets["gcp_service_account"])
creds = Credentials.from_service_account_info(_creds_dict, scopes=SCOPES)

client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_KEY)
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


# ---------------------------------------------------------------------------
# ONE-TIME SETUP — do this once, not part of the code path:
#
# 1) Open your existing key file (fincoach-project-504320-d546e4e64019.json)
#    in a text editor. It has fields like: type, project_id, private_key_id,
#    private_key, client_email, client_id, token_uri, etc.
#
# 2) Streamlit Cloud: go to your app -> Settings -> Secrets, and paste:
#
#    [gcp_service_account]
#    type = "service_account"
#    project_id = "fincoach-project-504320"
#    private_key_id = "PASTE_FROM_JSON"
#    private_key = "PASTE_FULL_PRIVATE_KEY_INCLUDING_-----BEGIN/END-----_LINES"
#    client_email = "PASTE_FROM_JSON"
#    client_id = "PASTE_FROM_JSON"
#    auth_uri = "https://accounts.google.com/o/oauth2/auth"
#    token_uri = "https://oauth2.googleapis.com/token"
#    auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
#    client_x509_cert_url = "PASTE_FROM_JSON"
#
#    IMPORTANT: the private_key value spans multiple lines in the JSON
#    (with \n escapes). Keep it as ONE quoted string in the TOML, with
#    the \n sequences left exactly as they appear in the JSON file --
#    do not manually insert real line breaks inside the quotes.
#
# 3) Local development (optional): create .streamlit/secrets.toml in
#    your project folder with the same [gcp_service_account] block, and
#    add ".streamlit/secrets.toml" to your .gitignore so it never gets
#    committed.
#
# 4) Delete fincoach-project-504320-d546e4e64019.json from the repo
#    entirely once secrets are working -- a real credential file should
#    never live in version control, public or private.
# ---------------------------------------------------------------------------
