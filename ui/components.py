"""UI components and home page sections."""

import html

import streamlit as st

from core import db, focus_db
from core.categorize import Categorizer, urgency_score
from core.focus import MODES, gate


def _set_page(page):
    st.session_state["page"] = page


@st.cache_resource
def _home_categorizer():
    return Categorizer()


def get_home_stats():
    c = db.conn()
    try:
        total = c.execute("SELECT COUNT(*) AS n FROM notifications").fetchone()["n"]
        choices = c.execute("SELECT COUNT(*) AS n FROM choices WHERE source='user'").fetchone()["n"]
    finally:
        c.close()
    held = len(focus_db.list_held(None))
    rules = len(focus_db.list_allow_rules())
    return {
        "notifications_handled": total,
        "held_during_focus": held,
        "learned_rules": rules,
        "choices_learned": choices,
    }


def focus_table_rows():
    rows = []
    for name, cfg in MODES.items():
        cats = cfg.get("categories")
        urg = cfg.get("urgencies")
        cats_txt = "All categories" if cats is None else ", ".join(sorted(cats))
        urg_txt = "All urgency levels" if urg is None else ", ".join(sorted(urg))
        if name == "Off":
            note = "No filtering."
        else:
            note = f"Allows {cats_txt} at {urg_txt} urgency. High urgency still shown. Shopping silenced when not allowed."
        rows.append({"mode": name, "allows": cats_txt, "urgency": urg_txt, "note": note})
    return rows


def _urg_label(urg):
    if urg >= 0.6:
        return "High"
    if urg >= 0.3:
        return "Medium"
    return "Low"


def render_home():
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-layout">'
        '<div>'
        '<h1 class="fade-up" style="--i:0">Less interruption, without missing what matters.</h1>'
        '<p class="muted fade-up" style="--i:1">A notification assistant that classifies messages, recommends when to act, learns from your choices, and uses Focus Mode to show, hold, or silence interruptions.</p>'
        '</div>'
        '<div class="fade-up" style="--i:2">'
        '<div class="lanes">'
        '<div class="lane lane-show"><div class="lane-title show">SHOW</div>'
        '<div class="chip c1">Mom: call me when free</div>'
        '<div class="chip c2">Report due 5 PM</div>'
        '<div class="chip c3">Team sync in 30 min</div>'
        '</div>'
        '<div class="lane lane-hold"><div class="lane-title hold">HOLD</div>'
        '<div class="chip c1">Project notes shared</div>'
        '<div class="chip c2">Class slides uploaded</div>'
        '<div class="chip c3">Digest ready to read</div>'
        '</div>'
        '<div class="lane lane-silence"><div class="lane-title silence">SILENCE</div>'
        '<div class="chip c1">Flash sale ends tonight</div>'
        '<div class="chip c2">New arrivals for you</div>'
        '<div class="chip c3">Limited time coupon</div>'
        '</div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="fade-up" style="--i:3">', unsafe_allow_html=True)
    st.markdown('<div class="explore-wrap">', unsafe_allow_html=True)
    if st.button("Explore", key="home_explore", type="primary"):
        _set_page("App")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p><a href="#how-it-works" class="how-link">How it works</a></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up reveal" style="--i:0">Live demonstration</h2>', unsafe_allow_html=True)
    demo_mode = st.selectbox("Focus mode for demo", list(MODES.keys()), index=list(MODES.keys()).index("Study") if "Study" in MODES else 0, key="demo_mode")
    examples = [
        {"message": "Submit the report by 5 PM today.", "app": "Slack", "sender": "Team Lead"},
        {"message": "Mom: call me when you are free", "app": "WhatsApp", "sender": "Mom"},
        {"message": "Flash sale ends tonight on selected items.", "app": "Flipkart", "sender": "Flipkart"},
    ]
    cat_model = _home_categorizer()
    # wrapper keyed by mode to replay animations on change
    st.markdown(f'<div class="demo-wrap" data-mode="{html.escape(demo_mode)}">', unsafe_allow_html=True)
    st.markdown('<div class="demo-row demo-head"><div>Message</div><div>Category</div><div>Urgency</div><div>Decision</div></div>', unsafe_allow_html=True)
    for i, ex in enumerate(examples):
        cat, _ = cat_model.predict(ex["message"])
        urg = urgency_score(ex["message"])
        ulabel = _urg_label(urg)
        decision = gate(demo_mode, cat, urg, source=ex["app"])
        dcls = decision.lower()
        st.markdown(
            f'<div class="demo-row slide" style="--i:{i}">'
            f'<div>{html.escape(ex["message"])}</div>'
            f'<div>{html.escape(cat)}</div>'
            f'<div>{ulabel}</div>'
            f'<div><span class="decision-pill {dcls}">{html.escape(decision)}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p class="muted" style="margin-top:0.5rem;">Results from the classifier and Focus gate for the selected mode.</p>', unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown('<h2 class="reveal">Numbers</h2>', unsafe_allow_html=True)
    stats = get_home_stats()
    empty = stats["notifications_handled"] == 0 and stats["choices_learned"] == 0 and stats["held_during_focus"] == 0 and stats["learned_rules"] == 0
    if empty:
        st.markdown('<p class="muted">No data yet - try the app.</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, stats["notifications_handled"], "Notifications handled"),
        (c2, stats["held_during_focus"], "Held during focus"),
        (c3, stats["learned_rules"], "Learned always-allow rules"),
        (c4, stats["choices_learned"], "Choices learned from"),
    ]:
        col.markdown(
            f'<div class="fade-up reveal"><div class="numeral count" style="--target:{int(val)}">{int(val)}</div>'
            f'<div class="num-label">{html.escape(label)}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div id="how-it-works"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="reveal">How it works</h2>', unsafe_allow_html=True)
    steps = [
        ("1", "Notification arrives", "A message and its source are received from the form or a sample."),
        ("2", "It is classified", "The system predicts a category and estimates urgency from the message."),
        ("3", "You choose or let it decide", "Focus Mode may show, hold, or silence it; when shown, you pick an action or let the assistant decide."),
        ("4", "It learns", "Your choices and release signals shape future recommendations and focus rules."),
    ]
    for i, (num, title, desc) in enumerate(steps):
        st.markdown(
            f'<div class="step-row fade-up reveal" style="--i:{i}">'
            f'<div class="step-num">{num}</div>'
            f'<div><span class="step-line"></span><p><strong>{html.escape(title)}</strong></p>'
            f'<p class="muted">{html.escape(desc)}</p></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<h2 class="reveal">Focus modes</h2>', unsafe_allow_html=True)
    rows = focus_table_rows()
    thead = "<tr><th>Mode</th><th>Allowed categories</th><th>Allowed urgency</th><th>Behavior</th></tr>"
    body_rows = []
    for r in rows:
        allow_cls = "" if r["allows"] == "All categories" else "allowed"
        urg_cls = "" if r["urgency"] == "All urgency levels" else "allowed"
        body_rows.append(
            f"<tr><td>{html.escape(r['mode'])}</td>"
            f"<td class='{allow_cls}'>{html.escape(r['allows'])}</td>"
            f"<td class='{urg_cls}'>{html.escape(r['urgency'])}</td>"
            f"<td>{html.escape(r['note'])}</td></tr>"
        )
    st.markdown(f'<table class="clean focus-table"><thead>{thead}</thead><tbody>{"".join(body_rows)}</tbody></table>', unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown('<p class="fade-up reveal">Try the assistant with sample notifications and see how Focus Mode and learning respond.</p>', unsafe_allow_html=True)
    st.markdown('<div class="explore-wrap">', unsafe_allow_html=True)
    if st.button("Explore", key="home_explore_bottom", type="primary"):
        _set_page("App")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
