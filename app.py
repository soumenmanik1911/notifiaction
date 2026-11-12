"""AI-Powered Notification Assistant - Streamlit UI.   Run:  python -m streamlit run app.py"""
import html
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from core import db, focus_db
from core.categorize import CATEGORIES, Categorizer, urgency_score
from core.chat import generate_reply
from core.focus import MODES, auto_mode, gate
from core.recommend import Recommender
from core.samples import next_sample
from core.schedule import ACTIONS, LABELS, due_time
from core.simulator import persona_action, random_notification, random_time
from ui.components import render_home
from ui.styles import inject_css

st.set_page_config(page_title="Notification Assistant", page_icon="N", layout="wide")
inject_css()

CAT_STYLE = {  # text colour, background
    "work": ("", "#2D5BFF", "#E6ECFF"),
    "family": ("", "#D6336C", "#FFE3EE"),
    "shopping": ("", "#E67700", "#FFF0D9"),
    "college": ("", "#7048E8", "#EEE6FF"),
    "finance": ("", "#0B8A5F", "#DDF6EA"),
    "social": ("", "#0C8599", "#DDF4F8"),
}
ACTION_ICON = {"1h": "", "tonight": "", "tomorrow": "", "important": "", "ignore": ""}


@st.cache_resource
def get_categorizer():
    return Categorizer()


cat_model = get_categorizer()
rec = Recommender().fit(db.user_choices_df())

DURATION_OPTIONS = {
    "30 min": 30,
    "1 hr": 60,
    "2 hr": 120,
    "Until I turn off": None,
}


def _new_focus_session(mode, duration_label):
    mins = DURATION_OPTIONS[duration_label]
    now = datetime.now()
    return {
        "mode": mode,
        "started_at": now.isoformat(timespec="seconds"),
        "ends_at": (now + timedelta(minutes=mins)).isoformat(timespec="seconds") if mins else None,
        "duration": duration_label,
        "shown": 0,
        "held": 0,
        "silenced": 0,
        "manual": True,
    }


def end_focus_session():
    s = st.session_state.get("focus_session")
    if s and s.get("mode") and s["mode"] != "Off":
        focus_db.log_session(
            s["mode"],
            s["started_at"],
            datetime.now().isoformat(timespec="seconds"),
            s.get("shown", 0),
            s.get("held", 0),
            s.get("silenced", 0),
        )
        st.session_state["focus_summary"] = {
            "mode": s["mode"],
            "shown": s.get("shown", 0),
            "held": s.get("held", 0),
            "silenced": s.get("silenced", 0),
        }
        st.session_state["focus_review_held"] = len(focus_db.list_held())
    st.session_state["focus_session"] = None
    st.session_state["focus_mode_select"] = "Off"


def badge(cat):
    e, fg, bg = CAT_STYLE.get(cat, ("", "#444", "#EEE"))
    return f'<span class="pill" style="color:{fg};background:{bg}">{html.escape(str(cat))}</span>'


def act(n, action, source="user"):
    now = datetime.now()
    db.log_choice(n["id"], n["category"], n["app"], now, n["urgency"], action, source)
    due = due_time(action, now)
    if due:
        db.add_reminder(n["id"], due, n["text"])
    db.set_status(n["id"], "ignored" if action == "ignore" else "snoozed")
    st.rerun()


def release_held_item(h):
    """Release a held notification back to inbox (shared logic)."""
    h = dict(h)
    focus_db.record_release_signal(h["id"])
    focus_db.set_held_status(h["id"], "released")
    db.add_notification(
        h.get("source", "App"),
        "held",
        h.get("text", ""),
        h.get("category", "social"),
        float(h.get("urgency", 0)),
    )


def dismiss_held_item(h):
    """Dismiss a held notification (shared logic)."""
    h = dict(h)
    focus_db.set_held_status(h["id"], "dismissed")


def process_incoming(app_name, sender, text):
    cat, _ = cat_model.predict(text)
    urg = urgency_score(text)
    mode = st.session_state.get("focus_mode_select", "Off")
    decision = gate(mode, cat, urg, source=app_name)
    if decision == "SHOW":
        db.add_notification(app_name, sender, text, cat, urg)
        toast_icon = "🚨" if urg >= 0.6 else "🛎️"
        st.toast(f"New {cat} notification added from {app_name or 'unknown source'}!", icon=toast_icon)
        fs = st.session_state.get("focus_session")
        if fs and fs.get("mode") == mode and mode != "Off":
            fs["shown"] = fs.get("shown", 0) + 1
        st.session_state["focus_notice"] = ("toast", '<div class="toast-notice show">Notification shown: sent to inbox.</div>')
        return decision
    if decision == "HOLD":
        focus_db.add_held(app_name, text, cat, urg, mode=mode)
        fs = st.session_state.get("focus_session")
        if fs and fs.get("mode") == mode and mode != "Off":
            fs["held"] = fs.get("held", 0) + 1
        st.session_state["focus_notice"] = ("toast", '<div class="toast-notice hold">Notification held: queued until focus ends.</div>')
        return decision
    if decision == "SILENCE":
        fs = st.session_state.get("focus_session")
        if fs and fs.get("mode") == mode and mode != "Off":
            fs["silenced"] = fs.get("silenced", 0) + 1
        st.session_state["focus_notice"] = ("toast", '<div class="toast-notice silence">Notification silenced: logged only.</div>')
        return decision
    return decision


def init_state():
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"
    if "focus_session" not in st.session_state:
        st.session_state["focus_session"] = None
    if "focus_summary" not in st.session_state:
        st.session_state["focus_summary"] = None
    if "focus_review_held" not in st.session_state:
        st.session_state["focus_review_held"] = 0
    if "show_held_review" not in st.session_state:
        st.session_state["show_held_review"] = False
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []


def render_app():
    st.markdown('<div class="app-header"><h2>Notification Assistant</h2><p>Manage notifications, reminders, and what the assistant has learned.</p></div>', unsafe_allow_html=True)

    summary = st.session_state.pop("focus_summary", None)
    if summary:
        st.markdown(
            f'<div class="banner">Focus summary — {html.escape(summary["mode"])}: '
            f'{summary["shown"]} shown, {summary["held"]} held, {summary["silenced"]} silenced</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.get("focus_review_held", 0) > 0:
        nheld = st.session_state["focus_review_held"]
        c1, c2 = st.columns([4, 1])
        c1.info(f"You have {nheld} held notifications.")
        if c2.button("Review them", key="review_held_btn"):
            st.session_state["show_held_review"] = True
            st.session_state["focus_review_held"] = 0
            st.rerun()
        else:
            st.session_state["focus_review_held"] = 0

    if st.session_state.get("show_held_review"):
        st.markdown("### Held notifications")
        held_items = focus_db.list_held()
        if not held_items:
            st.info("No held notifications.")
        for h in held_items:
            h = dict(h)
            a, b1, b2 = st.columns([6, 1, 1])
            a.markdown(
                f'<div class="card" style="margin-top:8px">'
                f'{badge(h.get("category", ""))}'
                f'<span class="pill">{html.escape(str(h.get("source", "")))}</span>'
                f'<div class="msg">{html.escape(str(h.get("text", "")))}</div>'
                f'<div class="meta">urgency {float(h.get("urgency", 0)):.2f} · {html.escape(str(h.get("created_at", "")))}</div></div>',
                unsafe_allow_html=True,
            )
            if b1.button("Release", key=f"rrel{h['id']}", width="stretch"):
                try:
                    release_held_item(h)
                except sqlite3.Error as e:
                    st.error(f"Could not release notification: {e}")
                except Exception as e:
                    st.error(f"Could not release notification: {e}")
                else:
                    st.toast("Held notification released to Inbox.", icon="✅")
                    st.rerun()
            if b2.button("Dismiss", key=f"rdis{h['id']}", width="stretch"):
                try:
                    dismiss_held_item(h)
                except sqlite3.Error as e:
                    st.error(f"Could not dismiss notification: {e}")
                except Exception as e:
                    st.error(f"Could not dismiss notification: {e}")
                else:
                    st.toast("Held notification dismissed.", icon="🗑️")
                    st.rerun()
        if st.button("Close review", key="close_held_review"):
            st.session_state["show_held_review"] = False
            st.rerun()

    notice = st.session_state.pop("focus_notice", None)
    if notice:
        kind, msg = notice
        if kind == "info":
            st.info(msg)
        elif kind == "caption":
            st.caption(msg)
        elif kind == "toast":
            st.markdown(msg, unsafe_allow_html=True)
        else:
            st.info(msg)

    n_pending = len(db.pending())
    n_rem = len(db.reminders())
    n_ch = len(db.user_choices_df())
    s1, s2, s3 = st.columns(3)
    s1.markdown(f'<div class="stat"><b>{n_pending}</b><span>Pending notifications</span></div>', unsafe_allow_html=True)
    s2.markdown(f'<div class="stat"><b>{n_rem}</b><span>Active reminders</span></div>', unsafe_allow_html=True)
    s3.markdown(f'<div class="stat"><b>{n_ch}</b><span>Choices learned from</span></div>', unsafe_allow_html=True)

    # ---------------- sidebar ----------------
    with st.sidebar:
        nav_home, nav_chat = st.columns(2)
        with nav_home:
            if st.button("Home", key="app_home_link", width="stretch"):
                st.session_state["page"] = "Home"
                st.rerun()
        with nav_chat:
            if st.button("Chat", key="app_chat_link", width="stretch"):
                st.session_state["page"] = "Chat"
                st.rerun()
        st.markdown("### Focus mode")
        mode_options = list(MODES.keys())
        default_mode = auto_mode()
        if "focus_mode_select" not in st.session_state:
            st.session_state["focus_mode_select"] = default_mode
        prev_mode = st.session_state["focus_mode_select"]
        selected_mode = st.selectbox(
            "Mode",
            mode_options,
            index=mode_options.index(st.session_state["focus_mode_select"]),
            key="focus_mode_widget",
        )
        st.session_state["focus_mode_select"] = selected_mode
        duration_label = st.selectbox("Duration", list(DURATION_OPTIONS.keys()), index=3, key="focus_duration_widget")
        if selected_mode != "Off" and (
            st.session_state.get("focus_session") is None
            or st.session_state.get("focus_session", {}).get("mode") != selected_mode
            or prev_mode != selected_mode
        ):
            st.session_state["focus_session"] = _new_focus_session(selected_mode, duration_label)
        if selected_mode == "Off" and prev_mode != "Off":
            end_focus_session()
        # update duration end for active session if user changed duration
        fs = st.session_state.get("focus_session")
        if fs and fs.get("mode") == selected_mode and selected_mode != "Off":
            mins = DURATION_OPTIONS[duration_label]
            now = datetime.now()
            fs["duration"] = duration_label
            fs["ends_at"] = (now + timedelta(minutes=mins)).isoformat(timespec="seconds") if mins else None
        st.caption(f"Auto suggestion now: {auto_mode()}")

        st.markdown("### Send a notification")
        if "sample_filter" not in st.session_state:
            st.session_state["sample_filter"] = "Any"
        if "send_warning" not in st.session_state:
            st.session_state["send_warning"] = ""

        def _sample_cat():
            f = st.session_state.get("sample_filter", "Any")
            return None if f == "Any" else f

        def _load_sample():
            last = st.session_state.get("current_sample")
            s = next_sample(_sample_cat(), last)
            st.session_state["current_sample"] = s
            st.session_state["in_msg"] = s["message"] if s else ""
            st.session_state["in_app"] = s["app"] if s else ""
            st.session_state["in_sender"] = s["sender"] if s else ""

        if "in_msg" not in st.session_state:
            _load_sample()

        def _send_current():
            msg = (st.session_state.get("in_msg") or "").strip()
            if not msg:
                st.session_state["send_warning"] = "Message is empty."
                return
            st.session_state["send_warning"] = ""
            app_n = st.session_state.get("in_app", "")
            snd = st.session_state.get("in_sender", "")
            _load_sample()
            try:
                process_incoming(app_n, snd, msg)
            except sqlite3.Error as e:
                st.session_state["send_warning"] = f"Database error while sending: {e}"
            except Exception as e:
                st.session_state["send_warning"] = f"Could not send notification: {e}"

        def _send_five():
            try:
                for _ in range(5):
                    s = next_sample(_sample_cat(), st.session_state.get("current_sample"))
                    st.session_state["current_sample"] = s
                    if not s:
                        break
                    pcat, _ = cat_model.predict(s["message"])
                    urg = urgency_score(s["message"])
                    mode = st.session_state.get("focus_mode_select", "Off")
                    decision = gate(mode, pcat, urg, source=s["app"])
                    if decision == "SHOW":
                        db.add_notification(s["app"], s["sender"], s["message"], pcat, urg)
                        fsess = st.session_state.get("focus_session")
                        if fsess and fsess.get("mode") == mode and mode != "Off":
                            fsess["shown"] = fsess.get("shown", 0) + 1
                    elif decision == "HOLD":
                        focus_db.add_held(s["app"], s["message"], pcat, urg, mode=mode)
                        fsess = st.session_state.get("focus_session")
                        if fsess and fsess.get("mode") == mode and mode != "Off":
                            fsess["held"] = fsess.get("held", 0) + 1
                    else:
                        fsess = st.session_state.get("focus_session")
                        if fsess and fsess.get("mode") == mode and mode != "Off":
                            fsess["silenced"] = fsess.get("silenced", 0) + 1
                s = st.session_state.get("current_sample")
                if s:
                    st.session_state["in_msg"] = s["message"]
                    st.session_state["in_app"] = s["app"]
                    st.session_state["in_sender"] = s["sender"]
            except sqlite3.Error as e:
                st.session_state["send_warning"] = f"Database error while sending samples: {e}"
                return
            except Exception as e:
                st.session_state["send_warning"] = f"Could not send samples: {e}"
                return
            st.rerun()

        st.selectbox("Sample category", ["Any"] + list(CATEGORIES), key="sample_filter")
        st.text_input("Message", key="in_msg")
        st.text_input("App", key="in_app")
        st.text_input("Sender", key="in_sender")
        cs = st.session_state.get("current_sample")
        if cs and st.session_state.get("in_msg") == cs["message"] and st.session_state.get("in_app") == cs["app"] and st.session_state.get("in_sender") == cs["sender"]:
            st.caption(f"Expected: {cs['category']} / {cs['urgency']}")
        if st.session_state.get("send_warning"):
            st.warning(st.session_state["send_warning"])
        b1, b2, b3 = st.columns(3)
        b1.button("Send", type="primary", width="stretch", on_click=_send_current)
        b2.button("Shuffle", width="stretch", on_click=_load_sample)
        b3.button("Send 5 random", width="stretch", on_click=_send_five)
        if st.button("Random notification", width="stretch"):
            try:
                _, a, t = random_notification()
                process_incoming(a, "random", t)
            except sqlite3.Error as e:
                st.warning(f"Database error: {e}")
            except Exception as e:
                st.warning(f"Could not send random notification: {e}")
        st.divider()
        st.markdown("### Demo helpers")
        n_sim = st.slider("Simulated decisions", 20, 200, 60, 10)
        if st.button("Train with simulated user", width="stretch"):
            try:
                for _ in range(n_sim):
                    tc, a, t = random_notification()
                    pc, _ = cat_model.predict(t)
                    u, ts = urgency_score(t), random_time()
                    nid = db.add_notification(a, "sim", t, pc, u, ts)
                    db.log_choice(nid, pc, a, ts, u, persona_action(tc, ts.hour, u), "user")
                    db.set_status(nid, "snoozed")
            except sqlite3.Error as e:
                st.error(f"Database error during simulation: {e}")
            except Exception as e:
                st.error(f"Simulation failed: {e}")
            else:
                st.rerun()
        if st.button("Reset all data", width="stretch"):
            try:
                db.reset()
            except sqlite3.Error as e:
                st.error(f"Database error during reset: {e}")
            except Exception as e:
                st.error(f"Reset failed: {e}")
            else:
                st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inbox", "Reminders", "Held", "What it learned", "Chat"])

    # ---------------- inbox ----------------
    with tab1:
        items = db.pending()
        if not items:
            st.info("Inbox zero. Send a notification from the sidebar.")
        for n in items:
            now = datetime.now()
            probs, state = rec.predict(n["category"], n["app"], n["urgency"], now)
            top = rec.best(probs)
            ranked = sorted(probs.items(), key=lambda kv: -kv[1])[:3]
            bars = "".join(
                f'<div style="margin-top:8px;font-size:.82rem;font-family:var(--font-mono)">{LABELS[a]} · {p:.0%}'
                f'<div class="bar"><div class="grow" style="--w:{p * 100:.0f}%"></div></div></div>' for a, p in ranked
            )
            st.markdown(
                f'<div class="inbox-card card">'
                f'<span class="pill mono-chip">{badge(n["category"])}</span> '
                f'<span class="pill mono-chip">{html.escape(n["app"])}</span>'
                f'<div class="msg">{html.escape(n["text"])}</div>'
                f'<div class="meta">from {html.escape(n["sender"])} · urgency {n["urgency"]:.2f}</div>'
                f'<div class="sugg"><b>Suggested: {LABELS[top]}</b> <span class="muted">({state})</span>{bars}</div></div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(len(ACTIONS) + 1)
            for col, a in zip(cols, ACTIONS):
                label = f"{LABELS[a]}"
                btn_type = "primary" if a == top else "secondary"
                with col:
                    st.markdown('<div class="inbox-action">', unsafe_allow_html=True)
                    if st.button(label, key=f"{n['id']}_{a}", type=btn_type, width="stretch"):
                        st.session_state["clicked_action"] = f"{n['id']}_{a}"
                        try:
                            act(n, a)
                        except sqlite3.Error as e:
                            st.error(f"Database error: {e}")
                        except Exception as e:
                            st.error(f"Could not apply action: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)
            with cols[-1]:
                st.markdown('<div class="ai-action">', unsafe_allow_html=True)
                if st.button("Let AI decide", key=f"{n['id']}_ai", width="stretch"):
                    st.session_state["clicked_action"] = f"{n['id']}_ai"
                    try:
                        act(n, top, source="ai")
                    except sqlite3.Error as e:
                        st.error(f"Database error: {e}")
                    except Exception as e:
                        st.error(f"Could not apply action: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- reminders ----------------
    with tab2:
        rs = db.reminders()
        if not rs:
            st.info("No active reminders.")
        for r in rs:
            due = datetime.fromisoformat(r["due_ts"])
            overdue = due <= datetime.now()
            colr = "#D6336C" if overdue else "#6C5CE7"
            a, b = st.columns([6, 1])
            a.markdown(
                f'<div class="card" style="margin-top:8px;border-left:3px solid {colr};padding-left:12px">'
                f'<span class="pill">{"Due now" if overdue else due.strftime("%a %d %b, %H:%M")}</span>'
                f'<div class="msg">{html.escape(r["text"])}</div></div>',
                unsafe_allow_html=True,
            )
            if b.button("Done", key=f"done{r['id']}", width="stretch"):
                try:
                    db.complete_reminder(r["id"])
                except sqlite3.Error as e:
                    st.error(f"Could not complete reminder: {e}")
                except Exception as e:
                    st.error(f"Could not complete reminder: {e}")
                else:
                    st.toast("Reminder completed.", icon="✅")
                    st.rerun()

    # ---------------- held ----------------
    with tab3:
        held_items = focus_db.list_held()
        if not held_items:
            st.info("No held notifications.")
        for h in held_items:
            h = dict(h)
            a, b1, b2 = st.columns([6, 1, 1])
            a.markdown(
                f'<div class="card" style="margin-top:8px">'
                f'{badge(h.get("category", ""))}'
                f'<span class="pill">{html.escape(str(h.get("source", "")))}</span>'
                f'<div class="msg">{html.escape(str(h.get("text", "")))}</div>'
                f'<div class="meta">urgency {float(h.get("urgency", 0)):.2f} · {html.escape(str(h.get("created_at", "")))}</div></div>',
                unsafe_allow_html=True,
            )
            if b1.button("Release", key=f"rel{h['id']}", width="stretch"):
                try:
                    release_held_item(h)
                except sqlite3.Error as e:
                    st.error(f"Could not release notification: {e}")
                except Exception as e:
                    st.error(f"Could not release notification: {e}")
                else:
                    st.toast("Held notification released to Inbox.", icon="✅")
                    st.rerun()
            if b2.button("Dismiss", key=f"dis{h['id']}", width="stretch"):
                try:
                    dismiss_held_item(h)
                except sqlite3.Error as e:
                    st.error(f"Could not dismiss notification: {e}")
                except Exception as e:
                    st.error(f"Could not dismiss notification: {e}")
                else:
                    st.toast("Held notification dismissed.", icon="🗑️")
                    st.rerun()

    # ---------------- insights ----------------
    with tab4:
        st.markdown("#### Focus always-allow rules")
        rules = focus_db.list_allow_rules()
        if rules:
            for r in rules:
                r = dict(r)
                c1, c2 = st.columns([6, 1])
                c1.write(f"{r.get('source', '')} | {r.get('category', '')} | {r.get('mode', '')} (learned {r.get('created_at', '')})")
                if c2.button("Remove", key=f"rmrule{r['id']}"):
                    try:
                        focus_db.remove_allow_rule(r["id"])
                    except sqlite3.Error as e:
                        st.error(f"Could not remove rule: {e}")
                    except Exception as e:
                        st.error(f"Could not remove rule: {e}")
                    else:
                        st.rerun()
        else:
            st.caption("No learned focus rules yet.")
        st.divider()
        df = db.user_choices_df()
        if df.empty:
            st.info("Make some choices, or click 'Train with simulated user', to see patterns.")
        else:
            by_cat = df.groupby("category")["action"].agg(lambda s: s.mode()[0]).reset_index()
            by_cat.columns = ["category", "usually"]
            st.markdown("**Your usual choice, by category**")
            st.dataframe(by_cat, hide_index=True, width="stretch")
            st.markdown("**Choices by category**")
            st.dataframe(pd.crosstab(df["category"], df["action"]), width="stretch")
            st.markdown("**Try: when would you snooze 'tomorrow'?**")
            cat = st.selectbox("Category", list(df["category"].unique()))
            hr = st.slider("Hour", 0, 23, 15)
            urg = st.slider("Urgency", 0.0, 1.0, 0.2, 0.05)
            probs, state = rec.predict(cat, "Slack", urg, datetime.now().replace(hour=hr))
            st.bar_chart(pd.Series({LABELS[k]: v for k, v in probs.items()}), color="#4DA3FF")
            st.caption(state)

    # ---------------- chat ----------------
    with tab5:
        st.markdown("#### Chat with the assistant")
        if not st.session_state["chat_messages"]:
            st.session_state["chat_messages"].append(
                {"role": "assistant", "content": generate_reply("hello", now=datetime.now())}
            )
        for m in st.session_state["chat_messages"]:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        if prompt := st.chat_input("Ask about notifications, reminders, focus, or what it learned"):
            st.session_state["chat_messages"].append({"role": "user", "content": prompt})
            reply = generate_reply(prompt, now=datetime.now())
            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
            st.rerun()


def render_chat():
    st.markdown('<div class="app-header"><h2>Chat</h2><p>Ask about notifications, reminders, focus, or what it learned.</p></div>', unsafe_allow_html=True)
    col_home, col_app = st.columns(2)
    with col_home:
        if st.button("Home", key="chat_home_link", width="stretch"):
            st.session_state["page"] = "Home"
            st.rerun()
    with col_app:
        if st.button("Dashboard", key="chat_app_link", width="stretch"):
            st.session_state["page"] = "App"
            st.rerun()

    if not st.session_state["chat_messages"]:
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": generate_reply("hello", now=datetime.now())}
        )
    for m in st.session_state["chat_messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if prompt := st.chat_input("Ask about notifications, reminders, focus, or what it learned"):
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        reply = generate_reply(prompt, now=datetime.now())
        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        st.rerun()


init_state()
page = st.session_state.get("page", "Home")
if page == "Home":
    render_home()
elif page == "Chat":
    render_chat()
else:
    render_app()
