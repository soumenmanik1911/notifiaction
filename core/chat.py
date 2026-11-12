"""Hybrid AI chat assistant for the Notification Assistant chat tab.

Uses Groq's LLM for natural, conversational replies grounded in live local data.
Falls back to deterministic rule-based replies if the Groq API is unavailable
or no API key is configured.
"""

import logging
import os
from datetime import datetime

import streamlit as st

from core import db, focus_db
from core.categorize import CATEGORIES
from core.focus import auto_mode

try:
    from groq import Groq
except Exception:  # pragma: no cover - optional dependency
    Groq = None

logger = logging.getLogger(__name__)

# Safely fetch the API key (Streamlit secrets first, then environment)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY and Groq is not None else None


def daytime_label(hour=None):
    """Return a time-of-day label (morning/afternoon/evening/night) for an hour."""
    h = datetime.now().hour if hour is None else int(hour)
    if 5 <= h < 12:
        return "morning"
    if 12 <= h < 17:
        return "afternoon"
    if 17 <= h < 21:
        return "evening"
    return "night"


def _urg_level(urgency):
    if urgency >= 0.6:
        return "High"
    if urgency >= 0.3:
        return "Medium"
    return "Low"


def _join_counts(counts):
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items()) if v) or "none"


def _live_context(now):
    """Gather counts and breakdowns from the live databases."""
    c = db.conn()
    try:
        pending_items = db.pending(c)
        by_cat = {}
        by_urg = {"High": 0, "Medium": 0, "Low": 0}
        for n in pending_items:
            cat = n["category"] or "uncategorized"
            by_cat[cat] = by_cat.get(cat, 0) + 1
            level = _urg_level(float(n["urgency"] or 0))
            by_urg[level] = by_urg.get(level, 0) + 1
        reminders = db.reminders(c)
        n_rem = len(reminders)
        n_due = sum(1 for r in reminders if datetime.fromisoformat(r["due_ts"]) <= now)
        n_choices = len(db.user_choices_df(c))
    finally:
        c.close()

    held_items = focus_db.list_held(None)
    held_cats = {}
    for h in held_items:
        cat = h["category"] or "uncategorized"
        held_cats[cat] = held_cats.get(cat, 0) + 1
    rules = focus_db.list_allow_rules()

    return {
        "n_pending": len(pending_items),
        "by_cat": by_cat,
        "by_urg": by_urg,
        "n_rem": n_rem,
        "n_due": n_due,
        "n_choices": n_choices,
        "n_held": len(held_items),
        "held_cats": held_cats,
        "n_rules": len(rules),
    }


def _rule_based_reply(message, ctx, now):
    """Return a deterministic rule-based reply using live context."""
    hour = now.hour
    day = daytime_label(hour)
    msg = (message or "").strip().lower()

    header = f"It is {day} now (hour {hour})."

    if any(w in msg for w in ("hi", "hello", "hey", "greet", "help", "start")):
        body = ("I'm the notification assistant. Ask me about pending notifications, reminders due, held items, "
                "focus mode and rules, or choices I've learned from. Try: 'how many pending notifications', "
                "'any reminders due now', 'what held items', 'what is focus mode', 'how many choices learned'.")
    elif any(w in msg for w in ("pending", "inbox", "notification")):
        body = (f"{ctx['n_pending']} pending notification{'s' if ctx['n_pending'] != 1 else ''}. "
                f"Categories: {_join_counts(ctx['by_cat'])}. Urgency: {_join_counts(ctx['by_urg'])}.")
    elif any(w in msg for w in ("reminder", "reminders", "due")):
        body = (f"{ctx['n_rem']} active reminder{'s' if ctx['n_rem'] != 1 else ''}, {ctx['n_due']} due now. ")
        if ctx["n_due"]:
            body += "Check the Reminders tab."
    elif any(w in msg for w in ("held", "hold")):
        body = (f"{ctx['n_held']} held notification{'s' if ctx['n_held'] != 1 else ''}. "
                f"Categories: {_join_counts(ctx['held_cats'])}.")
    elif any(w in msg for w in ("focus", "mode", "rule", "rules")):
        body = (f"Focus mode is {auto_mode(now)} now. {ctx['n_rules']} learned always-allow rule"
                f"{'s' if ctx['n_rules'] != 1 else ''}. {ctx['n_held']} item"
                f"{'s' if ctx['n_held'] != 1 else ''} held during focus.")
    elif any(w in msg for w in ("learn", "choice", "choices", "habit")):
        body = f"{ctx['n_choices']} user choice{'s' if ctx['n_choices'] != 1 else ''} learned from so far."
    elif any(cat in msg for cat in CATEGORIES):
        parts = [f"{cat}: {ctx['by_cat'].get(cat, 0)} pending, {ctx['held_cats'].get(cat, 0)} held"
                 for cat in CATEGORIES if cat in msg]
        body = "; ".join(parts) if parts else (f"Pending by category: {_join_counts(ctx['by_cat'])}. "
                                               f"Held by category: {_join_counts(ctx['held_cats'])}.")
    else:
        body = (f"{ctx['n_pending']} pending, {ctx['n_rem']} reminder{'s' if ctx['n_rem'] != 1 else ''} "
                f"({ctx['n_due']} due now), {ctx['n_held']} held, {ctx['n_rules']} focus rule"
                f"{'s' if ctx['n_rules'] != 1 else ''}, {ctx['n_choices']} choices learned.")

    return header + " " + body


def generate_reply(message, now=None):
    """Return a hybrid AI reply with deterministic fallback."""
    now = now or datetime.now()
    ctx = _live_context(now)

    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not found (checked st.secrets then env); using rule-based fallback.")
        return _rule_based_reply(message, ctx, now)
    if Groq is None:
        logger.warning("groq package not available; using rule-based fallback.")
        return _rule_based_reply(message, ctx, now)
    if groq_client is None:
        logger.warning("Groq client not initialized; using rule-based fallback.")
        return _rule_based_reply(message, ctx, now)

    system_prompt = f"""
You are the conversational AI for the "Smart Notification Assistant". You are powered by Groq's fast inference, but you operate securely on top of the user's local database.

APP OVERVIEW:
This app reduces interruptions without missing what matters. It categorizes notifications (Work, Family, Shopping, Education), detects urgency, and recommends actions. It features time-based Focus Modes, Reminders, and an AI learning algorithm.

YOUR CAPABILITIES & LIMITATIONS:
- You are a hybrid AI: Answer questions using ONLY the "LIVE LOCAL CONTEXT" provided below.
- You CANNOT take actions on behalf of the user.
- If the user wants to take action, politely guide them to the correct dashboard tab: "Inbox", "Reminders", "What It Learned", or "Analytics".
- Be concise, helpful, and conversational. 

LIVE LOCAL CONTEXT:
- Time of Day: {daytime_label(now.hour)} (Hour: {now.hour})
- Focus Mode Status: {auto_mode(now)}
- Pending Inbox: {ctx.get('n_pending', 0)} total (High: {ctx.get('by_urg', {}).get('High', 0)}, Medium: {ctx.get('by_urg', {}).get('Medium', 0)}, Low: {ctx.get('by_urg', {}).get('Low', 0)})
- Reminders: {ctx.get('n_rem', 0)} active, {ctx.get('n_due', 0)} due right now!
- Held Items (Muted by Focus Mode): {ctx.get('n_held', 0)}
- Personalized Learning: {ctx.get('n_choices', 0)} rules learned

BEHAVIORAL RULES:
1. If the user asks who you are, proudly mention you are the Smart Notification Assistant powered by Groq.
2. If reminders due right now > 0, gently urge the user to check their Reminders tab immediately.
3. Never make up numbers. Only use the exact counts provided in the LIVE LOCAL CONTEXT.
""".strip()

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message or ""},
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            logger.warning("Groq returned empty content; using rule-based fallback.")
            return _rule_based_reply(message, ctx, now)
        return content.strip()
    except Exception:
        logger.exception("Groq API call failed; using rule-based fallback.")
        return _rule_based_reply(message, ctx, now)
