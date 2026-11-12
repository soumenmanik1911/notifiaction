"""Design tokens and global styles for the Streamlit app."""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg: #f4f1ea;
  --bg-elev: #fbf9f4;
  --text: #171717;
  --muted: #6a655d;
  --ink: #171717;
  --rule: #d6d0c6;
  --accent: #b33a3a;
  --accent-text: #ffffff;
  --show-bg: #dff3e4;
  --show-text: #14532d;
  --hold-bg: #fff1d6;
  --hold-text: #7a4a00;
  --silence-bg: #eceff1;
  --silence-text: #37474f;
  --font-display: "Bricolage Grotesque", "Iowan Old Style", "Georgia", serif;
  --font-body: "Instrument Sans", "Avenir Next", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", "Menlo", "Consolas", monospace;
  --radius: 10px;
  --outline-w: 2px;
  --shadow: 4px 4px 0 var(--ink);
  --shadow-hover: 6px 6px 0 var(--ink);
  --shadow-sm: 3px 3px 0 var(--ink);
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 1rem;
  --space-4: 1.5rem;
  --space-5: 2.5rem;
  --space-6: 4rem;
  --max-width: 1100px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #141311;
    --bg-elev: #1c1b18;
    --text: #ece7de;
    --muted: #a39b90;
    --ink: #ece7de;
    --rule: #3a3731;
    --accent: #d46a6a;
    --accent-text: #141311;
    --show-bg: #143322;
    --show-text: #b7e4c7;
    --hold-bg: #3a2a10;
    --hold-text: #ffd699;
    --silence-bg: #2a2e33;
    --silence-text: #d7dde2;
  }
}
html, body, [class*="css"], .stApp { font-family: var(--font-body); color: var(--text); }
.stApp { background: var(--bg); }
.block-container { max-width: var(--max-width); padding-top: var(--space-4); padding-bottom: var(--space-6); }
h1, h2, h3, .serif, .numeral, .step-num { font-family: var(--font-display); color: var(--text); font-weight: 600; letter-spacing: -0.01em; }
h1 { font-size: clamp(2.2rem, 5vw, 3.6rem); line-height: 1.05; margin-bottom: var(--space-3); }
h2 { font-size: clamp(1.4rem, 3vw, 2rem); line-height: 1.2; margin: var(--space-5) 0 var(--space-3); }
p, li { font-size: 1.05rem; line-height: 1.7; color: var(--text); }
label, .caption, .small-label, [data-testid="stCaptionContainer"], .num-label, .demo-head, .mono, [data-testid="stMarkdownContainer"] label {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  letter-spacing: 0.01em;
}
.muted { color: var(--muted); }
.rule { border: none; border-top: 1px solid var(--rule); margin: var(--space-4) 0; }
a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--text); }
a:focus-visible, button:focus-visible, [tabindex]:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible,
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"] > div:focus-within {
  outline: 2px solid var(--accent) !important;
  outline-offset: 2px;
}

/* Buttons */
.stButton > button, [data-testid*="baseButton"] {
  border: var(--outline-w) solid var(--ink) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-body) !important;
  font-weight: 500;
  padding: 0.55rem 1rem;
  background: var(--bg-elev) !important;
  color: var(--text) !important;
  box-shadow: var(--shadow);
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}
.stButton > button[kind="primary"], [data-testid*="baseButton"][kind="primary"] {
  background: var(--accent) !important;
  color: var(--accent-text) !important;
  border-color: var(--ink) !important;
}
.stButton > button:hover, [data-testid*="baseButton"]:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-hover);
}
.stButton > button:active, [data-testid*="baseButton"]:active {
  transform: translate(2px, 2px);
  box-shadow: 0 0 0 var(--ink);
}
@keyframes pop { 0%{transform:scale(1) translate(2px,2px)} 50%{transform:scale(1.06) translate(2px,2px)} 100%{transform:scale(1) translate(2px,2px)} }
.stButton > button:active { animation: pop 120ms ease; }

.explore-wrap .stButton > button::after { content: " ->"; display: inline-block; transition: transform 120ms ease; }
.explore-wrap .stButton > button:hover::after { transform: translateX(4px); }

.ai-action .stButton > button {
  background: var(--bg) !important;
  border-style: dashed !important;
  font-family: var(--font-mono) !important;
  font-size: 0.85rem;
}

.how-link { color: var(--muted); text-decoration: none; position: relative; display: inline-block; }
.how-link::after {
  content: ""; position: absolute; left: 0; bottom: -2px; height: 2px; width: 100%;
  background: var(--accent); transform: scaleX(0); transform-origin: left; transition: transform 180ms ease;
}
.how-link:hover::after, .how-link:focus-visible::after { transform: scaleX(1); }
.how-link:hover { color: var(--text); }

/* Inputs & selectboxes */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
  border: var(--outline-w) solid var(--ink) !important;
  border-radius: var(--radius) !important;
  background: var(--bg-elev) !important;
  color: var(--text) !important;
  font-family: var(--font-body);
}
[data-baseweb="select"] > div:focus-within,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: none !important;
  outline: 2px solid var(--accent) !important;
  outline-offset: 1px;
}

/* Tabs (Streamlit 1.50+ uses stTabs/stTab; keep legacy BaseWeb selectors) */
[data-testid="stTabs"] [role="tablist"],
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: var(--space-3);
  border-bottom: 1px solid var(--rule);
  flex-wrap: wrap;
  overflow-x: visible;
}
[data-testid="stTabs"] [data-testid="stTab"],
[data-testid="stTabs"] [data-baseweb="tab"] {
  flex: 0 0 auto;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: var(--muted);
  background: transparent;
  border-radius: 0;
  padding: 0.5rem 0;
}
[data-testid="stTabs"] [data-testid="stTab"][data-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] { color: var(--text); }
[data-testid="stTabs"] [data-testid="stTab"] .react-aria-SelectionIndicator,
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--accent); height: 2px; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

[data-testid="stSidebar"] { background: var(--bg-elev); border-right: 1px solid var(--rule); }
[data-testid="stSidebar"] * { color: var(--text); }
/* hide Streamlit chrome but keep sidebar toggle */
footer { visibility: hidden; height: 0; }
#MainMenu { visibility: hidden; }
[data-testid="stDecoration"] { visibility: hidden; height: 0; }
[data-testid="stStatusWidget"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] { display: flex !important; visibility: visible !important; opacity: 1 !important; color: var(--text) !important; }

.card, .stat, .sugg, .hero { background: transparent !important; box-shadow: none !important; border-radius: 0 !important; }
.card { border: none; border-top: 1px solid var(--rule); padding: var(--space-3) 0; margin-top: 0; }
.hero { background: transparent !important; color: var(--text) !important; padding: 0 0 var(--space-4) 0; margin-bottom: var(--space-4); border-bottom: 1px solid var(--rule); }
.hero h1, .hero p { color: var(--text) !important; }
.pill { display: inline-block; padding: 2px 10px; border: var(--outline-w) solid var(--ink); border-radius: 999px; font-family: var(--font-mono); font-size: 0.8rem; font-weight: 500; color: var(--text); background: var(--bg-elev) !important; }
.mono-chip { font-family: var(--font-mono) !important; }
.stat { border: none; border-top: 1px solid var(--rule); padding: var(--space-3) 0; }
.stat b { font-size: clamp(1.6rem, 3vw, 2.2rem); color: var(--text); font-family: var(--font-display); }
.stat span { color: var(--muted); font-size: 0.85rem; display:block; font-family: var(--font-mono); }
.sugg { margin-top: var(--space-2); padding: var(--space-2) 0; border: none; border-top: 1px solid var(--rule); color: var(--text); background: transparent !important; }
.bar { background: var(--rule); border-radius: 4px; overflow: hidden; height: 6px; margin-top: 4px; }
.bar > div { background: var(--accent); height: 100%; }
table.clean { width:100%; border-collapse: collapse; margin: var(--space-3) 0; }
table.clean th, table.clean td { text-align:left; padding: 0.6rem 0.4rem; border-bottom: 1px solid var(--rule); vertical-align: top; }
table.clean th { font-family: var(--font-mono); font-weight: 500; color: var(--muted); font-size: 0.85rem; }
table.clean tr:hover td { background: var(--bg-elev); }
table.clean td.allowed { background: var(--show-bg); color: var(--show-text); }

.step-num { font-size: clamp(1.8rem, 4vw, 2.8rem); color: var(--muted); line-height: 1; margin-right: var(--space-3); min-width: 2.2rem; transition: color 120ms ease; }
.step-row { display:flex; align-items:flex-start; padding: var(--space-3) 0; border-top: 1px solid var(--rule); transition: transform 120ms ease; }
.step-row .step-line { height: 2px; width: 24px; background: var(--rule); margin-top: 0.4rem; margin-right: 0.5rem; transition: background 120ms ease, width 120ms ease; display: inline-block; }
.step-row:hover { transform: translateX(6px); }
.step-row:hover .step-num { color: var(--accent); }
.step-row:hover .step-line { background: var(--accent); width: 40px; }

.numeral { font-size: clamp(2rem, 4vw, 3rem); line-height: 1; color: var(--text); }
.num-label { color: var(--muted); font-size: 0.85rem; margin-top: 0.2rem; font-family: var(--font-mono); }
.demo-row { display:grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: var(--space-2); padding: 0.6rem 0; border-top: 1px solid var(--rule); font-size: 0.95rem; align-items: center; }
.demo-head { color: var(--muted); font-size: 0.8rem; font-weight: 500; font-family: var(--font-mono); }

.decision-pill { display:inline-block; padding: 2px 10px; border-radius: 999px; font-family: var(--font-mono); font-size: 0.8rem; border: var(--outline-w) solid var(--ink); }
.decision-pill.show { background: var(--show-bg); color: var(--show-text); }
.decision-pill.hold { background: var(--hold-bg); color: var(--hold-text); }
.decision-pill.silence { background: var(--silence-bg); color: var(--silence-text); }

.hero-layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: var(--space-5); align-items: start; }
.lanes { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-2); margin-top: var(--space-3); }
.lane { border: var(--outline-w) solid var(--ink); border-radius: var(--radius); background: var(--bg-elev); padding: var(--space-2); min-height: 220px; position: relative; overflow: hidden; }
.lane-title { font-family: var(--font-mono); font-size: 0.8rem; margin-bottom: var(--space-2); padding-bottom: 4px; border-bottom: 1px solid var(--rule); }
.lane-title.show { color: var(--show-text); }
.lane-title.hold { color: var(--hold-text); }
.lane-title.silence { color: var(--silence-text); }
.chip { border: var(--outline-w) solid var(--ink); border-radius: 8px; padding: 6px 8px; font-size: 0.8rem; background: var(--bg); margin-bottom: 6px; position: absolute; left: 8px; right: 8px; box-shadow: 2px 2px 0 var(--ink); }
.lane-show .chip { background: var(--show-bg); color: var(--show-text); }
.lane-hold .chip { background: var(--hold-bg); color: var(--hold-text); }
.lane-silence .chip { background: var(--silence-bg); color: var(--silence-text); }

.inbox-card { border-top: 1px solid var(--rule); padding: var(--space-3) 0; transition: transform 120ms ease, box-shadow 120ms ease; }
.inbox-card:hover { transform: translateY(-2px); box-shadow: 0 4px 0 var(--rule); }
.bar > div.grow { width: var(--w, 0%); }

.toast-notice { border: var(--outline-w) solid var(--ink); border-radius: var(--radius); padding: 0.6rem 1rem; margin: var(--space-2) 0; background: var(--bg-elev); box-shadow: var(--shadow-sm); font-family: var(--font-body); }
.toast-notice.show { background: var(--show-bg); color: var(--show-text); }
.toast-notice.hold { background: var(--hold-bg); color: var(--hold-text); }
.toast-notice.silence { background: var(--silence-bg); color: var(--silence-text); }

@media (max-width: 700px) {
  .demo-row { grid-template-columns: 1fr; gap: 0.2rem; }
  .hero-layout { grid-template-columns: 1fr; }
  .lanes { grid-template-columns: 1fr; }
  .lane { min-height: 120px; }
}

@media (prefers-reduced-motion: no-preference) {
  @keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes dropIn { 0% { opacity: 0; transform: translateY(-40px); } 10% { opacity: 1; transform: translateY(0); } 70% { opacity: 1; transform: translateY(0); } 85% { opacity: 0; transform: translateY(6px); } 100% { opacity: 0; transform: translateY(-40px); } }
  @keyframes slideIn { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
  @keyframes toastInOut { 0% { opacity: 0; transform: translateY(-8px); } 10% { opacity: 1; transform: translateY(0); } 80% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-6px); } }
  @keyframes growBar { from { width: 0; } to { width: var(--w, 0%); } }
  .fade-up { opacity: 0; animation: fadeUp 500ms ease forwards; animation-delay: calc(var(--i, 0) * 80ms); }
  .lane .chip { opacity: 0; animation: dropIn 12s ease-in-out infinite; }
  .chip.c1 { top: 36px; animation-delay: 0s; }
  .chip.c2 { top: 36px; animation-delay: 4s; }
  .chip.c3 { top: 36px; animation-delay: 8s; }
  .demo-row.slide { opacity: 0; animation: slideIn 400ms ease forwards; animation-delay: calc(var(--i, 0) * 80ms); }
  .toast-notice { animation: toastInOut 3s ease forwards; }
  .bar > div.grow { width: 0; animation: growBar 500ms ease forwards; }
  @supports (animation-timeline: view()) {
    .reveal { animation-timeline: view(); animation-range: entry 0% cover 30%; }
  }
}
@media (prefers-reduced-motion: reduce) {
  .fade-up, .demo-row.slide { opacity: 1; transform: none; }
  .lane .chip { opacity: 1; position: static; animation: none; margin-top: 8px; }
  .toast-notice { opacity: 1; animation: none; }
  .bar > div.grow { width: var(--w, 0%); animation: none; }
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
