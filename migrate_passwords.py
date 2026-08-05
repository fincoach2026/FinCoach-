import json
import bcrypt

USERS_FILE = "users.json"

# Load users
with open(USERS_FILE, "r", encoding="utf-8") as f:
    users = json.load(f)

updated = 0

for username, user in users.items():
    password = user.get("password", "")

    # Skip users that already have a bcrypt hash
    if isinstance(password, str) and password.startswith("$2"):
        continue

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user["password"] = hashed
    updated += 1

# Save users
with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump(users, f, indent=4)

print(f"Updated {updated} users.")
