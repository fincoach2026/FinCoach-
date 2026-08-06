"""
finny_llm.py — thin wrapper around the Claude API that gives Finny its
"understanding" layer: reading a free-text situation statement and deciding
whether it makes sense, and interpreting a free-text reply during analysis
(instead of naive keyword matching).

SETUP (required for the smart behavior — without it, finny.py still runs,
just using simpler fallback rules):
  1. Add "anthropic" to requirements.txt
  2. Put your key in .streamlit/secrets.toml (add this file to .gitignore,
     never commit it):
         ANTHROPIC_API_KEY = "sk-ant-..."
     ...or set ANTHROPIC_API_KEY as an environment variable on whatever
     host you deploy to (Streamlit Community Cloud: Settings -> Secrets).

Everything in this file is defensive: if the package isn't installed, the
key isn't set, the network call fails, or the reply isn't valid JSON,
ask_finny_json() just returns None. finny.py checks for None and falls
back to a rule-based heuristic, so the page never breaks — it just gets
smarter once a key is configured.
"""

import json
import os

import streamlit as st

# Good default: fast and smart enough for short classification/understanding
# calls like these. Swap to "claude-haiku-4-5-20251001" for a cheaper/faster
# model if you're making a lot of calls.
MODEL = "claude-sonnet-5"


def _get_client():
    try:
        import anthropic
    except ImportError:
        return None

    api_key = None
    try:
        # st.secrets raises if no secrets.toml exists at all — guard it
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception:
        return None


def ask_finny_json(system_prompt, user_message, max_tokens=500):
    """
    Calls Claude with a system prompt instructing it to return one JSON
    object, and parses that object out of the reply.

    Returns a dict on success, or None if the API isn't configured, the
    call fails, or the reply can't be parsed as JSON — callers should treat
    None as "fall back to rule-based logic", never as an error to surface
    to the user.
    """
    client = _get_client()
    if client is None:
        return None
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        ).strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        return None
