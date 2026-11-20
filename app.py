"""
Anna Setu Karnataka — Main Streamlit Application
Multi-agent AI Food Rescue & Donation Coordination Platform
"""

import os
import sys
import logging
import warnings
from datetime import datetime, timezone, timedelta

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s")
log = logging.getLogger("annasetu.app")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Anna Setu Karnataka",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS — Orchid Landing palette
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

/* ── Design tokens ── */
:root {
    --bg:         #F5E9FB;
    --bg2:        #FAEDF6;
    --white:      #FFFFFF;
    --primary:    #24112F;
    --purple:     #873DF5;
    --purple-lt:  #B26AF5;
    --purple-dim: rgba(135,61,245,0.08);
    --coral:      #F07886;
    --teal:       #16A69A;
    --card:       #FFFFFF;
    --card-border:rgba(135,61,245,0.13);
    --muted:      #6B5878;
    --radius:     18px;
    --shadow:     0 4px 24px rgba(135,61,245,0.10);
    --shadow-sm:  0 2px 10px rgba(135,61,245,0.07);
}

/* ── Page background ── */
html, body { font-family: 'Inter', -apple-system, system-ui, sans-serif; }

.main .block-container {
    background: linear-gradient(145deg, var(--bg) 0%, var(--bg2) 100%);
    padding: 2rem 2.5rem 4rem;
    max-width: 1300px;
}

/* Force all main-area text to be dark and readable */
.main p, .main li, .main span, .main div,
.main label, .main small, .main caption,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: var(--primary) !important;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: var(--primary) !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #150722 0%, #261044 60%, #1E0D35 100%) !important;
    border-right: 1px solid rgba(178,106,245,0.18);
}
/* Reset all sidebar text to light */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label {
    color: #EAE0F8 !important;
}
/* Sidebar padding tweak */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.5rem !important;
    padding-bottom: 1.5rem !important;
}

/* ── Hide the "Navigation" label Streamlit inserts ── */
section[data-testid="stSidebar"] .stRadio > label:first-child {
    display: none !important;
}

/* ── Radio group: tight column with smooth spacing ── */
section[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    padding: 0 4px !important;
}

/* ── Completely hide all radio circles / dots / icons in Streamlit 1.67+ ── */
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stRadioOption"] > div > div:first-child,
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stRadioOption"] > label > div:first-child,
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stRadioOption"] input[type="radio"],
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stRadioOption"] svg,
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child:not([data-testid="stMarkdownContainer"]),
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label > div:first-child:not([data-testid="stMarkdownContainer"]) {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
}

/* ── Each nav item: sleek, full-width interactive navigation tile ── */
section[data-testid="stSidebar"] [data-testid="stRadioOption"],
section[data-testid="stSidebar"] [data-baseweb="radio"],
section[data-testid="stSidebar"] .stRadio label {
    width: 100% !important;
    margin: 2px 0 !important;
    border-radius: 10px !important;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(178, 106, 245, 0.15) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12) !important;
}

section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div,
section[data-testid="stSidebar"] [data-testid="stRadioOption"] > label,
section[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
}

/* Hover state */
section[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover,
section[data-testid="stSidebar"] [data-baseweb="radio"]:hover,
section[data-testid="stSidebar"] .stRadio label:hover {
    background: linear-gradient(90deg, rgba(135, 61, 245, 0.32) 0%, rgba(178, 106, 245, 0.18) 100%) !important;
    border-color: rgba(178, 106, 245, 0.45) !important;
    transform: translateX(3px) !important;
}

/* Selected Active Navigation State */
section[data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked),
section[data-testid="stSidebar"] [data-testid="stRadioOption"][aria-checked="true"],
section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked),
section[data-testid="stSidebar"] [aria-checked="true"] label,
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: linear-gradient(90deg, rgba(135, 61, 245, 0.65) 0%, rgba(178, 106, 245, 0.4) 100%) !important;
    border: 1px solid #B26AF5 !important;
    border-left: 4px solid #F07886 !important;
    box-shadow: 0 4px 14px rgba(135, 61, 245, 0.4) !important;
}

/* Typography inside radio options */
section[data-testid="stSidebar"] [data-testid="stRadio"] p,
section[data-testid="stSidebar"] [data-testid="stRadio"] span,
section[data-testid="stSidebar"] [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
    line-height: 1.35 !important;
    white-space: normal !important;
}

/* ── Sidebar dividers ── */
section[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid rgba(178,106,245,0.18) !important;
    margin: 8px 10px !important;
}

/* ── Sidebar refresh button ── */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(135,61,245,0.18) !important;
    border: 1px solid rgba(178,106,245,0.3) !important;
    color: #E2D4F5 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    padding: 5px 10px !important;
    box-shadow: none !important;
    margin-top: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(135,61,245,0.35) !important;
    color: #FFFFFF !important;
}
    background: rgba(135,61,245,0.18) !important;
    border: 1px solid rgba(178,106,245,0.3) !important;
    color: #E2D4F5 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    padding: 5px 10px !important;
    box-shadow: none !important;
    margin-top: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(135,61,245,0.35) !important;
    color: #FFFFFF !important;
}

/* ── CARDS ── */
.as-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
    color: var(--primary);
}
.as-card * { color: var(--primary) !important; }
.as-card p, .as-card li, .as-card ul { color: var(--primary) !important; line-height: 1.7; }
.as-card strong { color: var(--purple) !important; font-weight: 700; }

.as-card-sm {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: .6rem;
    color: var(--primary);
}
.as-card-sm * { color: var(--primary) !important; }
.as-card-sm strong { color: var(--purple) !important; }

/* ── KPI METRIC CARDS ── */
.kpi-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.75rem;
}
.kpi {
    flex: 1;
    min-width: 150px;
    background: var(--card);
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    border-left: 4px solid var(--purple);
    box-shadow: var(--shadow-sm);
}
.kpi-val {
    font-size: 2.1rem;
    font-weight: 800;
    color: var(--purple) !important;
    line-height: 1.1;
}
.kpi-lbl {
    font-size: 0.76rem;
    color: var(--muted) !important;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .03em;
}
.kpi-teal  { border-left-color: var(--teal) !important; }
.kpi-teal .kpi-val { color: var(--teal) !important; }
.kpi-coral { border-left-color: var(--coral) !important; }
.kpi-coral .kpi-val { color: var(--coral) !important; }

/* ── STATUS BADGES ── */
.badge {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.badge-green  { background: #d1fae5; color: #065f46 !important; }
.badge-red    { background: #fee2e2; color: #991b1b !important; }
.badge-yellow { background: #fef9c3; color: #854d0e !important; }
.badge-purple { background: #ede9fe; color: #5b21b6 !important; }
.badge-blue   { background: #dbeafe; color: #1d4ed8 !important; }
.badge-teal   { background: #ccfbf1; color: #0f766e !important; }
.badge-gray   { background: #f3f4f6; color: #374151 !important; }

/* ── HERO ── */
.as-hero {
    text-align: center;
    padding: 3.5rem 1rem 1.5rem;
    background: linear-gradient(145deg, rgba(135,61,245,0.06), rgba(240,120,134,0.06));
    border-radius: 24px;
    margin-bottom: 2rem;
    border: 1px solid rgba(135,61,245,0.1);
}
.as-hero h1 {
    font-size: 3rem;
    font-weight: 800;
    color: var(--primary) !important;
    line-height: 1.18;
    margin-bottom: .75rem;
}
.as-hero h1 em { font-style: normal; color: var(--purple) !important; }
.as-hero .sub {
    font-size: 1.1rem;
    color: var(--muted) !important;
    max-width: 580px;
    margin: 0 auto 1.5rem;
    line-height: 1.65;
}
.as-hero .pill-row {
    display: flex;
    gap: .6rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.as-hero .pill {
    background: rgba(135,61,245,0.10);
    color: var(--purple) !important;
    border: 1px solid rgba(135,61,245,0.2);
    border-radius: 999px;
    padding: 5px 16px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── SECTION HEADERS ── */
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--primary) !important;
    margin-bottom: 1rem;
    padding-bottom: .5rem;
    border-bottom: 2px solid rgba(135,61,245,0.15);
    display: flex;
    align-items: center;
    gap: .5rem;
}

/* ── ALERT BOXES ── */
.alert-safe   { background: #ecfdf5; border:1px solid #6ee7b7; border-radius: 12px; padding: .85rem 1.1rem; color: #065f46 !important; font-weight: 500; margin-bottom:.75rem; }
.alert-warn   { background: #fffbeb; border:1px solid #fcd34d; border-radius: 12px; padding: .85rem 1.1rem; color: #92400e !important; font-weight: 500; margin-bottom:.75rem; }
.alert-danger { background: #fef2f2; border:1px solid #fca5a5; border-radius: 12px; padding: .85rem 1.1rem; color: #991b1b !important; font-weight: 500; margin-bottom:.75rem; }
.alert-info   { background: #eff6ff; border:1px solid #93c5fd; border-radius: 12px; padding: .85rem 1.1rem; color: #1e40af !important; font-weight: 500; margin-bottom:.75rem; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #873DF5, #B26AF5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: .55rem 1.6rem !important;
    font-size: 0.88rem !important;
    transition: opacity .2s, transform .1s !important;
    box-shadow: 0 4px 14px rgba(135,61,245,0.3) !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── DATAFRAME ── */
.stDataFrame { border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-sm); }

/* ── AGENT STRIP ── */
.agent-strip {
    display: flex;
    gap: .5rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
    padding: .75rem 1rem;
    background: var(--card);
    border-radius: 14px;
    border: 1px solid var(--card-border);
}
.agent-pill {
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.a1 { background: #ede9fe; color: #5b21b6 !important; }
.a2 { background: #ccfbf1; color: #0f766e !important; }
.a3 { background: #fef9c3; color: #854d0e !important; }
.a4 { background: #dbeafe; color: #1d4ed8 !important; }

/* ── CREDS TABLE ── */
.creds-table { width:100%; border-collapse:collapse; font-size:.85rem; }
.creds-table th { background: rgba(135,61,245,0.08); color: var(--purple) !important; padding: 9px 14px; text-align:left; font-weight:700; border-bottom:2px solid rgba(135,61,245,0.15); }
.creds-table td { padding: 9px 14px; border-bottom: 1px solid #f0eaf8; color: var(--primary) !important; }
.creds-table tr:last-child td { border-bottom: none; }
.creds-table tr:hover td { background: rgba(135,61,245,0.04); }

/* ── AGENT FEATURE CARDS ── */
.agent-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:.5rem; }
.agent-feat-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow-sm);
}
.agent-feat-card .af-title { font-size:.95rem; font-weight:700; margin-bottom:.4rem; }
.agent-feat-card .af-desc  { font-size:.82rem; color: var(--muted) !important; line-height:1.6; }

/* ── FORM INPUTS — keep labels readable ── */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stTextArea label, .stDateInput label, .stTimeInput label {
    color: var(--primary) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
}
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid rgba(135,61,245,0.2) !important;
    color: var(--primary) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--purple) !important;
    box-shadow: 0 0 0 3px rgba(135,61,245,0.12) !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: rgba(135,61,245,0.05) !important;
    border-radius: 10px !important;
    color: var(--primary) !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE BOOTSTRAP
# ─────────────────────────────────────────────
def _init_session():
    defaults = {
        "authenticated": False,
        "user": None,
        "page": "home",
        "agents_ready": False,
        "db_ready": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# ─────────────────────────────────────────────
# ONE-TIME STARTUP
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising Anna Setu platform…")
def startup():
    import database as db
    import agents as ag
    db.init_schema()
    try:
        c = db.execute_query("SELECT COUNT(*) AS c FROM as_users")
        if not c or c[0]["c"] == 0:
            db.seed_demo_data()
    except Exception:
        db.seed_demo_data()
    ag.initialise_agents()
    return {"db": True, "ai": ag.get_ai_status()}


def refresh_ai_status():
    """Re-probe Gemini/Granite and update session state without full restart."""
    import agents as ag
    ag._init_gemini()
    ag._init_granite()
    st.session_state["ai_status"] = ag.get_ai_status()


try:
    _startup = startup()
    st.session_state["db_ready"] = True
    if "ai_status" not in st.session_state or not st.session_state["ai_status"]:
        st.session_state["ai_status"] = _startup.get("ai", {})
except Exception as e:
    st.error(f"⚠️ Startup error: {e}")
    st.stop()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def status_badge(status: str) -> str:
    mapping = {
        "pending_screening": ("yellow", "Pending Screening"),
        "screening_passed":  ("green",  "Screening Passed"),
        "screening_failed":  ("red",    "Screening Failed"),
        "pending_review":    ("yellow", "Pending Review"),
        "matched":           ("teal",   "Matched"),
        "collected":         ("blue",   "Collected"),
        "delivered":         ("green",  "Delivered"),
        "cancelled":         ("gray",   "Cancelled"),
        "proposed":          ("purple", "Proposed"),
        "admin_approved":    ("green",  "Approved"),
        "admin_rejected":    ("red",    "Rejected"),
        "volunteer_assigned":("teal",   "Volunteer Assigned"),
        "assigned":          ("blue",   "Assigned"),
        "accepted":          ("teal",   "Accepted"),
        "at_pickup":         ("yellow", "At Donor Pickup"),
        "picked_up":         ("teal",   "Picked Up"),
        "in_transit":        ("blue",   "In Transit"),
        "arrived_destination": ("green", "Arrived at Destination 🏁"),
        "delayed":           ("yellow", "Delayed"),
        "failed":            ("red",    "Failed"),
        "pending":           ("yellow", "Pending"),
        "approved":          ("green",  "Approved"),
        "rejected":          ("red",    "Rejected"),
    }
    color, label = mapping.get(status, ("gray", status or "—"))
    return f'<span class="badge badge-{color}">{label}</span>'


def kpi_card(value, label: str, variant: str = "") -> str:
    extra = f" kpi-{variant}" if variant else ""
    return (f'<div class="kpi{extra}">'
            f'<div class="kpi-val">{value}</div>'
            f'<div class="kpi-lbl">{label}</div></div>')


def ai_status_bar():
    ai = st.session_state.get("ai_status", {})
    gemini_model = ai.get("gemini_model", "")
    gemini_label = (f"🟢 Gemini: {gemini_model}" if ai.get("gemini_available")
                    else "🔴 Gemini Offline")
    granite_label = "🟢 Granite Online" if ai.get("granite_available") else "🔴 Granite Offline"
    gemini_error  = ai.get("gemini_error", "")
    st.markdown(
        f'<div class="agent-strip">'
        f'<span class="agent-pill a1">🤖 Agent 1 — Donation &amp; Safety</span>'
        f'<span class="agent-pill a2">🤖 Agent 2 — Matching &amp; Priority</span>'
        f'<span class="agent-pill a3">🤖 Agent 3 — Logistics</span>'
        f'<span class="agent-pill a4">🤖 Agent 4 — Delivery &amp; Impact</span>'
        f'<span class="badge badge-{"green" if ai.get("gemini_available") else "red"}">{gemini_label}</span>'
        f'<span class="badge badge-{"green" if ai.get("granite_available") else "red"}">{granite_label}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    if not ai.get("gemini_available") and gemini_error:
        st.caption(f"ℹ️ Gemini: {gemini_error[:120]}")


def require_role(*roles):
    if not st.session_state.get("authenticated"):
        st.error("Please log in to access this page.")
        st.stop()
    user = st.session_state["user"]
    if user["role"] not in roles:
        st.error(f"Access denied. This page requires role: {', '.join(roles)}")
        st.stop()
    return user


def fmt_dt(val) -> str:
    if not val:
        return "—"
    if isinstance(val, str):
        try:
            val = datetime.fromisoformat(val.replace("Z", "+00:00"))
        except Exception:
            return val
    if isinstance(val, datetime):
        return val.strftime("%d %b %Y %H:%M")
    return str(val)


# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

def page_home():
    # ── Hero ──
    st.markdown("""
    <div class="as-hero">
        <h1>Rescue surplus food.<br><em>Deliver hope where it matters.</em></h1>
        <p class="sub">Connecting food donors, community organisations and volunteers through
        intelligent food redistribution — powered by AI agents across Karnataka.</p>
        <div class="pill-row">
            <span class="pill">🤖 4 AI Agents</span>
            <span class="pill">🛡️ 9 Guardrail Categories</span>
            <span class="pill">🗺️ Bengaluru &amp; Beyond</span>
            <span class="pill">📊 Real-time Impact Tracking</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Action buttons ──
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("🚨 Find Immediate Food Support", use_container_width=True, key="home_btn_emergency"):
            st.session_state["nav_override"] = "🚨 Find Immediate Food Support"
            st.rerun()
    with btn_col2:
        if st.button("🚚 Track Food Delivery & Driver", use_container_width=True, key="home_btn_track"):
            st.session_state["nav_override"] = "🚚 Track Food Delivery & Driver"
            st.rerun()
    with btn_col3:
        if st.button("🔍 Explore Support Organisations", use_container_width=True, key="home_btn_explore"):
            st.session_state["nav_override"] = "🔍 Explore Organisations"
            st.rerun()

    st.write("")

    # ── Live KPI strip ──
    import tools as t
    import database as db
    report = t.generate_impact_report()
    org_counts = t.get_organisation_counts()
    reg_donors = len(t.get_all_donor_orgs())
    all_donations = t.get_all_donations()
    active_donations = len([d for d in all_donations if d.get("status") in
                             ("pending_screening", "screening_passed", "matched")])
    try:
        active_requests = db.execute_query(
            "SELECT COUNT(*) AS c FROM recipient_requests WHERE status IN ('submitted','referred_to_org')"
        )[0]['c']
        urgent_requests = db.execute_query(
            "SELECT COUNT(*) AS c FROM recipient_requests WHERE urgency_level IN ('Urgent','Critical')"
        )[0]['c']
    except Exception:
        active_requests = 0
        urgent_requests = 0
    recent_matches = len(t.get_matches_with_details())

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(reg_donors,       "Donor Organisations")
        + kpi_card(active_donations,  "Active Donations", "teal")
        + kpi_card(active_requests,   "Open Recipient Requests")
        + kpi_card(org_counts.get("real_count", 0), "Support Organisations", "coral")
        + kpi_card(urgent_requests,   "Urgent Requests", "coral")
        + kpi_card(recent_matches,    "Total Matches", "teal")
        + '</div>',
        unsafe_allow_html=True
    )

    # ── AI Agent status ──
    ai_status_bar()

    st.write("")

    # ── About + Credentials row ──
    col_about, col_creds = st.columns([1, 1], gap="large")

    with col_about:
        st.markdown("""
        <div class="as-card">
          <div class="section-title">🌾 About Anna Setu Karnataka</div>
          <p>Anna Setu (<em>ಅನ್ನ ಸೇತು</em> — Bridge of Food) is an intelligent food rescue
          coordination platform that connects surplus food from restaurants, hotels,
          wedding halls and canteens to shelters, orphanages, old-age homes and
          community kitchens across Karnataka.</p>
          <ul style="margin-top:.75rem;padding-left:1.2rem">
            <li>🤖 Four specialised AI agents coordinate the full donation lifecycle</li>
            <li>🛡️ Nine-category guardrails ensure food safety and data security</li>
            <li>🗺️ Volunteer and transport coordination for Bengaluru and beyond</li>
            <li>📊 Real-time impact tracking with confirmed delivery data only</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_creds:
        st.markdown("""
        <div class="as-card">
          <div class="section-title">🔑 Demo Login Credentials</div>
          <table class="creds-table">
            <thead>
              <tr><th>Username</th><th>Password</th><th>Role</th></tr>
            </thead>
            <tbody>
              <tr><td><strong>donor_raj</strong></td><td>Demo@1234</td>
                  <td><span class="badge badge-teal">Donor</span></td></tr>
              <tr><td><strong>donor_priya</strong></td><td>Demo@1234</td>
                  <td><span class="badge badge-teal">Donor</span></td></tr>
              <tr><td><strong>recipient_hope</strong></td><td>Demo@1234</td>
                  <td><span class="badge badge-blue">Recipient</span></td></tr>
              <tr><td><strong>volunteer_arjun</strong></td><td>Demo@1234</td>
                  <td><span class="badge badge-yellow">Volunteer</span></td></tr>
              <tr><td><strong>admin</strong></td><td>Admin@1234</td>
                  <td><span class="badge badge-purple">Admin</span></td></tr>
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Four Agents section ──
    st.write("")
    st.markdown('<div class="section-title">🔄 Four Coordinated AI Agents</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="agent-grid">
      <div class="agent-feat-card">
        <div class="af-title" style="color:#5b21b6">🤖 Agent 1 — Donation &amp; Safety</div>
        <div class="af-desc">Registers donations, runs FSSAI-guided food safety screening using
        IBM Granite, flags uncertain cases for mandatory human review before any matching.</div>
      </div>
      <div class="agent-feat-card">
        <div class="af-title" style="color:#0f766e">🤖 Agent 2 — Matching &amp; Priority</div>
        <div class="af-desc">Matches food to recipients by dietary compatibility, capacity and
        urgency. Provides explainable scoring using Python rules + Gemini narrative.</div>
      </div>
      <div class="agent-feat-card">
        <div class="af-title" style="color:#854d0e">🤖 Agent 3 — Collection &amp; Logistics</div>
        <div class="af-desc">Assigns available volunteers and transport based on vehicle capacity
        and location. Coordinates pickup schedules and handles cancellations.</div>
      </div>
      <div class="agent-feat-card">
        <div class="af-title" style="color:#1d4ed8">🤖 Agent 4 — Delivery &amp; Impact</div>
        <div class="af-desc">Tracks delivery lifecycle, enforces recipient acknowledgement before
        marking complete, and generates impact reports from confirmed PostgreSQL records only.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PHASE 2 PAGES: EXPLORE & IMMEDIATE SUPPORT
# ─────────────────────────────────────────────

def page_explore_organisations():
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🔍 Explore Food Support Organisations in Bengaluru</div>', unsafe_allow_html=True)
    st.caption("Browse and filter the directory of verified community food support organizations, food banks, redistribution networks, and partner institutions without needing to submit a request.")

    ai_status_bar()

    # Filters row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        locality_filter = st.selectbox(
            "Locality",
            ["All", "Yelahanka", "Hebbal", "Shivaji Nagar", "R.T. Nagar", "Peenya", "Kalyan Nagar", "Hennur", "Richmond Town", "Frazer Town", "Indiranagar", "Whitefield", "Koramangala", "Bengaluru Urban"]
        )
    with col2:
        type_filter = st.selectbox(
            "Organisation Type",
            ["All", "food_bank", "food_redistribution_org", "community_kitchen", "ngo", "shelter", "orphanage", "old_age_home"]
        )
    with col3:
        cat_filter = st.selectbox(
            "Food Category",
            ["All", "cooked_meals", "packaged", "raw_produce", "grains", "any"]
        )
    with col4:
        avail_filter = st.selectbox(
            "Availability Status",
            ["All", "confirmed_available", "contact_to_confirm", "unknown", "temporarily_unavailable"]
        )

    fcol1, fcol2 = st.columns([3, 1])
    with fcol1:
        search_query = st.text_input("🔎 Search by organisation name, address, or service keywords", placeholder="e.g. Bangalore Food Bank, Hennur, cooked meals...")
    with fcol2:
        st.write("")
        st.write("")
        include_demo = st.checkbox("Include Demo Records", value=False, help="Show clearly marked fictional demo records")

    # Fetch records with parameterised search
    records, total_count = t.get_support_organisations_directory(
        locality=locality_filter if locality_filter != "All" else None,
        org_type=type_filter if type_filter != "All" else None,
        food_category=cat_filter if cat_filter != "All" else None,
        availability_status=avail_filter if avail_filter != "All" else None,
        search_query=search_query if search_query else None,
        include_demo=include_demo,
        limit=200
    )

    st.markdown(f"**Showing {len(records)} organisations matching filters** (Total in directory: {total_count})")

    # Coordinates map view if real coordinates exist
    coord_records = [
        {"lat": float(r["latitude"]), "lon": float(r["longitude"]), "name": r["organisation_name"]}
        for r in records if r.get("latitude") is not None and r.get("longitude") is not None
    ]
    if coord_records:
        with st.expander(f"🗺️ View {len(coord_records)} mapped organisations on Bengaluru map", expanded=False):
            st.map(pd.DataFrame(coord_records))

    if not records:
        st.info("No organisations match your selected filters. Try broadening your locality or food category filters.")
        return

    # Render organisation cards
    for org in records:
        is_synthetic = org.get("is_synthetic", False)
        avail = org.get("availability_status", "unknown")
        can_dist = org.get("can_distribute_food", False)
        is_ben = org.get("is_beneficiary_institution", False)

        with st.container():
            st.markdown('<div class="as-card">', unsafe_allow_html=True)

            # Badges header
            title_badges = []
            title_badges.append(f'<span class="badge badge-purple">{org.get("organisation_type", "").replace("_", " ").title()}</span>')
            if is_synthetic:
                title_badges.append('<span class="badge badge-red">DEMO DATA — not a real organisation</span>')

            if avail == "confirmed_available":
                title_badges.append('<span class="badge badge-green">Confirmed Available</span>')
            else:
                title_badges.append('<span class="badge badge-yellow">Availability not confirmed — contact organisation</span>')

            if can_dist:
                title_badges.append('<span class="badge badge-teal">Food Provider</span>')
            elif is_ben:
                title_badges.append('<span class="badge badge-blue">Beneficiary Institution</span>')

            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">'
                f'<h3 style="margin:0;font-size:1.15rem;color:var(--primary);">{org["organisation_name"]}</h3>'
                f'<div>{" ".join(title_badges)}</div></div>',
                unsafe_allow_html=True
            )

            # Details
            col_a, col_b = st.columns([3, 2])
            with col_a:
                addr = org.get("address") or org.get("locality") or "Bengaluru"
                st.markdown(f"📍 **Address / Locality:** {addr}")
                if org.get("food_services"):
                    st.markdown(f"ℹ️ **Services:** {org['food_services']}")
                if org.get("food_categories_supported"):
                    st.markdown(f"🥗 **Categories Supported:** {org['food_categories_supported']}")
                if org.get("beneficiary_type"):
                    st.caption(f"Beneficiaries Served: {org['beneficiary_type']}")

            with col_b:
                phone = org.get("contact_phone")
                email = org.get("contact_email")
                website = org.get("website_url")
                directions_url = t.build_directions_url(org["organisation_name"], org.get("address", "") or org.get("locality", ""), org.get("city", "Bengaluru"))

                if phone:
                    clean_phone = phone.replace(" ", "").replace("-", "")
                    st.markdown(f'📞 **Phone:** <a href="tel:{clean_phone}">{phone}</a>', unsafe_allow_html=True)
                else:
                    st.markdown("📞 **Phone:** Not available")

                if email:
                    st.markdown(f'✉️ **Email:** <a href="mailto:{email}">{email}</a>', unsafe_allow_html=True)
                else:
                    st.markdown("✉️ **Email:** Not available")

                action_links = []
                if website:
                    action_links.append(f'<a href="{website}" target="_blank" style="text-decoration:none;font-weight:600;color:var(--purple);">🌐 Visit Website</a>')
                action_links.append(f'<a href="{directions_url}" target="_blank" style="text-decoration:none;font-weight:600;color:var(--teal);">🗺️ Directions</a>')
                st.markdown(" | ".join(action_links), unsafe_allow_html=True)

            # Disclaimer
            src_name = org.get("source_name", "Public Directory")
            src_url = org.get("source_url", "#")
            verified_date = org.get("last_verified_at")
            vdate_str = verified_date.strftime("%d %b %Y") if hasattr(verified_date, "strftime") else (str(verified_date)[:10] if verified_date else "2026-11-19")
            st.markdown(
                f'<div style="font-size:0.75rem;color:var(--muted);margin-top:8px;border-top:1px dashed var(--border);padding-top:4px;">'
                f'Listing is from <a href="{src_url}" target="_blank">{src_name}</a> checked on {vdate_str}. '
                f'This does not confirm food is available.</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)


def page_find_immediate_support():
    import tools as t
    import agents as ag
    import guardrails as g

    st.markdown('<div class="section-title">🚨 Find Immediate Food Support</div>', unsafe_allow_html=True)
    st.caption("Submit your emergency food requirement to check for active surplus food donations in Bengaluru or instantly discover verified local food-support organisations.")

    ai_status_bar()

    with st.form("emergency_request_form"):
        st.markdown("#### 1. Requirements & Location")
        col1, col2 = st.columns(2)
        with col1:
            locality = st.text_input("Bengaluru Locality / Area *", value="Yelahanka", placeholder="e.g. Yelahanka, Hebbal, Indiranagar, Peenya")
            food_category = st.selectbox(
                "Food Category Needed *",
                ["cooked_meals", "raw_produce", "packaged", "dairy", "bakery", "any"],
                index=0,
                format_func=lambda x: {
                    "cooked_meals": "Cooked Meals (Ready to eat)",
                    "raw_produce": "Raw Groceries / Fresh Produce",
                    "packaged": "Packaged Rations / Dry Food",
                    "dairy": "Dairy / Milk Products",
                    "bakery": "Bakery / Bread",
                    "any": "Any Available Food"
                }.get(x, x)
            )
        with col2:
            quantity = st.number_input("Quantity Needed (Meals / Food Packets) *", min_value=1, max_value=10000, value=50, step=10)
            people_count = st.number_input("Number of People to Feed *", min_value=1, max_value=5000, value=50, step=5)

        st.markdown("#### 2. Timing & Urgency")
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            time_window = st.selectbox(
                "When is food needed by? *",
                [
                    "Within 2 hours (Immediate Crisis)",
                    "Within 3 hours",
                    "Within 6 hours",
                    "Within 12 hours",
                    "Today Evening (18-24 hours)"
                ],
                index=0
            )
        with time_col2:
            user_urgency = st.selectbox(
                "Self-Assessed Urgency Level",
                ["Critical", "Urgent", "Normal"],
                index=0,
                help="Critical: immediate crisis, no meal available today for vulnerable groups; Urgent: needed today; Normal: scheduled support."
            )

        special_needs = st.text_area(
            "Special Needs / Vulnerability Context (Optional)",
            value="Children and elderly in urgent need of dinner",
            placeholder="e.g. 50 children in community shelter with no dinner today; diabetic dietary restrictions, etc."
        )

        st.markdown("#### 3. Contact Information (Optional — Anonymous Submissions Allowed)")
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            requester_name = st.text_input("Contact Name (Optional)", placeholder="Leave blank to stay anonymous")
        with c_col2:
            requester_phone = st.text_input("Phone Number (Optional)", placeholder="For donor/volunteer callback")
        with c_col3:
            demo_mode = st.checkbox("Include Demo Records", value=False, help="Include fictional demo records for testing")

        submitted = st.form_submit_button("🔍 Find Food Support Now", use_container_width=True)

    if submitted or st.session_state.get("last_emergency_request"):
        if submitted:
            now = datetime.now(timezone.utc)
            if "2 hours" in time_window:
                req_dt = now + timedelta(hours=2)
            elif "3 hours" in time_window:
                req_dt = now + timedelta(hours=3)
            elif "6 hours" in time_window:
                req_dt = now + timedelta(hours=6)
            elif "12 hours" in time_window:
                req_dt = now + timedelta(hours=12)
            else:
                req_dt = now + timedelta(hours=18)

            req_payload = {
                "locality": locality,
                "food_category": food_category,
                "quantity": int(quantity),
                "people_count": int(people_count),
                "required_by_time": req_dt,
                "urgency_level": user_urgency,
                "special_needs": special_needs,
                "requester_name": requester_name or None,
                "requester_phone": requester_phone or None,
                "is_anonymous": not bool(requester_name or requester_phone),
                "user_id": st.session_state.get("user", {}).get("id") if st.session_state.get("authenticated") else None,
            }
            with st.spinner("Agent 1 screening request… Agent 2 searching active donors & organizations…"):
                result_state = ag.run_recipient_emergency_workflow(req_payload, include_demo=demo_mode)
            st.session_state["last_emergency_request"] = result_state

        result_state = st.session_state.get("last_emergency_request", {})

        if not result_state.get("validation_passed"):
            st.error(f"Request validation failed: {', '.join(result_state.get('errors', []))}")
            return

        urgency = result_state.get("urgency_level", "Normal")
        reason = result_state.get("urgency_reason", "")
        u_badge_class = "badge-red" if urgency == "Critical" else ("badge-yellow" if urgency == "Urgent" else "badge-blue")

        st.markdown(
            f'<div class="as-card">'
            f'<strong>Assigned Urgency:</strong> <span class="badge {u_badge_class}">{urgency}</span><br>'
            f'<small style="color:var(--muted);">{reason}</small>'
            f'</div>',
            unsafe_allow_html=True
        )

        donor_matches = result_state.get("donor_matches", [])
        if donor_matches:
            st.markdown("### 🍱 Active Food Donor Offers Found")
            st.success(f"We found {len(donor_matches)} active food donation offer(s) matching your criteria.")
            for dm in donor_matches:
                with st.container():
                    st.markdown(
                        f'<div class="as-card">'
                        f'<h4>{dm.get("food_name")}</h4>'
                        f'<p><strong>Donor:</strong> {dm.get("donor_name")} | <strong>Available Qty:</strong> {dm.get("available_quantity")} meals | '
                        f'<strong>Location:</strong> {dm.get("donor_address")}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
        else:
            # EXACT BANNER REQUIRED BY SPEC
            st.markdown(
                f'<div class="alert-warn" style="font-size:1.05rem;font-weight:600;margin:1.25rem 0;border-left:5px solid #854d0e;">'
                f'⚠️ {result_state.get("banner_message")}'
                f'</div>',
                unsafe_allow_html=True
            )

            discovered = result_state.get("discovered_organisations", [])
            if discovered:
                st.markdown(f"### 🏛️ Verified Food Support Organisations ({len(discovered)} Found)")

                for idx, org in enumerate(discovered):
                    is_synthetic = org.get("is_synthetic", False)
                    avail = org.get("availability_status", "unknown")
                    score = org.get("match_score", 0)

                    st.markdown('<div class="as-card">', unsafe_allow_html=True)

                    badges = [
                        f'<span class="badge badge-purple">{org.get("organisation_type", "").replace("_", " ").title()}</span>',
                        f'<span class="badge badge-teal">Match Score: {score}</span>'
                    ]
                    if is_synthetic:
                        badges.append('<span class="badge badge-red">DEMO DATA — not a real organisation</span>')

                    if avail == "confirmed_available":
                        badges.append('<span class="badge badge-green">Confirmed Available</span>')
                    else:
                        badges.append('<span class="badge badge-yellow">Availability not confirmed — contact organisation</span>')

                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">'
                        f'<h4 style="margin:0;font-size:1.15rem;color:var(--primary);">{org["organisation_name"]}</h4>'
                        f'<div>{" ".join(badges)}</div></div>',
                        unsafe_allow_html=True
                    )

                    c1, c2 = st.columns([3, 2])
                    with c1:
                        addr = org.get("address") or org.get("locality") or "Bengaluru"
                        st.markdown(f"📍 **Address:** {addr}")
                        st.markdown(f"📏 **Distance:** {org.get('distance_str', 'Distance not available')}")
                        st.markdown(f"💡 **Recommendation Reason:** {org.get('match_reason')}")
                        if org.get("llm_explanation"):
                            st.info(f"🤖 **AI Analysis:** {org['llm_explanation']}")
                        if org.get("food_services"):
                            st.caption(f"Services: {org['food_services']}")

                    with c2:
                        phone = org.get("contact_phone")
                        email = org.get("contact_email")
                        website = org.get("website_url")
                        directions_url = org.get("directions_url")

                        if phone:
                            clean_phone = phone.replace(" ", "").replace("-", "")
                            st.markdown(f'📞 <a href="tel:{clean_phone}" style="font-weight:700;font-size:1.05rem;color:var(--purple);">Call {phone}</a>', unsafe_allow_html=True)
                        else:
                            st.markdown("📞 Phone: Not available")

                        if email:
                            st.markdown(f'✉️ <a href="mailto:{email}">Send Email</a>', unsafe_allow_html=True)

                        links = []
                        if website:
                            links.append(f'<a href="{website}" target="_blank">🌐 Website</a>')
                        if directions_url:
                            links.append(f'<a href="{directions_url}" target="_blank">🗺️ Directions</a>')
                        if links:
                            st.markdown(" | ".join(links), unsafe_allow_html=True)

                        # "I contacted this organisation" interactive recording
                        contact_key = f"contact_expander_{org.get('organisation_id')}_{idx}"
                        with st.expander("📝 I contacted this organisation", expanded=False):
                            outcome = st.selectbox(
                                "Contact Outcome",
                                ["got_help", "no_answer", "not_available", "other"],
                                format_func=lambda x: {
                                    "got_help": "Got food / assistance",
                                    "no_answer": "No answer / unreachable",
                                    "not_available": "No food available",
                                    "other": "Other outcome"
                                }.get(x, x),
                                key=f"outcome_{org.get('organisation_id')}_{idx}"
                            )
                            notes = st.text_input("Brief Note (Optional)", key=f"notes_{org.get('organisation_id')}_{idx}")
                            if st.button("Save Contact Record", key=f"btn_rec_{org.get('organisation_id')}_{idx}"):
                                t.record_recipient_contact(
                                    request_id=result_state.get("request_id"),
                                    organisation_id=org["organisation_id"],
                                    action="marked_contacted",
                                    outcome=outcome,
                                    details=notes
                                )
                                st.success("✅ Thank you! Contact action logged in audit trail.")

                    src_name = org.get("source_name", "Public Directory")
                    src_url = org.get("source_url", "#")
                    verified_date = org.get("last_verified_at")
                    vdate_str = verified_date.strftime("%d %b %Y") if hasattr(verified_date, "strftime") else (str(verified_date)[:10] if verified_date else "2026-11-19")
                    st.markdown(
                        f'<div style="font-size:0.75rem;color:var(--muted);margin-top:8px;border-top:1px dashed var(--border);padding-top:4px;">'
                        f'Listing is from <a href="{src_url}" target="_blank">{src_name}</a> checked on {vdate_str}. '
                        f'This does not confirm food is available.</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

            else:
                general = result_state.get("general_contacts", [])
                st.warning("No verified local food organisations could be matched for this specific locality and category.")
                st.markdown("### 🚨 Verified Emergency Helplines & Crisis Contacts")
                for c in general:
                    st.markdown(
                        f'<div class="as-card-sm" style="margin-bottom:0.75rem;">'
                        f'<strong>{c["contact_name"]}</strong> — <a href="tel:{c["phone"]}" style="font-weight:700;color:var(--coral);">📞 {c["phone"]}</a><br>'
                        f'<small>{c.get("description")}</small><br>'
                        f'<small style="color:var(--muted);">Source: <a href="{c.get("source_url")}" target="_blank">{c.get("source_name")}</a></small>'
                        f'</div>',
                        unsafe_allow_html=True
                    )


    else:
        st.markdown("""
        <div class="as-card" style="text-align: center; padding: 2.2rem 1.5rem; margin-top: 1.25rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">🌾 ➔ 🚚 ➔ 🏠</div>
            <h3 style="color: #1E1035; font-weight: 900; margin-bottom: 0.5rem; font-size: 1.25rem;">Multi-Agent Food Support Matching</h3>
            <p style="color: var(--muted); max-width: 620px; margin: 0 auto 1.25rem; font-size: 0.92rem; line-height: 1.5;">
                Select your Bengaluru locality and food requirements above, then click <strong>Find Food Support Now</strong>.
                Our multi-agent system will screen your emergency request, match active surplus food donations, and filter verified community food support organisations in your area.
            </p>
            <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
                <span class="badge badge-purple">🤖 Agent 1: Intake &amp; Urgency</span>
                <span class="badge badge-teal">🔍 Agent 2: Organisation Discovery</span>
                <span class="badge badge-yellow">🛡️ Guardrail Verified</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def page_login():
    st.markdown('<div class="section-title">🔐 Anna Setu Portal Access</div>', unsafe_allow_html=True)
    
    # ── Clean, visually clear toggle between Login & Sign Up ──
    auth_mode = st.radio(
        "Select Portal Mode",
        ["🔑 Login", "📝 Sign Up"],
        horizontal=True,
        label_visibility="collapsed",
        key="auth_mode_selector"
    )
    st.write("")

    if auth_mode == "🔑 Login":
        render_login_view()
    else:
        render_signup_view()


def render_login_view():
    st.markdown("### 🔑 Account Login")
    st.caption("Sign in with your registered mobile number and password.")
    import database as db
    from guardrails import sanitise_text, check_prompt_injection

    with st.form("login_form"):
        mobile_num = st.text_input("Mobile Number", placeholder="10-digit mobile number (e.g. 9876543210)", key="login_mobile_field")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass_field")
        submitted = st.form_submit_button("Login to Dashboard →", use_container_width=True)

    if submitted:
        m = sanitise_text(mobile_num, 80).strip()
        if not m or not password:
            st.error("Please enter both your mobile number and password.")
            return

        safe, reason = check_prompt_injection(m)
        if not safe:
            st.error(f"Invalid input: {reason}")
            return

        user = db.authenticate(m, password)
        if not user:
            st.error("❌ Invalid mobile number or password. Please verify your credentials or select 'Sign Up' to create an account.")
            return

        # Check account approval status
        if not user.get("is_active", True) or not user.get("is_approved", True):
            st.warning("⏳ Your account is currently awaiting administrative approval. Our operational team will verify your credentials shortly.")
            return

        st.session_state["authenticated"] = True
        st.session_state["user"] = user
        from database import log_audit
        log_audit(user["id"], user["username"], user["role"], "login")
        st.success(f"Welcome back, {user['full_name']}! ({user['role'].title()})")
        st.rerun()


def render_signup_view():
    st.markdown("### 🤝 Volunteer & Transport Partner Onboarding")
    st.markdown("""
    <p style="color:var(--primary);line-height:1.6;">
    Join Karnataka's agentic food rescue network! Whether you are a student, NGO member, vehicle owner, 
    or commercial logistics partner, you help ensure surplus food never goes to waste.
    </p>
    """, unsafe_allow_html=True)

    partner_type = st.radio(
        "Select Your Onboarding Category",
        ["Individual Community Volunteer", "Logistics & Fleet Transport Partner"],
        horizontal=True,
        key="onboarding_category_choice"
    )

    import tools as t
    import database as db
    from guardrails import check_prompt_injection, sanitise_text

    if partner_type == "Individual Community Volunteer":
        with st.form("form_volunteer_join"):
            st.markdown("#### 🚴 Volunteer Information")
            c1, c2 = st.columns(2)
            with c1:
                v_name = st.text_input("Full Name *", placeholder="e.g. Rohini Sharma")
                v_phone = st.text_input("Mobile Number *", placeholder="10-digit mobile number")
                v_locality = st.selectbox(
                    "Primary Bengaluru Locality *",
                    ["Indiranagar", "Koramangala", "Whitefield", "Yelahanka", "Jayanagar", 
                     "Malleshwaram", "HSR Layout", "Majestic", "Electronic City", "Hebbal", 
                     "Banashankari", "Rajajinagar", "Marathahalli", "BTM Layout", "Other"]
                )
            with c2:
                v_vehicle = st.selectbox(
                    "Mode of Transport / Vehicle *",
                    ["Two-Wheeler (Motorbike/Scooter)", "Bicycle / Walking", "Four-Wheeler / Car", "Auto-Rickshaw"]
                )
                v_capacity = st.number_input("Transport Capacity (Meals you can carry)", min_value=10, max_value=200, value=30, step=10)
                v_hours = st.selectbox("Preferred Volunteering Window", ["Morning (9 AM - 1 PM)", "Afternoon (1 PM - 5 PM)", "Evening (5 PM - 9 PM)", "Flexible / On-Call"])
            
            # User password field for registration
            v_password = st.text_input("Password *", type="password", placeholder="Create a password for your account (min 6 characters)", key="reg_vol_pass")
            v_notes = st.text_area("Affiliation / Experience (Optional)", placeholder="College NSS unit, Rotaract club, local resident, etc.")
            v_sub = st.form_submit_button("Register as Volunteer ✓", use_container_width=True)

        if v_sub:
            name_clean = sanitise_text(v_name, 100).strip()
            phone_clean = sanitise_text(v_phone, 20).strip()
            pass_clean = v_password.strip() if v_password else ""

            if not name_clean or not phone_clean:
                st.error("Please provide your full name and mobile number.")
                return

            digits = "".join(filter(str.isdigit, phone_clean))
            if len(digits) < 10:
                st.error("Please provide a valid 10-digit mobile number.")
                return

            if not pass_clean or len(pass_clean) < 6:
                st.error("Password must be at least 6 characters long.")
                return

            safe, reason = check_prompt_injection(name_clean + " " + phone_clean)
            if not safe:
                st.error(f"Invalid input: {reason}")
                return

            # Prevent duplicate accounts using mobile number
            existing = db.get_user_by_identifier(digits)
            if existing:
                st.error("An account with this mobile number already exists. Please select 'Login' to sign in.")
                return

            # Securely hash password and save account
            pwd_hash = db.hash_password(pass_clean)
            uid = db.create_user({
                "username": digits,
                "phone": digits,
                "password_hash": pwd_hash,
                "role": "volunteer",
                "full_name": name_clean,
                "email": f"{digits}@volunteer.annasetu.org",
                "is_active": True,
                "is_approved": True,
            })

            veh_map = {
                "Two-Wheeler (Motorbike/Scooter)": "bike",
                "Bicycle / Walking": "bike",
                "Four-Wheeler / Car": "car",
                "Auto-Rickshaw": "auto"
            }
            vid = t.register_new_volunteer({
                "user_id": uid,
                "full_name": name_clean,
                "phone": digits,
                "city": "Bengaluru",
                "address": f"{v_locality}, Bengaluru",
                "locality": v_locality,
                "vehicle_type": veh_map.get(v_vehicle, "bike"),
                "vehicle_capacity_meals": v_capacity,
            })
            st.success(f"🎉 Welcome aboard, {name_clean}! You are registered as Volunteer #{vid} with Mobile: {digits}. Switch to 'Login' above to sign in with your password.")
            st.balloons()

    else:
        with st.form("form_transport_partner"):
            st.markdown("#### 🚚 Transport & Fleet Partner Details")
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("Fleet / Provider Name *", placeholder="e.g. QuickDrop Cargo or Self-Owned Tata Ace")
                t_phone = st.text_input("Contact Phone *", placeholder="10-digit phone number")
                t_stype = st.selectbox("Service Classification *", ["Commercial Logistics Partner", "NGO Own Vehicle", "Corporate CSR Fleet"])
                t_locality = st.selectbox(
                    "Base Locality *",
                    ["Outer Ring Road", "Central Bengaluru", "Whitefield", "Peenya Industrial Area", 
                     "Yeshwanthpur", "Electronic City", "Koramangala", "Other"]
                )
            with c2:
                t_vtype = st.selectbox("Vehicle Fleet Type *", ["Tata Ace / Mini-Truck", "Cargo Auto / 3-Wheeler", "Delivery Van", "Two-Wheeler Fleet"])
                t_cap = st.number_input("Capacity (Meals)", min_value=50, max_value=2000, value=300, step=50)
                t_cost = st.number_input("Base Cost per Trip (₹) - Enter 0 if NGO/CSR", min_value=0.0, max_value=2000.0, value=200.0, step=25.0)

            # User password field for registration
            t_password = st.text_input("Password *", type="password", placeholder="Create a password for your account (min 6 characters)", key="reg_fleet_pass")
            t_sub = st.form_submit_button("Register Fleet Partner ✓", use_container_width=True)

        if t_sub:
            name_clean = sanitise_text(t_name, 100).strip()
            phone_clean = sanitise_text(t_phone, 20).strip()
            pass_clean = t_password.strip() if t_password else ""

            if not name_clean or not phone_clean:
                st.error("Please provide fleet name and contact phone number.")
                return

            digits = "".join(filter(str.isdigit, phone_clean))
            if len(digits) < 10:
                st.error("Please provide a valid 10-digit mobile number.")
                return

            if not pass_clean or len(pass_clean) < 6:
                st.error("Password must be at least 6 characters long.")
                return

            safe, reason = check_prompt_injection(name_clean + " " + phone_clean)
            if not safe:
                st.error(f"Invalid input: {reason}")
                return

            # Prevent duplicate accounts using mobile number
            existing = db.get_user_by_identifier(digits)
            if existing:
                st.error("An account with this contact phone already exists. Please select 'Login' to sign in.")
                return

            # Securely hash password and save account
            pwd_hash = db.hash_password(pass_clean)
            uid = db.create_user({
                "username": digits,
                "phone": digits,
                "password_hash": pwd_hash,
                "role": "volunteer",
                "full_name": name_clean,
                "email": f"{digits}@fleet.annasetu.org",
                "is_active": True,
                "is_approved": True,
            })

            stype_map = {
                "Commercial Logistics Partner": "Commercial",
                "NGO Own Vehicle": "NGO Vehicle",
                "Corporate CSR Fleet": "CSR Sponsored"
            }
            vtype_map = {
                "Tata Ace / Mini-Truck": "Tata Ace",
                "Cargo Auto / 3-Wheeler": "tempo",
                "Delivery Van": "van",
                "Two-Wheeler Fleet": "bike"
            }
            tpid = t.register_new_transport_partner({
                "name": name_clean,
                "vehicle_type": vtype_map.get(t_vtype, "tempo"),
                "capacity_meals": t_cap,
                "city": "Bengaluru",
                "locality": t_locality,
                "service_type": stype_map.get(t_stype, "Commercial"),
                "cost_per_trip": t_cost,
                "contact_phone": digits,
            })
            # Also register corresponding volunteer driver record linked to user_id
            t.register_new_volunteer({
                "user_id": uid,
                "full_name": name_clean,
                "phone": digits,
                "city": "Bengaluru",
                "address": f"{t_locality}, Bengaluru",
                "locality": t_locality,
                "vehicle_type": vtype_map.get(t_vtype, "tempo"),
                "vehicle_capacity_meals": t_cap,
            })
            st.success(f"🎉 Fleet partner '{name_clean}' registered successfully (ID: #{tpid}) with Mobile: {digits}! Switch to 'Login' above to sign in with your password.")
            st.balloons()


def page_join_logistics():
    """Relocated onboarding view — redirects or renders the Sign Up view."""
    render_signup_view()


def page_logout():
    if st.session_state.get("authenticated"):
        user = st.session_state["user"]
        from database import log_audit
        log_audit(user["id"], user["username"], user["role"], "logout")
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["page"] = "home"
    st.success("Logged out successfully.")
    st.rerun()


# ══════════════════════════════════════════════
# DONOR PAGES
# ══════════════════════════════════════════════

def donor_dashboard():
    user = require_role("donor", "admin")
    import tools as t
    import pandas as pd
    org_id = user.get("org_id")
    donations = t.get_donations_for_donor(org_id) if org_id else []

    total = len(donations)
    delivered = sum(1 for d in donations if d.get("status") == "delivered")
    pending   = sum(1 for d in donations if d.get("status") in ("pending_screening","matched","collected"))

    st.markdown('<div class="section-title">🌾 Food Donor Dashboard & Surplus Management</div>', unsafe_allow_html=True)
    st.caption("Coordinate surplus donation batches, monitor food safety screening, and track live delivery drivers.")
    ai_status_bar()
    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(total,     "Total Donations")
        + kpi_card(delivered, "Delivered", "teal")
        + kpi_card(pending,   "In Progress", "coral")
        + '</div>', unsafe_allow_html=True
    )

    # ── Live Outbound Delivery Tracking ──
    donation_ids = [d["id"] for d in donations]
    deliveries = t.get_deliveries() if donation_ids else []
    active_deliveries = [dl for dl in deliveries if dl.get("donation_id") in donation_ids and dl.get("status") in ("assigned", "accepted", "at_pickup", "picked_up", "in_transit", "arrived_destination")]

    if active_deliveries:
        st.markdown("### 🚚 Live Outbound Delivery & Driver Tracking")
        for dl in active_deliveries:
            aid = dl.get("assignment_id")
            tracking = t.get_live_trip_tracking(aid) if aid else None
            status = dl.get("status", "assigned")

            with st.expander(f"📦 Dispatch #{dl['id']} — {dl.get('food_name','Food')} → {dl.get('recipient_name','Recipient')} ({status.replace('_',' ').title()})", expanded=True):
                if status == "arrived_destination":
                    st.markdown(f"""
                    <div style="background:rgba(22,166,154,0.18);border:1.5px solid #16A69A;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                        <div style="font-size:1.05rem;font-weight:900;color:#0F766E;">🏁 Destination Reached!</div>
                        <div style="font-size:0.92rem;color:#134E4A;margin-top:2px;font-weight:600;">
                            The driver has arrived at <strong>{dl.get('recipient_name')}</strong> gate. Handover and meal inspection is currently underway.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif status == "in_transit":
                    chk = tracking["current_checkpoint"] if tracking else "En route"
                    mins = tracking["estimated_remaining_mins"] if tracking else 15
                    st.markdown(f"""
                    <div style="background:rgba(135,61,245,0.15);border:1.5px solid #873DF5;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                        <div style="font-size:1.02rem;font-weight:900;color:#5B21B6;">🚚 Driver En Route to Recipient</div>
                        <div style="font-size:0.9rem;color:#2E1065;margin-top:2px;font-weight:600;">
                            Current GPS Checkpoint: <strong style="color:#5B21B6;">{chk}</strong> · Estimated arrival in <strong style="color:#0F766E;">~{mins} mins</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                col_info, col_map = st.columns([1.2, 1])
                with col_info:
                    st.markdown(f"**🍱 Food:** {dl.get('food_name','—')} ({dl.get('allocated_quantity','—')} meals)")
                    st.markdown(f"**🏠 Recipient:** {dl.get('recipient_name','—')}")
                    st.markdown(f"**📍 Delivery Destination:** {dl.get('delivery_location','—')}")
                    if tracking:
                        st.markdown(f"**🚴 Driver:** {tracking['driver_display_name']} (📞 <a href='tel:{tracking['driver_phone']}'>{tracking['driver_phone']}</a>)", unsafe_allow_html=True)
                        st.markdown(f"**🗺️ Corridor:** {tracking['route_summary']}")
                        st.markdown(f"[↗ Open Navigation Route in Google Maps]({tracking['gmaps_url']})")
                with col_map:
                    if tracking:
                        map_df = pd.DataFrame([{"lat": float(tracking["driver_lat"]), "lon": float(tracking["driver_lon"])}])
                        st.map(map_df, zoom=12, use_container_width=True)
                        st.caption(f"📍 Live Marker: ({tracking['driver_lat']:.4f}, {tracking['driver_lon']:.4f})")

    st.write("")
    st.markdown("### 📋 Recent Surplus Food Donations")
    if donations:
        rows = []
        for d in donations[:10]:
            rows.append({
                "ID": d["id"],
                "Food": d["food_name"],
                "Qty": f"{d['quantity']} {d['unit']}",
                "Status": d["status"],
                "Created": fmt_dt(d.get("created_at")),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No donations yet. Click below to register your first surplus food donation!")

    if st.button("🍱 Register a New Donation →", type="primary"):
        st.session_state["nav_override"] = "🍱 Register Donation"
        st.rerun()


def donor_register_donation():
    user = require_role("donor", "admin")
    st.markdown('<div class="section-title">🍱 Register a New Donation</div>', unsafe_allow_html=True)

    import tools as t
    from guardrails import pre_flight_donation
    from agents import run_donation_workflow
    from database import log_audit

    donor_orgs = t.get_all_donor_orgs()
    if not donor_orgs:
        st.warning("No donor organisations found. Please contact admin.")
        return

    org_id = user.get("org_id")
    if not org_id and donor_orgs:
        org_id = donor_orgs[0]["id"]

    with st.form("reg_donation"):
        col1, col2 = st.columns(2)
        with col1:
            food_name     = st.text_input("Food Name *", placeholder="e.g. Vegetarian Thali Meals")
            food_category = st.selectbox("Food Category *",
                ["cooked_meals","raw_produce","bakery","dairy","beverages","snacks","other"])
            dietary_type  = st.selectbox("Dietary Type *",
                ["vegetarian","non_vegetarian","vegan","jain","halal","any"])
            quantity      = st.number_input("Quantity (number of meals/items) *", min_value=1, max_value=10000, value=50)
            unit          = st.selectbox("Unit", ["meals","kg","litres","packets","items"])
        with col2:
            packaging     = st.selectbox("Packaging", ["sealed","bulk","open","vacuum_packed","other"])
            storage       = st.selectbox("Storage Condition", ["ambient","refrigerated","frozen"])
            location      = st.text_input("Pickup Location *", placeholder="e.g. Indiranagar, Bengaluru")
            city          = st.text_input("City", value="Bengaluru")
            prep_time     = st.text_input("Preparation Time (YYYY-MM-DD HH:MM)", placeholder="e.g. 2024-01-15 12:00")
            deadline      = st.text_input("Pickup Deadline * (YYYY-MM-DD HH:MM)", placeholder="e.g. 2024-01-15 18:00")
        allergens = st.text_input("Allergen Information (optional)", placeholder="e.g. Contains nuts, dairy")
        notes     = st.text_area("Additional Notes", height=80)
        submit    = st.form_submit_button("Register & Run AI Screening →")

    if submit:
        # Parse times
        prep_dt = None
        if prep_time.strip():
            try:
                prep_dt = datetime.strptime(prep_time.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            except ValueError:
                st.error("Invalid preparation time format. Use YYYY-MM-DD HH:MM")
                return
        try:
            deadline_dt = datetime.strptime(deadline.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except ValueError:
            st.error("Invalid pickup deadline format. Use YYYY-MM-DD HH:MM")
            return

        data = {
            "food_name": food_name, "food_category": food_category,
            "dietary_type": dietary_type, "quantity": int(quantity),
            "packaging": packaging, "storage_condition": storage,
            "location": location, "city": city,
            "pickup_deadline": deadline_dt, "preparation_time": prep_dt,
            "allergen_info": allergens, "notes": notes,
        }

        ok, errors = pre_flight_donation(data, user)
        if not ok:
            for e in errors:
                st.error(e)
            return

        with st.spinner("Registering donation and running AI safety screening…"):
            result = t.register_donation(
                donor_org_id=org_id, donor_user_id=user["id"],
                food_name=food_name, food_category=food_category,
                dietary_type=dietary_type, quantity=int(quantity), unit=unit,
                preparation_time=prep_dt, pickup_deadline=deadline_dt,
                location=location, city=city, packaging=packaging,
                storage_condition=storage, allergen_info=allergens, notes=notes,
            )
            donation_id = result["donation_id"]

            # Run Agent 1+2 workflow
            workflow_result = run_donation_workflow(donation_id)

        log_audit(user["id"], user["username"], user["role"],
                  "register_donation", "donation", donation_id)

        screening = workflow_result.get("screening_result", "pending_review")
        if screening == "eligible":
            st.markdown('<div class="alert-safe">✅ Donation registered and passed safety screening. Matching in progress.</div>', unsafe_allow_html=True)
        elif screening == "pending_review":
            st.markdown('<div class="alert-warn">⚠️ Donation registered but flagged for human safety review before matching.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-danger">🚫 Donation blocked by safety screening. An administrator will review.</div>', unsafe_allow_html=True)

        matches = workflow_result.get("proposed_matches", [])
        if matches:
            st.success(f"🎯 Agent 2 proposed {len(matches)} matches — pending admin approval.")
            for m in matches:
                st.markdown(
                    f'<div class="as-card-sm">🏠 <strong>{m["recipient_name"]}</strong> — '
                    f'{m["allocated_quantity"]} meals (score {m["match_score"]:.1f})<br>'
                    f'<small style="color:#57606a">{m.get("match_reason","")[:200]}</small></div>',
                    unsafe_allow_html=True
                )

        errors_list = workflow_result.get("errors", [])
        if errors_list:
            for err in errors_list:
                st.warning(f"ℹ️ {err}")


def donor_my_donations():
    user = require_role("donor", "admin")
    import tools as t
    import pandas as pd

    org_id = user.get("org_id")
    if not org_id:
        st.warning("No organisation linked to your account.")
        return

    donations = t.get_donations_for_donor(org_id)
    st.markdown('<div class="section-title">📋 My Donations</div>', unsafe_allow_html=True)

    if not donations:
        st.info("No donations registered yet.")
        return

    for d in donations:
        safety = t.get_food_safety_record(d["id"])
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"**{d['food_name']}** — {d['quantity']} {d['unit']}", unsafe_allow_html=False)
            st.caption(f"📍 {d.get('location','—')} | Deadline: {fmt_dt(d.get('pickup_deadline'))}")
        with col2:
            st.markdown(status_badge(d.get("status","")), unsafe_allow_html=True)
            if safety:
                score = safety.get("safety_score", 0)
                st.caption(f"Safety score: {score}/10")
        with col3:
            st.caption(f"Registered: {fmt_dt(d.get('created_at'))}")
        st.divider()


def donor_tracking():
    user = require_role("donor", "admin")
    import tools as t
    import pandas as pd

    org_id = user.get("org_id")
    if not org_id:
        st.warning("No organisation linked.")
        return

    donations = t.get_donations_for_donor(org_id)
    donation_ids = [d["id"] for d in donations]

    st.markdown('<div class="section-title">🚚 Live Delivery & Driver Tracking Console</div>', unsafe_allow_html=True)

    if not donation_ids:
        st.info("No donations registered to track yet.")
        return

    deliveries = t.get_deliveries()
    my_deliveries = [dl for dl in deliveries if dl.get("donation_id") in donation_ids]

    if not my_deliveries:
        st.info("No delivery records found for your surplus donations.")
        return

    in_transit_cnt = len([dl for dl in my_deliveries if dl.get("status") in ("picked_up", "in_transit")])
    arrived_cnt = len([dl for dl in my_deliveries if dl.get("status") == "arrived_destination"])
    delivered_cnt = len([dl for dl in my_deliveries if dl.get("status") == "delivered"])

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(len(my_deliveries), "Tracked Dispatches")
        + kpi_card(in_transit_cnt, "In Transit En Route", "teal")
        + kpi_card(arrived_cnt, "Arrived at Destination", "coral")
        + kpi_card(delivered_cnt, "Delivered & Confirmed", "teal")
        + '</div>',
        unsafe_allow_html=True
    )

    for dl in my_deliveries:
        aid = dl.get("assignment_id")
        tracking = t.get_live_trip_tracking(aid) if aid else None
        status = dl.get("status", "assigned")

        with st.expander(
            f"📦 Delivery #{dl['id']} — {dl.get('food_name','Food')} → {dl.get('recipient_name','Recipient')} | {status.upper()}",
            expanded=(status in ("in_transit", "arrived_destination", "picked_up", "at_pickup"))
        ):
            # Arrival and Milestone Banner
            if status == "arrived_destination":
                st.markdown(f"""
                <div style="background:rgba(22,166,154,0.18);border:1.5px solid #16A69A;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                    <div style="font-size:1.05rem;font-weight:900;color:#0F766E;">🏁 Destination Reached!</div>
                    <div style="font-size:0.92rem;color:#134E4A;margin-top:2px;font-weight:600;">
                        The driver has arrived at <strong>{dl.get('recipient_name')}</strong> gate. Handover and meal inspection is currently underway.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif status == "in_transit":
                chk = tracking["current_checkpoint"] if tracking else "En route"
                mins = tracking["estimated_remaining_mins"] if tracking else 15
                st.markdown(f"""
                <div style="background:rgba(135,61,245,0.15);border:1.5px solid #873DF5;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                    <div style="font-size:1.02rem;font-weight:900;color:#5B21B6;">🚚 Driver En Route to Recipient</div>
                    <div style="font-size:0.9rem;color:#2E1065;margin-top:2px;font-weight:600;">
                        Current GPS Checkpoint: <strong style="color:#5B21B6;">{chk}</strong> · Estimated arrival in <strong style="color:#0F766E;">~{mins} mins</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif status == "picked_up":
                st.markdown(f"""
                <div style="background:rgba(240,120,134,0.15);border:1.5px solid #F07886;border-radius:12px;padding:10px 14px;margin-bottom:12px;">
                    <strong style="color:#F07886;">📦 Food Picked Up:</strong> Driver has collected surplus food from your location and started vehicle transit.
                </div>
                """, unsafe_allow_html=True)
            elif status == "delivered":
                st.markdown(f"""
                <div style="background:rgba(22,166,154,0.12);border:1px solid #16A69A;border-radius:10px;padding:10px 14px;margin-bottom:12px;">
                    <strong style="color:#16A69A;">✅ Delivered &amp; Confirmed:</strong> Recipient acknowledged receipt of <strong>{dl.get('actual_quantity', dl.get('allocated_quantity'))} meals</strong>.
                </div>
                """, unsafe_allow_html=True)

            # Milestone Progress Indicator
            pct = tracking["progress_pct"] if tracking else 25
            st.progress(pct / 100.0)
            st.caption(f"Journey Milestone: {pct}% Completed · Current Status: {status.replace('_',' ').title()}")

            col_info, col_map = st.columns([1.2, 1])

            with col_info:
                st.markdown(f"**🍱 Food Donated:** {dl.get('food_name','—')} ({dl.get('allocated_quantity','—')} meals)")
                st.markdown(f"**📍 Pickup Location:** {dl.get('pickup_location','—')}")
                st.markdown(f"**🏠 Recipient Organisation:** {dl.get('recipient_name','—')}")
                st.markdown(f"**📍 Destination Address:** {dl.get('delivery_location','—')}")
                st.markdown(f"**⏰ Scheduled Pickup:** {fmt_dt(dl.get('pickup_time_scheduled'))}")

                if tracking:
                    st.divider()
                    st.markdown("**🚴 Dispatched Driver / Fleet Provider:**")
                    st.markdown(f"• **Name:** {tracking['driver_display_name']}")
                    st.markdown(f"• **Contact:** 📞 <a href='tel:{tracking['driver_phone']}'>{tracking['driver_phone']}</a>", unsafe_allow_html=True)
                    st.markdown(f"• **Corridor:** {tracking['route_summary']}")
                    st.markdown(f"[↗ Open Live Direction Route in Google Maps]({tracking['gmaps_url']})")

            with col_map:
                st.markdown("**🗺️ Live GPS Telemetry Map**")
                if tracking:
                    # Generate coordinate pins: Pickup, In-transit, Destination
                    lat = tracking["driver_lat"]
                    lon = tracking["driver_lon"]
                    map_df = pd.DataFrame([
                        {"lat": lat, "lon": lon, "label": "Driver's Current Location"},
                    ])
                    st.map(map_df, zoom=12, use_container_width=True)
                    st.caption(f"📍 Driver Marker: ({lat:.4f}, {lon:.4f}) · Checkpoint: {tracking['current_checkpoint']}")
                else:
                    st.caption("Awaiting driver dispatch coordinates.")


# ══════════════════════════════════════════════
# RECIPIENT PAGES
# ══════════════════════════════════════════════

def recipient_dashboard():
    user = require_role("recipient", "admin")
    import tools as t
    import pandas as pd

    org_id = user.get("org_id")
    matches = []
    if org_id:
        all_matches = t.get_matches_with_details()
        matches = [m for m in all_matches if m.get("recipient_org_id") == org_id]

    pending_deliveries = [m for m in matches if m.get("status") not in ("delivered","failed","admin_rejected")]

    st.markdown('<div class="section-title">🏥 Recipient Shelter Dashboard & Inbound Food Intake</div>', unsafe_allow_html=True)
    st.caption("Monitor incoming food donations, track approaching drivers live on map, and verify meal handovers.")
    ai_status_bar()
    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(len(matches),           "Total Matches")
        + kpi_card(len(pending_deliveries), "Active Deliveries", "teal")
        + kpi_card(sum(1 for m in matches if m.get("status")=="delivered"), "Received", "coral")
        + '</div>', unsafe_allow_html=True
    )

    # ── Live Inbound Deliveries & Driver Telemetry ──
    deliveries = t.get_deliveries()
    my_inbound = [dl for dl in deliveries
                  if (dl.get("recipient_org_id") == org_id or user.get("role") == "admin")
                  and dl.get("status") in ("arrived_destination", "in_transit", "picked_up", "at_pickup")]

    if my_inbound:
        st.markdown("### 🚚 Inbound Food Deliveries & Live Driver Tracking")
        for dl in my_inbound:
            aid = dl.get("assignment_id")
            tracking = t.get_live_trip_tracking(aid) if aid else None
            status = dl.get("status", "assigned")

            with st.expander(f"📦 Incoming Delivery #{dl['id']} — {dl.get('food_name','Meals')} ({status.replace('_',' ').title()})", expanded=True):
                if status == "arrived_destination":
                    st.markdown("""
                    <div style="background:rgba(22,166,154,0.22);border:2px solid #0F766E;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                        <div style="font-size:1.1rem;font-weight:900;color:#065F46;">🔔 DRIVER HAS ARRIVED AT YOUR GATE!</div>
                        <div style="font-size:0.92rem;color:#134E4A;margin-top:2px;font-weight:600;">
                            The rescue driver is waiting outside with your food donation. Inspect the food condition and confirm handover below.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif status == "in_transit":
                    chk = tracking.get("current_checkpoint") if tracking else "En route"
                    mins = tracking.get("estimated_remaining_mins") if tracking else 15
                    st.markdown(f"""
                    <div style="background:rgba(135,61,245,0.15);border:1px solid #873DF5;border-radius:10px;padding:10px 14px;margin-bottom:12px;">
                        <strong style="color:#B26AF5;">🚚 Driver Approaching:</strong> {chk} · Estimated arrival in <strong>~{mins} mins</strong>
                    </div>
                    """, unsafe_allow_html=True)

                col1, col2 = st.columns([1.2, 1])
                with col1:
                    st.write(f"**Donated Food:** {dl.get('food_name','—')}")
                    st.write(f"**Expected Quantity:** `{dl.get('allocated_quantity','—')} meals`")
                    st.write(f"**Status:** {status_badge(status)}", unsafe_allow_html=True)
                    if tracking:
                        st.write(f"**Driver:** {tracking['driver_display_name']} (📞 <a href='tel:{tracking['driver_phone']}'>{tracking['driver_phone']}</a>)", unsafe_allow_html=True)
                        st.write(f"**Corridor:** {tracking['route_summary']}")
                with col2:
                    if tracking:
                        st.markdown("**Live GPS Map**")
                        st.map(pd.DataFrame([{"lat": float(tracking["driver_lat"]), "lon": float(tracking["driver_lon"])}]), zoom=12, use_container_width=True)

                st.divider()
                st.markdown("##### 📝 Quick Handover Confirmation")
                ack_col1, ack_col2 = st.columns(2)
                with ack_col1:
                    actual = st.number_input(f"Actual quantity received (meals)", min_value=0,
                                             max_value=int(dl.get("allocated_quantity", 1000)),
                                             value=int(dl.get("allocated_quantity", 50)),
                                             key=f"dash_ack_qty_{dl['id']}")
                with ack_col2:
                    notes = st.text_input("Inspection / Quality Notes", placeholder="Received in good hot condition, sealed packaging, etc.", key=f"dash_ack_notes_{dl['id']}")
                if st.button(f"Confirm & Acknowledge Delivery #{dl['id']} ✓", key=f"dash_ack_btn_{dl['id']}", type="primary"):
                    t.record_acknowledgement(dl["id"], actual, notes)
                    from database import log_audit
                    log_audit(user["id"], user["username"], user["role"], "acknowledge_delivery", "delivery", dl["id"], f"actual_qty={actual}")
                    st.success("✅ Delivery confirmed & successfully acknowledged! Recorded into permanent impact ledger.")
                    st.rerun()

    st.write("")
    st.markdown("### 🎯 Available Matched Surplus Food")
    if matches:
        for m in matches[:5]:
            mc1, mc2, mc3 = st.columns([3, 2, 2])
            with mc1:
                st.markdown(f"**{m.get('food_name','—')}** from {m.get('donor_name','—')}")
                st.caption(f"Quantity: {m.get('allocated_quantity','—')} meals | Type: {m.get('dietary_type','—')}")
            with mc2:
                st.markdown(status_badge(m.get("status","")), unsafe_allow_html=True)
            with mc3:
                st.caption(f"Score: {m.get('match_score','—')}")
            st.divider()
    else:
        st.info("No surplus food matches pending right now.")


def recipient_available_matches():
    user = require_role("recipient", "admin")
    import tools as t

    org_id = user.get("org_id")
    all_matches = t.get_matches_with_details()
    my_matches  = [m for m in all_matches if m.get("recipient_org_id") == org_id]

    st.markdown('<div class="section-title">🎯 Available Matches</div>', unsafe_allow_html=True)
    if not my_matches:
        st.info("No matches available for your organisation yet.")
        return

    for m in my_matches:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"**{m.get('food_name','—')}** from {m.get('donor_name','—')}")
            st.caption(f"Quantity: {m.get('allocated_quantity','—')} meals | Type: {m.get('dietary_type','—')}")
        with col2:
            st.markdown(status_badge(m.get("status","")), unsafe_allow_html=True)
            st.caption(f"Match score: {m.get('match_score','—')}")
        with col3:
            st.caption(f"Proposed: {fmt_dt(m.get('created_at'))}")
        st.divider()


def recipient_acknowledge_delivery():
    user = require_role("recipient", "admin")
    import tools as t
    from guardrails import validate_delivery_completion

    org_id = user.get("org_id")
    deliveries = t.get_deliveries()
    my_deliveries = [dl for dl in deliveries
                     if (dl.get("recipient_org_id") == org_id or user.get("role") == "admin")
                     and dl.get("status") in ("arrived_destination", "in_transit", "picked_up", "at_pickup", "assigned", "accepted")]

    st.markdown('<div class="section-title">✅ Incoming Deliveries & Handover Acknowledgement</div>', unsafe_allow_html=True)
    if not my_deliveries:
        st.info("No incoming deliveries currently awaiting acknowledgement.")
        return

    for dl in my_deliveries:
        aid = dl.get("assignment_id")
        tracking = t.get_live_trip_tracking(aid) if aid else None
        status = dl.get("status", "assigned")

        with st.expander(
            f"Delivery #{dl['id']} — {dl.get('food_name','Meals')} ({status.replace('_',' ').title()})",
            expanded=(status in ("arrived_destination", "in_transit", "picked_up"))
        ):
            if status == "arrived_destination":
                st.markdown("""
                <div style="background:rgba(22,166,154,0.22);border:2px solid #0F766E;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
                    <div style="font-size:1.1rem;font-weight:900;color:#065F46;">🔔 DRIVER HAS ARRIVED AT YOUR GATE!</div>
                    <div style="font-size:0.92rem;color:#134E4A;margin-top:2px;font-weight:600;">
                        The rescue driver is waiting outside with your food donation. Please inspect the food condition, receive the meal containers, and enter the actual portion count below to confirm delivery.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif status == "in_transit":
                chk = tracking.get("current_checkpoint") if tracking else "En route"
                mins = tracking.get("estimated_remaining_mins") if tracking else 15
                st.markdown(f"""
                <div style="background:rgba(135,61,245,0.15);border:1px solid #873DF5;border-radius:10px;padding:10px 14px;margin-bottom:12px;">
                    <strong style="color:#B26AF5;">🚚 Driver Approaching:</strong> {chk} · Estimated arrival in <strong>~{mins} mins</strong>
                </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Donated Food:** {dl.get('food_name','—')}")
                st.write(f"**Expected Quantity:** `{dl.get('allocated_quantity','—')} meals`")
                st.write(f"**Status:** {status_badge(status)}", unsafe_allow_html=True)
                if tracking:
                    st.write(f"**Driver:** {tracking['driver_display_name']} (📞 {tracking['driver_phone']})")
                    st.write(f"**Corridor:** {tracking['route_summary']}")
            with col2:
                actual = st.number_input(f"Actual quantity received (meals)", min_value=0,
                                         max_value=int(dl.get("allocated_quantity", 1000)),
                                         value=int(dl.get("allocated_quantity", 50)),
                                         key=f"ack_qty_{dl['id']}")
                notes  = st.text_input("Inspection / Quality Notes", placeholder="Received in good hot condition, sealed packaging, etc.", key=f"ack_notes_{dl['id']}")
                if st.button(f"Confirm & Acknowledge Delivery ✓", key=f"ack_btn_{dl['id']}", type="primary"):
                    t.record_acknowledgement(dl["id"], actual, notes)
                    from database import log_audit
                    log_audit(user["id"], user["username"], user["role"],
                              "acknowledge_delivery", "delivery", dl["id"],
                              f"actual_qty={actual}")
                    st.success("✅ Delivery confirmed & successfully acknowledged! Recorded into permanent impact ledger.")
                    st.rerun()


# ══════════════════════════════════════════════
# RECIPIENT & PUBLIC LIVE DRIVER TRACKING
# ══════════════════════════════════════════════

def page_track_live_delivery():
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🚚 Live Food Delivery & Driver Tracking</div>', unsafe_allow_html=True)
    st.caption("Real-time GPS tracking and direct contact details for rescue drivers delivering surplus food to your community organisation.")
    ai_status_bar()

    user = st.session_state.get("user")
    org_id = user.get("org_id") if user else None

    # Fetch all active deliveries from PostgreSQL
    all_active = t.execute_query("""
        SELECT ca.id AS assignment_id, ca.status, ca.current_checkpoint, ca.current_latitude, ca.current_longitude,
               ca.estimated_remaining_mins, ca.pickup_location, ca.delivery_location,
               dm.allocated_quantity, d.food_name,
               ro.name AS recipient_name, ro.contact_phone AS recipient_phone,
               dorg.name AS donor_name,
               COALESCE(v.full_name, tp.name, 'Assigned Rescue Driver') AS driver_name,
               COALESCE(v.phone, tp.contact_phone, '9900001111') AS driver_phone,
               COALESCE(v.vehicle_type, ca.transport_mode, 'Vehicle') AS vehicle_type
        FROM as_collection_assignments ca
        JOIN as_donation_matches dm ON ca.match_id = dm.id
        JOIN as_donations d ON dm.donation_id = d.id
        LEFT JOIN as_recipient_orgs ro ON dm.recipient_org_id = ro.id
        LEFT JOIN as_donor_orgs dorg ON d.donor_org_id = dorg.id
        LEFT JOIN as_volunteers v ON ca.volunteer_id = v.id
        LEFT JOIN as_transport_providers tp ON ca.transport_provider_id = tp.id
        WHERE ca.status NOT IN ('failed', 'cancelled')
        ORDER BY ca.id DESC
    """)

    if not all_active:
        st.info("ℹ️ No deliveries are currently active. Once a surplus food donation is matched and dispatched by Agent 3, real-time driver tracking will appear here automatically.")
        return

    # Filter / selector
    if org_id:
        my_deliveries = [a for a in all_active if a.get("recipient_name") == user.get("full_name")]
        selected = my_deliveries[0] if my_deliveries else all_active[0]
    else:
        options = {
            f"Delivery #{a['assignment_id']} — {a.get('food_name','Food')} → {a.get('recipient_name','Recipient')} ({a['status'].replace('_',' ').title()})": a
            for a in all_active
        }
        choice = st.selectbox("📦 Select Delivery to Track:", list(options.keys()), key="track_delivery_choice")
        selected = options[choice]

    aid = selected["assignment_id"]
    tracking = t.get_live_trip_tracking(aid)
    if not tracking:
        st.error(f"Could not load telemetry for delivery #{aid}.")
        return

    tr_data = tracking.get("data", {})
    status = tracking.get("status", "in_transit")
    driver_name = tracking.get("driver_display_name", "Rescue Driver")
    driver_phone = tracking.get("driver_phone", "9900001111")
    vehicle = tr_data.get("driver_vehicle") or tr_data.get("transport_mode") or "Delivery Vehicle"
    clean_phone = driver_phone.replace(" ", "").replace("-", "")

    # 1. Prominent Driver Contact & Identity Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(22,166,154,0.18), rgba(135,61,245,0.18));
                border: 2px solid #16A69A; border-radius: 14px; padding: 18px 22px; margin-bottom: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="font-size: 0.78rem; font-weight: 800; color: #0F766E; text-transform: uppercase; letter-spacing: 0.08em;">
                    🛵 ASSIGNED DELIVERY PARTNER DETAILS
                </div>
                <div style="font-size: 1.45rem; font-weight: 900; color: #1E1035; margin: 4px 0;">
                    {driver_name}
                </div>
                <div style="font-size: 0.9rem; color: #374151; font-weight: 600;">
                    Vehicle: <strong style="color: #6D28D9; font-weight: 800;">{vehicle.upper()}</strong> · Status: <span class="badge badge-teal">{status.upper()}</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <div style="text-align: right;">
                    <div style="font-size: 0.74rem; color: #6D28D9; font-weight: 800; letter-spacing: 0.05em;">DIRECT MOBILE NUMBER</div>
                    <div style="font-size: 1.35rem; font-weight: 900; color: #1E1035;">📞 {driver_phone}</div>
                </div>
                <a href="tel:{clean_phone}" style="background: linear-gradient(135deg, #0F766E, #14B8A6);
                          color: #FFFFFF !important; font-weight: 800; padding: 10px 22px;
                          border-radius: 10px; text-decoration: none; font-size: 0.95rem;
                          box-shadow: 0 4px 14px rgba(15,118,110,0.35); display: inline-flex; align-items: center;">
                    <span style="color: #FFFFFF !important; font-weight: 800;">📞 Call Delivery Partner</span>
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Live Status & Arrival Alerts
    if status == "arrived_destination":
        st.markdown(f"""
        <div style="background: rgba(22,166,154,0.25); border: 2.5px solid #0F766E; border-radius: 14px; padding: 16px 20px; margin-bottom: 1.25rem;">
            <div style="font-size: 1.2rem; font-weight: 900; color: #065F46; display: flex; align-items: center; gap: 8px;">
                🔔 DELIVERY PARTNER HAS ARRIVED OUTSIDE YOUR PREMISES!
            </div>
            <div style="color: #134E4A; font-size: 0.95rem; margin-top: 6px; line-height: 1.5; font-weight: 600;">
                The rescue driver (<strong style="color: #065F46;">{driver_name}</strong>) has arrived at your gate with <strong style="color: #065F46;">{tr_data.get('allocated_quantity','—')} meals</strong> of <strong style="color: #065F46;">{tr_data.get('food_name','surplus food')}</strong>.
                Please meet the vehicle outside to inspect and receive the meal containers.
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif status in ("in_transit", "picked_up"):
        chk = tracking.get("current_checkpoint") or "En route to destination"
        mins = tracking.get("estimated_remaining_mins", 15)
        st.markdown(f"""
        <div style="background: rgba(135,61,245,0.18); border: 2px solid #7C3AED; border-radius: 14px; padding: 16px 20px; margin-bottom: 1.25rem;">
            <div style="font-size: 1.15rem; font-weight: 900; color: #5B21B6;">
                🚚 Delivery Partner is Approaching Your Location
            </div>
            <div style="color: #2E1065; font-size: 0.95rem; margin-top: 6px; font-weight: 600;">
                Current GPS Checkpoint: <strong style="color: #5B21B6;">{chk}</strong> · Estimated arrival in: <strong style="color: #0F766E;">~{mins} minutes</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Live Driver GPS Map
    st.markdown("### 🗺️ Live Delivery Driver Location & Route")
    lat = float(tracking.get("driver_lat") or 12.9716)
    lon = float(tracking.get("driver_lon") or 77.5946)
    map_df = pd.DataFrame([{"lat": lat, "lon": lon}])
    st.map(map_df, zoom=13)

    # 4. Details Summary Cards
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"""
        <div class="as-card-sm">
            <strong style="color: var(--teal);">🍱 Food Details:</strong> {tr_data.get('food_name','Meals')}<br>
            <strong>Allocated Quantity:</strong> {tr_data.get('allocated_quantity','—')} portions<br>
            <strong>Donor Venue:</strong> {tr_data.get('donor_name','Donor')}<br>
            <strong>Pickup Location:</strong> {tr_data.get('pickup_location','Bengaluru')}
        </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.markdown(f"""
        <div class="as-card-sm">
            <strong style="color: var(--purple);">🏠 Recipient Organisation:</strong> {tr_data.get('recipient_name','Recipient')}<br>
            <strong>Delivery Address:</strong> {tr_data.get('delivery_location','Bengaluru')}<br>
            <strong>Corridor Summary:</strong> {tracking.get('route_summary','Direct Bengaluru Route')}<br>
            <strong><a href="{tracking.get('gmaps_url','#')}" target="_blank">🗺️ Open in Google Maps ↗</a></strong>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# VOLUNTEER PAGES
# ══════════════════════════════════════════════

def volunteer_dashboard():
    user = require_role("volunteer", "admin")
    import tools as t
    import pandas as pd

    vol = t.get_volunteer_by_user_id(user["id"])
    if not vol and user.get("role") == "admin":
        vols = t.get_all_volunteers()
        vol = vols[0] if vols else None

    assignments = t.get_assignments_for_volunteer(vol["id"]) if vol else []
    active = [a for a in assignments if a.get("status") not in ("delivered","failed","cancelled")]

    st.markdown('<div class="section-title">🚴 Volunteer & Driver Mission Portal</div>', unsafe_allow_html=True)
    st.caption("Live rescue mission console, route navigation, and GPS checkpoint broadcasting.")
    ai_status_bar()

    if vol:
        avail_color = "green" if vol.get("is_available") else "red"
        st.markdown(
            f'<div class="as-card">'
            f'<strong>{vol["full_name"]}</strong> | '
            f'Vehicle: {vol.get("vehicle_type","—").upper()} (capacity: {vol.get("vehicle_capacity_meals","—")} meals) | '
            f'Locality: {vol.get("locality","Bengaluru")} | '
            f'<span class="badge badge-{avail_color}">{"Available / On Duty" if vol.get("is_available") else "Unavailable"}</span>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(len(assignments), "Total Assignments")
        + kpi_card(len(active),      "Active Assignments", "teal")
        + kpi_card(sum(1 for a in assignments if a.get("status")=="delivered"), "Completed", "coral")
        + '</div>', unsafe_allow_html=True
    )

    if active:
        st.markdown("### 🗺️ Active Rescue Missions in Progress")
        for a in active:
            status = a.get("status", "assigned")
            pickup_loc = a.get("pickup_location", "Donor location")
            drop_loc = a.get("delivery_address", a.get("delivery_location", "Recipient location"))
            route_info = t.estimate_bengaluru_route(pickup_loc, drop_loc)

            with st.expander(f"📦 Trip #{a['id']} — {a.get('recipient_name','Recipient')} ({status.upper()})", expanded=True):
                col1, col2 = st.columns([1.3, 1])
                with col1:
                    st.markdown(f"**🍱 Food Quantity:** `{a.get('allocated_quantity','—')} meals`")
                    st.markdown(f"**📍 Pickup Location:** {pickup_loc}")
                    st.markdown(f"**🏠 Delivery Destination:** {drop_loc}")
                    st.markdown(f"**⏰ Scheduled Pickup:** {fmt_dt(a.get('pickup_time_scheduled'))}")
                    st.markdown(f"**🗺️ Route Corridor:** {route_info['summary']}")
                    st.markdown(f"[↗ Open Live Navigation in Google Maps]({route_info['gmaps_url']})")
                with col2:
                    st.write("**Live Mission Actions:**")
                    st.markdown(status_badge(status), unsafe_allow_html=True)
                    st.write("")
                    if status in ("assigned", "accepted"):
                        if st.button("📍 Arrived at Donor Pickup", key=f"vdash_arr_{a['id']}", use_container_width=True):
                            t.update_driver_live_tracking(a["id"], "at_pickup", f"Driver arrived at donor location ({pickup_loc[:25]})")
                            st.success("Arrival recorded! Inspect meal packages before loading.")
                            st.rerun()
                    if status in ("accepted", "at_pickup"):
                        if st.button("Confirm Food Picked Up 📦", key=f"vdash_pick_{a['id']}", use_container_width=True):
                            t.update_driver_live_tracking(a["id"], "picked_up", "Food verified and loaded into vehicle")
                            st.success("Pickup recorded! Transit initiated.")
                            st.rerun()
                    if status in ("picked_up", "in_transit"):
                        if st.button("🏁 Mark Arrived at Destination", key=f"vdash_dest_{a['id']}", use_container_width=True, type="primary"):
                            t.update_driver_live_tracking(a["id"], "arrived_destination", f"Driver arrived at recipient gate ({drop_loc[:25]})", remaining_mins=0)
                            st.success("Destination reached! Recipient organisation alerted for handover.")
                            st.rerun()
    else:
        st.info("🟢 No active pickups assigned right now. You are ready for dispatch! Agent 3 will assign you to the nearest surplus food rescue in your locality.")

    vcol1, vcol2 = st.columns(2)
    with vcol1:
        if st.button("📍 Delivery Destinations & Routes →", use_container_width=True, key="vdash_btn_dest"):
            st.session_state["nav_override"] = "📍 Delivery Destinations & Routes"
            st.rerun()
    with vcol2:
        if st.button("🚚 Open Full Driver Trip Console & GPS →", use_container_width=True, key="vdash_btn_console"):
            st.session_state["nav_override"] = "🚚 Driver Trip Console & GPS"
            st.rerun()


def volunteer_delivery_destinations():
    user = require_role("volunteer", "admin")
    import tools as t

    vol = t.get_volunteer_by_user_id(user["id"])
    if not vol and user.get("role") == "admin":
        vols = t.get_all_volunteers()
        vol = vols[0] if vols else None

    st.markdown('<div class="section-title">📍 Delivery Destinations & Active Routes</div>', unsafe_allow_html=True)
    st.caption("Organized driver console: view verified pickup locations, delivery destinations, recipient phone numbers, and navigation corridors across Bengaluru.")
    ai_status_bar()

    assignments = t.get_assignments_for_volunteer(vol["id"]) if vol else []
    if not assignments and user.get("role") == "admin":
        assignments = t.execute_query("""
            SELECT ca.*, dm.allocated_quantity, d.food_name, 
                   ro.name AS recipient_name, ro.address AS recipient_address, ro.contact_phone AS recipient_phone,
                   dorg.name AS donor_name, dorg.address AS donor_address, dorg.contact_phone AS donor_phone
            FROM as_collection_assignments ca
            JOIN as_donation_matches dm ON ca.match_id = dm.id
            JOIN as_donations d ON dm.donation_id = d.id
            LEFT JOIN as_recipient_orgs ro ON dm.recipient_org_id = ro.id
            LEFT JOIN as_donor_orgs dorg ON d.donor_org_id = dorg.id
            ORDER BY ca.id DESC LIMIT 10
        """)

    active_orders = [a for a in assignments if a.get("status") not in ("failed", "cancelled")]

    if not active_orders:
        st.info("🟢 No active deliveries are currently assigned to your vehicle. You are on standby! When a surplus food donation is matched by Agent 3, your route and destination details will appear here immediately.")
        return

    st.markdown(f"**Found {len(active_orders)} active delivery destination assignment(s):**")

    for a in active_orders:
        aid = a["id"]
        status = a.get("status", "assigned")
        tracking = t.get_live_trip_tracking(aid) or {}
        tr_data = tracking.get("data", {})

        pickup_loc = a.get("pickup_location") or tr_data.get("pickup_location") or "Donor Pickup Location"
        delivery_loc = a.get("delivery_address") or a.get("delivery_location") or tr_data.get("delivery_location") or "Recipient Destination"
        food_name = a.get("food_name") or tr_data.get("food_name") or "Cooked Surplus Meals"
        qty = a.get("allocated_quantity") or tr_data.get("allocated_quantity") or "—"
        donor_name = a.get("donor_name") or tr_data.get("donor_name") or "Verified Food Donor"
        donor_phone = a.get("donor_phone") or tr_data.get("donor_phone") or "—"
        recipient_name = a.get("recipient_name") or tr_data.get("recipient_name") or "Recipient Shelter"
        recipient_phone = a.get("recipient_phone") or tr_data.get("recipient_phone") or "—"

        route_info = t.estimate_bengaluru_route(pickup_loc, delivery_loc)

        st.markdown(f"""
        <div class="as-card" style="border-left: 4px solid var(--purple); margin-bottom: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="font-size: 1.2rem; font-weight: 900; color: #1E1035;">
                    📦 Mission #{aid} — <span style="color: #0F766E;">{food_name}</span> ({qty} portions)
                </div>
                <div>
                    <span class="badge badge-purple">{status.upper()}</span>
                    <span class="badge badge-teal">~{route_info['distance_km']} km · ~{route_info['transit_mins']} mins</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_p, col_d = st.columns(2)
        with col_p:
            clean_dphone = donor_phone.replace(" ", "").replace("-", "")
            st.markdown(f"""
            <div class="as-card-sm" style="height: 100%;">
                <div style="font-size: 0.78rem; font-weight: 800; color: #6D28D9; text-transform: uppercase; letter-spacing: 0.05em;">
                    📍 STEP 1: PICKUP ORIGIN (DONOR)
                </div>
                <div style="font-size: 1.15rem; font-weight: 900; margin: 4px 0; color: #1E1035;">{donor_name}</div>
                <div style="font-size: 0.9rem; color: #374151; font-weight: 500;">📌 {pickup_loc}</div>
                <div style="margin-top: 8px;">
                    <a href="tel:{clean_dphone}" style="color: #0F766E; font-weight: 800; text-decoration: none;">
                        📞 Call Donor: {donor_phone}
                    </a>
                </div>
                <div style="font-size: 0.8rem; color: #6B7280; margin-top: 4px; font-weight: 500;">
                    Scheduled Pickup: {fmt_dt(a.get('pickup_time_scheduled'))}
                </div>
                <div style="margin-top: 8px;">
                    <a href="https://maps.google.com/?q={pickup_loc.replace(' ', '+')}" target="_blank" style="font-size: 0.84rem; color: #6D28D9; font-weight: 700;">
                        🗺️ Open Pickup in Google Maps ↗
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_d:
            clean_rphone = recipient_phone.replace(" ", "").replace("-", "")
            st.markdown(f"""
            <div class="as-card-sm" style="height: 100%;">
                <div style="font-size: 0.78rem; font-weight: 800; color: #BE123C; text-transform: uppercase; letter-spacing: 0.05em;">
                    🏠 STEP 2: DELIVERY DESTINATION (RECIPIENT)
                </div>
                <div style="font-size: 1.15rem; font-weight: 900; margin: 4px 0; color: #1E1035;">{recipient_name}</div>
                <div style="font-size: 0.9rem; color: #374151; font-weight: 500;">📌 {delivery_loc}</div>
                <div style="margin-top: 8px;">
                    <a href="tel:{clean_rphone}" style="color: #0F766E; font-weight: 800; text-decoration: none;">
                        📞 Call Recipient: {recipient_phone}
                    </a>
                </div>
                <div style="font-size: 0.8rem; color: #6B7280; margin-top: 4px; font-weight: 500;">
                    Delivery Target: Complete within perishable window
                </div>
                <div style="margin-top: 8px;">
                    <a href="https://maps.google.com/?q={delivery_loc.replace(' ', '+')}" target="_blank" style="font-size: 0.84rem; color: #6D28D9; font-weight: 700;">
                        🗺️ Open Destination in Google Maps ↗
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(135,61,245,0.06); border: 1.5px solid rgba(135,61,245,0.22); border-radius: 12px; padding: 12px 16px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-weight: 800; color: #6D28D9;">🛣️ Route Corridor:</span>
                    <span style="color: #1E1035; margin-left: 6px; font-weight: 600;">{route_info['summary']}</span>
                </div>
                <a href="{route_info['gmaps_url']}" target="_blank" style="color: #0F766E; font-weight: 800; font-size: 0.88rem;">
                    🗺️ Turn-by-Turn Navigation ↗
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        with bcol1:
            if status in ("assigned", "accepted"):
                if st.button("📍 Arrived at Donor", key=f"dest_arr_p_{aid}", use_container_width=True):
                    t.update_driver_live_tracking(aid, "at_pickup", f"Driver reached {pickup_loc[:20]}")
                    st.success("Recorded arrival at donor!")
                    st.rerun()
        with bcol2:
            if status in ("accepted", "at_pickup"):
                if st.button("📦 Confirm Food Loaded", key=f"dest_pic_{aid}", use_container_width=True):
                    t.update_driver_live_tracking(aid, "picked_up", "Food verified and loaded")
                    st.success("Food picked up! In transit.")
                    st.rerun()
        with bcol3:
            if status in ("picked_up", "in_transit"):
                if st.button("🏁 Arrived at Destination", key=f"dest_arr_d_{aid}", use_container_width=True, type="primary"):
                    t.update_driver_live_tracking(aid, "arrived_destination", f"Driver at recipient gate ({delivery_loc[:20]})", remaining_mins=0)
                    st.success("Destination reached! Recipient alerted.")
                    st.rerun()
        with bcol4:
            if status == "arrived_destination":
                st.info("Awaiting recipient handover confirmation.")


def volunteer_assignments():
    user = require_role("volunteer", "admin")
    import tools as t
    from guardrails import validate_delivery_status_transition

    vol = t.get_volunteer_by_user_id(user["id"])
    if not vol and user.get("role") == "admin":
        # Admin testing mode: view all volunteer assignments or pick Arjun Nair
        vols = t.get_all_volunteers()
        vol = vols[0] if vols else None

    if not vol:
        st.warning("Your account is not linked to a volunteer profile. Contact admin or register as a volunteer.")
        return

    st.markdown('<div class="section-title">📦 Volunteer Portal & Logistics Operations</div>', unsafe_allow_html=True)

    # Volunteer Profile & Milestones
    stats = t.get_volunteer_profile_stats(vol["id"])
    vol_badge = stats.get("badge_level", "Bronze Hero")
    badge_colors = {"Gold Guardian": "teal", "Silver Champion": "purple", "Bronze Hero": "yellow"}
    b_col = badge_colors.get(vol_badge, "yellow")

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(stats.get("active_trips", 0), "Active Pickups", "coral")
        + kpi_card(stats.get("completed_trips", 0), "Rescues Completed", "teal")
        + kpi_card(f"{stats.get('verified_hours', 0)} hrs", "Verified Hours")
        + kpi_card(f"₹{stats.get('reimbursement_due', 0):.0f}", "Fuel Stipend Due", "teal")
        + f'<div class="kpi kpi-{b_col}"><div class="kpi-val" style="font-size:1.2rem;margin-top:4px;">{vol_badge}</div><div class="kpi-lbl">Achievement Badge</div></div>'
        + '</div>',
        unsafe_allow_html=True
    )

    tab_tasks, tab_cert, tab_guidelines = st.tabs([
        "📦 My Assigned Rescues", 
        "🏅 Volunteer Recognition & Certificate", 
        "📘 Rescue Protocol & Reimbursement"
    ])

    with tab_tasks:
        assignments = t.get_assignments_for_volunteer(vol["id"])
        if not assignments:
            st.info("No active rescue assignments at the moment. You'll receive a notification when a nearby donation matches your capacity!")
        else:
            for a in assignments:
                status = a.get("status", "assigned")
                pickup_loc = a.get("pickup_location", "Donor location")
                drop_loc = a.get("delivery_address", a.get("delivery_location", "Recipient location"))
                route_info = t.estimate_bengaluru_route(pickup_loc, drop_loc)

                with st.expander(f"Assignment #{a['id']} — {a.get('recipient_name','Recipient')} | {status.upper()}", expanded=(status not in ("delivered","failed","cancelled"))):
                    col1, col2 = st.columns([1.3, 1])
                    with col1:
                        st.markdown(f"**🍱 Food Quantity:** `{a.get('allocated_quantity','—')} meals`")
                        st.markdown(f"**📍 Pickup Location:** {pickup_loc}")
                        st.markdown(f"**🏠 Delivery Destination:** {drop_loc}")
                        st.markdown(f"**⏰ Scheduled Pickup:** {fmt_dt(a.get('pickup_time_scheduled'))}")
                        
                        # Route Guidance
                        st.markdown(f"""
                        <div style="background:rgba(135,61,245,0.08);border:1px solid rgba(178,106,245,0.25);border-radius:10px;padding:8px 12px;margin:8px 0;">
                            <div style="font-size:0.75rem;font-weight:800;color:#6D28D9;text-transform:uppercase;">🗺️ Recommended Bengaluru Corridor</div>
                            <div style="font-size:0.88rem;color:#1E1035;margin-top:2px;font-weight:600;">{route_info['summary']}</div>
                            <div style="font-size:0.78rem;color:#6B5878;margin-top:2px;font-weight:500;">Estimated Transit: ~{route_info['transit_mins']} mins | Distance: {route_info['distance_km']} km</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"[↗ Open Navigation in Google Maps]({route_info['gmaps_url']})")

                    with col2:
                        st.write("**Driver Trip Controls:**")
                        st.markdown(status_badge(status), unsafe_allow_html=True)
                        st.write("")

                        if status == "assigned":
                            if st.button("Accept Assignment ✓", key=f"accept_{a['id']}", use_container_width=True):
                                t.update_driver_live_tracking(a["id"], "accepted", "Driver accepted trip & preparing departure")
                                st.success("Assignment accepted! Proceeding to pickup location.")
                                st.rerun()

                        if status in ("assigned", "accepted"):
                            if st.button("📍 Arrived at Donor Pickup", key=f"arr_pickup_{a['id']}", use_container_width=True):
                                t.update_driver_live_tracking(a["id"], "at_pickup", f"Driver arrived at donor location ({pickup_loc[:25]})")
                                st.success("Arrival recorded! Inspect meal packages before loading.")
                                st.rerun()

                        if status in ("accepted", "at_pickup"):
                            if st.button("Confirm Food Picked Up 📦", key=f"pickup_{a['id']}", use_container_width=True):
                                t.update_driver_live_tracking(a["id"], "picked_up", "Food verified and loaded into vehicle")
                                st.success("Pickup recorded! Transit initiated.")
                                st.rerun()

                        if status in ("picked_up", "in_transit"):
                            with st.popover("🚚 Update Live Checkpoint & ETA"):
                                st.caption("Broadcast live progress to donor and recipient.")
                                ck_choice = st.selectbox(
                                    "Route Checkpoint",
                                    [
                                        f"Departed {pickup_loc[:20]} — via {route_info['corridor']}",
                                        "Midway checkpoint: Passing Intermediate Ring Road / Domlur",
                                        f"Approaching destination corridor ({drop_loc[:20]})",
                                        "Custom checkpoint note"
                                    ],
                                    key=f"ck_choice_{a['id']}"
                                )
                                eta_slider = st.slider("Estimated Mins to Destination", 2, 45, int(a.get("estimated_remaining_mins") or 15), key=f"eta_{a['id']}")
                                if st.button("Broadcast Checkpoint ✓", key=f"btn_ck_{a['id']}", type="primary"):
                                    t.update_driver_live_tracking(a["id"], "in_transit", ck_choice, remaining_mins=eta_slider)
                                    st.success(f"Checkpoint broadcasted! Remaining ETA: {eta_slider} mins")
                                    st.rerun()

                            if st.button("🏁 Mark Arrived at Destination", key=f"arr_dest_{a['id']}", use_container_width=True, type="primary"):
                                t.update_driver_live_tracking(a["id"], "arrived_destination", f"Driver arrived at recipient gate ({drop_loc[:25]})", remaining_mins=0)
                                st.success("Destination reached! Recipient organisation has been alerted for handover.")
                                st.rerun()

                        if status == "arrived_destination":
                            st.markdown("""
                            <div style="background:rgba(22,166,154,0.15);border:1px solid #16A69A;border-radius:10px;padding:8px 12px;margin:6px 0;">
                                <strong style="color:#16A69A;">🏁 Arrived at Destination:</strong> Awaiting recipient staff to verify food quantity and acknowledge delivery.
                            </div>
                            """, unsafe_allow_html=True)

                        # Reassign / Decline option (Triggers Agent 3 Re-dispatch)
                        if status in ("assigned", "accepted"):
                            st.write("")
                            with st.popover("Decline / Reassign Assignment"):
                                st.caption("If you are unable to complete this pickup, Agent 3 will automatically find another available volunteer or vehicle so food is not delayed.")
                                decline_reason = st.text_input("Reason for cancellation", key=f"reason_{a['id']}", placeholder="Vehicle issue, urgent conflict, etc.")
                                if st.button("Confirm Decline & Reassign", key=f"btn_decline_{a['id']}", type="primary"):
                                    res = t.reassign_logistics_assignment(a["id"], decline_reason or "Volunteer unavailable", triggered_by="volunteer_decline")
                                    if res.get("success"):
                                        st.success(f"Assignment released. Agent 3 has re-dispatched to: {res.get('assigned_to')} ({res.get('transport_mode')})")
                                        st.rerun()
                                    else:
                                        st.error(res.get("error"))

    with tab_cert:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(135,61,245,0.12), rgba(22,166,154,0.12));
                    border: 2px solid #873DF5; border-radius: 18px; padding: 2rem 2.5rem; text-align: center;
                    margin: 1rem 0; box-shadow: 0 8px 32px rgba(135,61,245,0.15);">
            <div style="font-size: 2.2rem; margin-bottom: 6px;">🌾 📜</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: #B26AF5; letter-spacing: 0.15em; text-transform: uppercase;">
                GOVERNMENT OF KARNATAKA &amp; ANNA SETU ALLIANCE
            </div>
            <h2 style="font-size: 1.8rem; color: #FFFFFF; font-weight: 800; margin: 0.5rem 0;">
                CERTIFICATE OF VOLUNTEER SERVICE
            </h2>
            <div style="font-size: 0.95rem; color: #D4B8F0; margin: 0.5rem 0 1.2rem;">
                This certificate is proudly awarded to
            </div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #F07886; text-decoration: underline; text-decoration-color: #873DF5;">
                {vol['full_name']}
            </div>
            <div style="font-size: 0.9rem; color: #EAE0F8; max-width: 650px; margin: 1.2rem auto; line-height: 1.6;">
                In recognition of exceptional dedication and social commitment as an active Food Rescue Volunteer. 
                Successfully completed <strong>{stats['completed_trips']} food collection &amp; delivery missions</strong>, 
                contributing <strong>{stats['verified_hours']} verified community service hours</strong> to prevent surplus food waste 
                and nourish vulnerable communities across Bengaluru, Karnataka.
            </div>
            <div style="display: flex; justify-content: space-around; margin-top: 1.8rem; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 1.2rem;">
                <div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #16A69A;">{stats['badge_level']}</div>
                    <div style="font-size: 0.65rem; color: #C8B8E8;">ACHIEVEMENT RANK</div>
                </div>
                <div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF;">ANNA SETU CORE</div>
                    <div style="font-size: 0.65rem; color: #C8B8E8;">AGENTIC COORDINATION</div>
                </div>
                <div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #16A69A;">VERIFIED AUTHENTIC</div>
                    <div style="font-size: 0.65rem; color: #C8B8E8;">AS-VOL-2026-{vol['id']:04d}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("ℹ️ This certificate can be included in college NSS/Rotaract records, corporate CSR volunteer profiles, or career portfolios.")

    with tab_guidelines:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("""
            <div class="as-card">
              <div class="section-title">🛡️ Food Transport Safety Rules</div>
              <ul style="padding-left:1.2rem;line-height:1.7;">
                <li>Cover all cooked food containers tightly during transport.</li>
                <li>Keep vegetarian and non-vegetarian food strictly segregated.</li>
                <li>Never expose food packets to direct sunlight or rain.</li>
                <li>Verify recipient organisation identity upon arrival before handover.</li>
                <li>Promptly update delivery status to trigger recipient acknowledgement.</li>
              </ul>
            </div>
            """, unsafe_allow_html=True)
        with col_g2:
            st.markdown(f"""
            <div class="as-card">
              <div class="section-title">⛽ Travel Stipend &amp; Expenses</div>
              <p>Anna Setu coordinates travel reimbursements supported by corporate CSR partners:</p>
              <ul style="padding-left:1.2rem;line-height:1.7;">
                <li>Two-Wheeler: ₹25 per completed rescue trip.</li>
                <li>Four-Wheeler / Car: ₹50 per completed rescue trip.</li>
                <li>Current balance due to you: <strong>₹{stats['reimbursement_due']:.0f}</strong></li>
              </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Request Stipend Reimbursement Settlement", key="btn_claim_stipend"):
                st.success("Stipend claim submitted to Anna Setu operations for direct bank transfer settlement!")


# ══════════════════════════════════════════════
# ADMIN PAGES
# ══════════════════════════════════════════════

def admin_overview():
    user = require_role("admin")
    import tools as t
    import database as db
    import pandas as pd

    report = t.generate_impact_report()
    donations = t.get_all_donations()
    pending_approvals = t.get_human_approvals("pending")

    # Phase 2 metrics
    org_counts = t.get_organisation_counts()
    reg_donors = len(t.get_all_donor_orgs())
    active_donations = len([d for d in donations if d.get("status") in ("pending_screening", "screening_passed", "matched")])
    try:
        active_requests = db.execute_query("SELECT COUNT(*) AS c FROM recipient_requests WHERE status IN ('submitted', 'referred_to_org')")[0]['c']
        urgent_requests = db.execute_query("SELECT COUNT(*) AS c FROM recipient_requests WHERE urgency_level IN ('Urgent', 'Critical')")[0]['c']
    except Exception:
        active_requests = 0
        urgent_requests = 0
    recent_matches = len(t.get_matches_with_details())

    st.markdown('<div class="section-title">📊 Admin Command Center — Bengaluru Citywide Operations</div>', unsafe_allow_html=True)
    st.caption("Citywide multi-agent orchestration, live driver fleet telemetry, and real-time food rescue operations.")
    ai_status_bar()

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(reg_donors, "Registered Donors")
        + kpi_card(active_donations, "Active Donations", "teal")
        + kpi_card(active_requests, "Active Recipient Requests")
        + kpi_card(f"{org_counts['real_count']} <small style='font-size:0.8rem'>({org_counts['demo_count']} demo)</small>", "Support Organisations", "coral")
        + kpi_card(urgent_requests, "Urgent Requests", "coral")
        + kpi_card(recent_matches, "Recent Matches", "teal")
        + '</div>',
        unsafe_allow_html=True
    )

    # ── Quick Action Command Bar ──
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("🚚 Fleet Command & Dispatch", use_container_width=True, key="admin_qc_fleet"):
            st.session_state["nav_override"] = "🚚 Fleet Command & Driver Tracking"
            st.rerun()
    with qc2:
        if st.button("✅ Review Match Approvals", use_container_width=True, key="admin_qc_approvals"):
            st.session_state["nav_override"] = "✅ Match Approvals"
            st.rerun()
    with qc3:
        if st.button("🚨 View Safety Alerts", use_container_width=True, key="admin_qc_safety"):
            st.session_state["nav_override"] = "🚨 Safety Alerts"
            st.rerun()
    with qc4:
        if st.button("🎬 Run Live End-to-End Demo", use_container_width=True, key="admin_qc_demo"):
            st.session_state["nav_override"] = "🎬 Run Demo"
            st.rerun()

    st.write("")

    # ── Live Fleet Map & Driver Tracking ──
    st.markdown("### 🗺️ Real-Time Fleet & Driver Locations across Bengaluru")
    st.caption("Live GPS telemetry stream of dispatched drivers, active checkpoints, and destination arrival status.")
    
    active_drivers = t.get_all_active_driver_locations()
    if active_drivers:
        map_data = []
        for d in active_drivers:
            map_data.append({
                "lat": float(d["latitude"]),
                "lon": float(d["longitude"]),
            })
        st.map(pd.DataFrame(map_data), zoom=11, use_container_width=True)

        st.markdown("##### 📍 Active Telemetry Stream")
        for d in active_drivers:
            status = d["status"]
            arr_badge = '<span class="badge badge-green">🏁 Arrived at Destination</span>' if status in ("arrived_destination", "delivered") else f'<span class="badge badge-blue">~{d["remaining_mins"]} mins away</span>'
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid rgba(135,61,245,0.18);border-radius:10px;padding:12px 16px;margin-bottom:8px;box-shadow:0 2px 8px rgba(135,61,245,0.06);">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <strong style="color:#1E1035;font-size:0.98rem;font-weight:800;">🚴 {d['driver_name']}</strong> ({d['vehicle_type'].upper()}) · 📞 <a href="tel:{d['driver_phone']}" style="color:#0F766E;font-weight:700;">{d['driver_phone']}</a>
                        <div style="font-size:0.82rem;color:#4B5563;margin-top:3px;font-weight:500;">
                            📍 <strong style="color:#6D28D9;">Checkpoint:</strong> {d['checkpoint']} → 🏠 <strong style="color:#0F766E;">Destination:</strong> {d['destination_name']}
                        </div>
                    </div>
                    <div>{arr_badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Default Bengaluru Map
        default_map = pd.DataFrame([{"lat": 12.9716, "lon": 77.5946}])
        st.map(default_map, zoom=10, use_container_width=True)
        st.info("ℹ️ No drivers currently in transit. Use '🎬 Run Demo' or dispatch a delivery to see live real-time driver movement across Bengaluru.")


def admin_support_organisations_management():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🏛️ Manage Support Organisations Directory</div>', unsafe_allow_html=True)
    st.caption("Admin control panel for verifying, adding, editing, and updating availability status of Bengaluru food-support organisations.")
    ai_status_bar()

    tab1, tab2 = st.tabs(["📋 Directory Records", "➕ Add New Organisation"])
    with tab1:
        include_demo = st.checkbox("Show Demo Records", value=True, key="admin_show_demo_cb")
        records, total = t.get_support_organisations_directory(include_demo=include_demo, limit=300)
        st.write(f"Total Organisations in DB: **{total}**")

        df_display = [{
            "ID": r["organisation_id"],
            "Name": r["organisation_name"],
            "Type": r["organisation_type"],
            "Locality": r.get("locality") or "—",
            "Phone": r.get("contact_phone") or "—",
            "Availability": r.get("availability_status", "unknown"),
            "Can Distribute": r.get("can_distribute_food"),
            "Beneficiary": r.get("is_beneficiary_institution"),
            "Demo": r.get("is_synthetic"),
            "Active": r.get("is_active"),
        } for r in records]
        st.dataframe(pd.DataFrame(df_display), use_container_width=True, hide_index=True)

        st.markdown("#### ✏️ Edit Organisation Record")
        org_ids = [r["organisation_id"] for r in records]
        if org_ids:
            selected_org_id = st.selectbox(
                "Select Organisation to Edit",
                org_ids,
                format_func=lambda oid: f"#{oid} - {next((r['organisation_name'] for r in records if r['organisation_id'] == oid), '')}"
            )
            curr_org = next((r for r in records if r["organisation_id"] == selected_org_id), None)
            if curr_org:
                with st.form("edit_org_form"):
                    e_name = st.text_input("Organisation Name", value=curr_org["organisation_name"])
                    avail_options = ["unknown", "contact_to_confirm", "confirmed_available", "temporarily_unavailable"]
                    curr_avail = curr_org.get("availability_status", "unknown")
                    avail_idx = avail_options.index(curr_avail) if curr_avail in avail_options else 0
                    e_avail = st.selectbox("Availability Status", avail_options, index=avail_idx)
                    e_phone = st.text_input("Phone", value=curr_org.get("contact_phone") or "")
                    e_email = st.text_input("Email", value=curr_org.get("contact_email") or "")
                    e_can_dist = st.checkbox("Can Distribute Food", value=curr_org.get("can_distribute_food", False))
                    admin_reason = st.text_input("Mandatory Reason for Modification *", placeholder="Reason required for audit logging")

                    col_save, col_deact = st.columns(2)
                    with col_save:
                        save_btn = st.form_submit_button("Update Organisation", use_container_width=True)
                    with col_deact:
                        deact_btn = st.form_submit_button("Deactivate (Soft-Delete)", use_container_width=True)

                    if save_btn:
                        if not admin_reason.strip():
                            st.error("Admin reason is mandatory for audit logging.")
                        else:
                            t.admin_update_organisation(selected_org_id, {
                                "organisation_name": e_name,
                                "contact_phone": e_phone or None,
                                "contact_email": e_email or None,
                                "availability_status": e_avail,
                                "can_distribute_food": e_can_dist
                            }, user["id"], admin_reason)
                            st.success(f"Organisation #{selected_org_id} updated successfully!")
                            st.rerun()

                    if deact_btn:
                        if not admin_reason.strip():
                            st.error("Admin reason is mandatory for audit logging.")
                        else:
                            t.admin_soft_delete_organisation(selected_org_id, user["id"], admin_reason)
                            st.warning(f"Organisation #{selected_org_id} deactivated.")
                            st.rerun()

    with tab2:
        with st.form("add_org_form"):
            st.markdown("#### Add Verified Organisation")
            a_name = st.text_input("Organisation Name *")
            a_type = st.selectbox("Type *", ["food_bank", "food_redistribution_org", "community_kitchen", "ngo", "shelter", "orphanage", "old_age_home"])
            a_address = st.text_area("Address *")
            a_locality = st.text_input("Locality *", value="Bengaluru Urban")
            a_phone = st.text_input("Contact Phone")
            a_email = st.text_input("Contact Email")
            a_web = st.text_input("Website URL")
            a_services = st.text_input("Food Services")
            a_source_name = st.text_input("Verification Source Name *", value="Official Directory Verification")
            a_source_url = st.text_input("Source URL *", value="https://sharefood.eatrightindia.gov.in/agency-list.html")
            a_dist = st.checkbox("Can Distribute Food", value=True)
            a_ben = st.checkbox("Is Beneficiary Institution", value=False)
            a_reason = st.text_input("Reason for adding record *")
            add_btn = st.form_submit_button("Add Verified Organisation")
            if add_btn:
                if not a_name or not a_source_name or not a_source_url or not a_reason:
                    st.error("Please fill all required fields and provide a reason.")
                else:
                    new_id = t.admin_add_organisation({
                        "organisation_name": a_name,
                        "organisation_type": a_type,
                        "address": a_address,
                        "locality": a_locality,
                        "city": "Bengaluru",
                        "contact_phone": a_phone or None,
                        "contact_email": a_email or None,
                        "website_url": a_web or None,
                        "food_services": a_services or None,
                        "source_name": a_source_name,
                        "source_url": a_source_url,
                        "last_verified_at": datetime.now(timezone.utc),
                        "verification_status": "listed_in_source",
                        "availability_status": "unknown",
                        "can_distribute_food": a_dist,
                        "is_beneficiary_institution": a_ben,
                        "is_synthetic": False
                    }, user["id"], a_reason)
                    st.success(f"Added new organization with ID #{new_id}")
                    st.rerun()


    # Delivery breakdown
    breakdown = report.get("delivery_breakdown", {})
    if breakdown:
        st.markdown('<div class="section-title">🚚 Delivery Status Breakdown</div>', unsafe_allow_html=True)
        col_items = list(breakdown.items())
        cols = st.columns(len(col_items) or 1)
        for i, (s, c) in enumerate(col_items):
            with cols[i]:
                st.markdown(f'<div class="kpi"><div class="kpi-val">{c}</div><div class="kpi-lbl">{s.replace("_"," ").title()}</div></div>',
                            unsafe_allow_html=True)

    # Recent donations
    st.markdown('<div class="section-title">📋 Recent Donations</div>', unsafe_allow_html=True)
    if donations:
        rows = [{
            "ID": d["id"], "Donor": d.get("donor_name","—"),
            "Food": d["food_name"][:30], "Qty": f"{d['quantity']} {d['unit']}",
            "Status": d["status"], "City": d.get("city","—"),
            "Created": fmt_dt(d.get("created_at"))
        } for d in donations[:20]]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Impact narrative
    if report.get("narrative"):
        st.markdown(f'<div class="alert-info">🤖 {report["narrative"]}</div>', unsafe_allow_html=True)


def admin_match_approvals():
    user = require_role("admin")
    import tools as t
    from agents import run_logistics_workflow

    pending = t.get_human_approvals("pending")
    match_approvals = [a for a in pending if a.get("entity_type") == "match"]

    st.markdown('<div class="section-title">✅ Match Approval Queue</div>', unsafe_allow_html=True)

    if not match_approvals:
        st.success("No pending match approvals.")
    else:
        for approval in match_approvals:
            match_id = approval.get("entity_id")
            match = t.get_match(match_id)
            if not match:
                continue
            with st.expander(f"Match #{match_id} — {approval.get('reason','')[:80]}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Donation ID:** {match.get('donation_id','—')}")
                    st.write(f"**Recipient Org ID:** {match.get('recipient_org_id','—')}")
                    st.write(f"**Allocated Qty:** {match.get('allocated_quantity','—')} meals")
                    st.write(f"**Match Score:** {match.get('match_score','—')}")
                    st.write(f"**Reason:** {(match.get('match_reason','') or '')[:200]}")
                with col2:
                    st.markdown(status_badge(match.get("status","")), unsafe_allow_html=True)
                    col_a, col_r = st.columns(2)
                    with col_a:
                        if st.button(f"✅ Approve", key=f"approve_match_{match_id}"):
                            t.approve_match(match_id, user["id"])
                            # Trigger Agent 3 & 4
                            donation_id = match.get("donation_id")
                            with st.spinner("Running Agent 3 (logistics) + Agent 4 (tracking)…"):
                                run_logistics_workflow(donation_id, [match_id])
                            from database import log_audit
                            log_audit(user["id"], user["username"], "admin", "approve_match", "match", match_id)
                            st.success(f"Match #{match_id} approved and logistics started!")
                            st.rerun()
                    with col_r:
                        if st.button(f"❌ Reject", key=f"reject_match_{match_id}"):
                            notes = st.text_input("Rejection reason", key=f"rej_note_{match_id}")
                            t.reject_match(match_id, user["id"], notes)
                            st.warning(f"Match #{match_id} rejected.")
                            st.rerun()


def admin_food_safety_alerts():
    user = require_role("admin")
    import tools as t
    from database import execute_query

    st.markdown('<div class="section-title">🚨 Food Safety Alerts</div>', unsafe_allow_html=True)

    pending_safety = t.get_human_approvals("pending")
    safety_items = [a for a in pending_safety if a.get("entity_type") == "donation"]

    if not safety_items:
        st.success("No pending food safety reviews.")
    else:
        for item in safety_items:
            don_id = item.get("entity_id")
            donation = t.get_donation(don_id)
            safety   = t.get_food_safety_record(don_id)
            with st.expander(f"⚠️ Donation #{don_id} — Safety Review Required", expanded=True):
                if donation:
                    st.write(f"**Food:** {donation.get('food_name','—')} | "
                             f"**Category:** {donation.get('food_category','—')} | "
                             f"**Qty:** {donation.get('quantity','—')} meals")
                    st.write(f"**Location:** {donation.get('location','—')}")
                if safety:
                    score = float(safety.get("safety_score", 0))
                    if score < 4:
                        st.markdown(f'<div class="alert-danger">Safety Score: {score}/10 — HIGH RISK</div>', unsafe_allow_html=True)
                    elif score < 7:
                        st.markdown(f'<div class="alert-warn">Safety Score: {score}/10 — Review Needed</div>', unsafe_allow_html=True)
                    st.write(f"**Issues:** {safety.get('issues_found','—')}")
                    st.write(f"**Recommendations:** {safety.get('recommendations','—')}")

                notes_key = f"safety_notes_{item['id']}"
                reviewer_notes = st.text_area("Reviewer Notes", key=notes_key)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Clear for Matching", key=f"clear_{item['id']}"):
                        t.update_donation_status(don_id, "screening_passed", "admin")
                        from database import execute_query as eq
                        from sqlalchemy import text
                        from database import engine
                        with engine.connect() as conn:
                            conn.execute(text(
                                "UPDATE as_human_approvals SET status='approved', review_notes=:n, resolved_at=:ra "
                                "WHERE id=:id"
                            ), {"n": reviewer_notes, "ra": datetime.now(timezone.utc), "id": item["id"]})
                            conn.execute(text(
                                "UPDATE as_food_safety SET human_reviewed=TRUE, reviewer_notes=:n WHERE donation_id=:did"
                            ), {"n": reviewer_notes, "did": don_id})
                            conn.commit()
                        st.success("Donation cleared for matching!")
                        st.rerun()
                with col2:
                    if st.button("🚫 Block Donation", key=f"block_{item['id']}"):
                        t.update_donation_status(don_id, "screening_failed", "admin")
                        from database import engine
                        from sqlalchemy import text
                        with engine.connect() as conn:
                            conn.execute(text(
                                "UPDATE as_human_approvals SET status='rejected', review_notes=:n, resolved_at=:ra WHERE id=:id"
                            ), {"n": reviewer_notes, "ra": datetime.now(timezone.utc), "id": item["id"]})
                            conn.commit()
                        st.warning("Donation blocked.")
                        st.rerun()


def admin_logistics_dispatch():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🚚 Logistics & Fleet Dispatch Center</div>', unsafe_allow_html=True)
    ai_status_bar()

    board = t.get_logistics_dispatch_board()
    transports = t.get_transport_providers()
    vols = t.get_all_volunteers()

    active_cnt = len([b for b in board if b.get("assignment_status") in ("assigned", "accepted", "picked_up", "in_transit")])
    in_transit_cnt = len([b for b in board if b.get("assignment_status") == "in_transit"])
    delivered_cnt = len([b for b in board if b.get("assignment_status") == "delivered"])
    avail_vols = len([v for v in vols if v.get("is_available")])
    avail_fleet = len([tr for tr in transports if tr.get("is_available")])

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(active_cnt, "Active Dispatches", "coral")
        + kpi_card(in_transit_cnt, "In-Transit", "teal")
        + kpi_card(delivered_cnt, "Delivered", "teal")
        + kpi_card(avail_vols, "Volunteers Available")
        + kpi_card(avail_fleet, "Fleet Vehicles Ready", "purple")
        + '</div>',
        unsafe_allow_html=True
    )

    tab_map, tab_board, tab_fleet, tab_vols = st.tabs([
        "🗺️ Bengaluru Live Fleet Map",
        "📋 Live Dispatch Board",
        "🏢 Travel & Logistics Partners",
        "🚴 Volunteer Rescuers Roster"
    ])

    with tab_map:
        st.markdown("#### 🗺️ Real-Time Fleet & Driver Locations across Bengaluru")
        st.caption("Live GPS telemetry of dispatched drivers, active checkpoints, and destination arrival status.")
        active_drivers = t.get_all_active_driver_locations()
        if not active_drivers:
            st.info("No drivers currently in transit. Dispatches will appear on the map in real time as trips commence.")
        else:
            map_data = []
            for d in active_drivers:
                map_data.append({
                    "lat": float(d["latitude"]),
                    "lon": float(d["longitude"]),
                    "Driver": d["driver_name"],
                    "Vehicle": d["vehicle_type"],
                    "Status": d["status"],
                    "Checkpoint": d["checkpoint"]
                })
            st.map(pd.DataFrame(map_data), zoom=11, use_container_width=True)

            st.write("")
            st.markdown("##### 📍 Active Telemetry Stream")
            for d in active_drivers:
                status = d["status"]
                arr_badge = '<span class="badge badge-green">🏁 Arrived at Destination</span>' if status in ("arrived_destination", "delivered") else f'<span class="badge badge-blue">~{d["remaining_mins"]} mins away</span>'
                st.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid rgba(135,61,245,0.18);border-radius:10px;padding:12px 16px;margin-bottom:8px;box-shadow:0 2px 8px rgba(135,61,245,0.06);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <strong style="color:#1E1035;font-size:0.98rem;font-weight:800;">🚴 {d['driver_name']}</strong> ({d['vehicle_type'].upper()}) · 📞 <a href="tel:{d['driver_phone']}" style="color:#0F766E;font-weight:700;">{d['driver_phone']}</a>
                            <div style="font-size:0.82rem;color:#4B5563;margin-top:3px;font-weight:500;">
                                📍 <strong style="color:#6D28D9;">Checkpoint:</strong> {d['checkpoint']} → 🏠 <strong style="color:#0F766E;">Destination:</strong> {d['destination_name']}
                            </div>
                        </div>
                        <div>{arr_badge}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_board:
        st.markdown("#### 🔄 Agent 3 Collection Assignments & Fleet Operations")
        filter_status = st.selectbox("Filter Status", ["All", "Active Only", "assigned", "accepted", "picked_up", "in_transit", "delivered", "cancelled"], index=0)
        
        filtered_board = board
        if filter_status == "Active Only":
            filtered_board = [b for b in board if b.get("assignment_status") in ("assigned", "accepted", "picked_up", "in_transit")]
        elif filter_status != "All":
            filtered_board = [b for b in board if b.get("assignment_status") == filter_status]

        if not filtered_board:
            st.info("No assignments match the selected filter.")
        else:
            for b in filtered_board:
                status = b.get("assignment_status", "assigned")
                mode = b.get("transport_mode", "volunteer")
                aid = b["assignment_id"]
                
                mode_badge = {
                    "volunteer": '<span class="badge badge-teal">Volunteer Rescuer</span>',
                    "ngo_vehicle": '<span class="badge badge-green">NGO Van</span>',
                    "paid_logistics": '<span class="badge badge-purple">Commercial Paid</span>',
                    "sponsored_transport": '<span class="badge badge-blue">CSR Sponsored</span>',
                    "unassigned_alert": '<span class="badge badge-red">Needs Allocation</span>'
                }.get(mode, f'<span class="badge badge-gray">{mode}</span>')

                with st.expander(f"Dispatch #{aid} | {b.get('food_name','Meals')} ({b.get('allocated_quantity',0)} meals) | {status.upper()}", expanded=(status in ("assigned","in_transit"))):
                    c1, c2, c3 = st.columns([1.2, 1.2, 0.9])
                    with c1:
                        st.markdown(f"**🍱 Food:** {b.get('food_name')} ({b.get('allocated_quantity')} portions)")
                        st.markdown(f"**🏢 Donor Org:** {b.get('donor_name','Donor')} (📞 {b.get('donor_phone','—')})")
                        st.markdown(f"**📍 Pickup Location:** {b.get('pickup_location','—')}")
                        st.markdown(f"**⏰ Scheduled:** {fmt_dt(b.get('pickup_time_scheduled'))}")
                    with c2:
                        st.markdown(f"**🏠 Recipient:** {b.get('recipient_name','Recipient')} (📞 {b.get('recipient_phone','—')})")
                        st.markdown(f"**📍 Delivery Destination:** {b.get('delivery_location','—')}")
                        st.markdown(f"**🗺️ Route Corridor:** {b.get('route_summary') or 'Direct corridor'}")
                        st.markdown(f"**📏 Metrics:** `{b.get('estimated_distance_km', 5.0)} km` | `~{b.get('estimated_transit_mins', 25)} mins`")
                    with c3:
                        st.markdown(f"**Mode:** {mode_badge}", unsafe_allow_html=True)
                        st.markdown(f"**Status:** {status_badge(status)}", unsafe_allow_html=True)
                        if b.get("volunteer_name"):
                            st.markdown(f"**Rescuer:** 🚴 {b.get('volunteer_name')} ({b.get('volunteer_phone','—')})")
                        elif b.get("transport_provider_name"):
                            st.markdown(f"**Fleet:** 🚛 {b.get('transport_provider_name')} ({b.get('transport_provider_phone','—')})")
                        if b.get("delivery_cost") and float(b.get("delivery_cost")) > 0:
                            st.markdown(f"**Trip Charge:** ₹{float(b['delivery_cost']):.2f}")
                        if b.get("sponsor_name"):
                            st.caption(f"Sponsored by: {b['sponsor_name']}")

                        # Manual / Agent Reassign Trigger
                        if status in ("assigned", "accepted", "delayed"):
                            st.write("")
                            with st.popover("⚡ Reassign / Escalate Dispatch"):
                                st.caption("Re-dispatches this collection through Agent 3 to an alternative volunteer or paid fleet partner.")
                                r_reason = st.text_input("Reassignment reason", key=f"admin_reassign_reason_{aid}", placeholder="Delay, vehicle change, etc.")
                                if st.button("Execute Reassignment", key=f"btn_admin_reassign_{aid}", type="primary"):
                                    res = t.reassign_logistics_assignment(aid, r_reason or "Admin manual reassign", triggered_by="admin_override")
                                    if res.get("success"):
                                        st.success(f"Re-dispatched to: {res.get('assigned_to')} ({res.get('transport_mode')})")
                                        st.rerun()
                                    else:
                                        st.error(res.get("error"))

    with tab_fleet:
        st.markdown("#### 🚛 Commercial, NGO & CSR Transport Partners")
        st.caption("Agent 3 draws from this partner network when food volume exceeds volunteer vehicle capacity or during urgent deadlines.")
        
        fleet_rows = []
        for tr in transports:
            fleet_rows.append({
                "ID": tr["id"],
                "Provider Name": tr["name"],
                "Vehicle Type": tr.get("vehicle_type", "tempo"),
                "Capacity (Meals)": tr.get("capacity_meals", 200),
                "Classification": tr.get("service_type", "Commercial"),
                "Base Locality": tr.get("locality", "Bengaluru"),
                "Trip Cost (₹)": f"₹{float(tr.get('cost_per_trip') or 0):.0f}",
                "Contact": tr.get("contact_phone", "—"),
                "Ready": "🟢 Active" if tr.get("is_available") else "🔴 Offline"
            })
        st.dataframe(pd.DataFrame(fleet_rows), use_container_width=True, hide_index=True)

    with tab_vols:
        st.markdown("#### 🚴 Registered Community Volunteers Roster")
        st.caption("Verified community rescuers mapped across Bengaluru with achievement ranks and vehicle capacities.")
        vol_rows = []
        for v in vols:
            vol_rows.append({
                "ID": v["id"],
                "Volunteer Name": v["full_name"],
                "Locality": v.get("locality", v.get("address", "Bengaluru")),
                "Vehicle": v.get("vehicle_type", "bike"),
                "Meal Capacity": v.get("vehicle_capacity_meals", 20),
                "Rank Badge": v.get("badge_level", "Bronze Hero"),
                "Hours Logged": f"{float(v.get('total_hours_volunteered') or 0):.1f} hrs",
                "Contact": v.get("phone", "—"),
                "Available": "🟢 Available" if v.get("is_available") else "🔴 Busy"
            })
        st.dataframe(pd.DataFrame(vol_rows), use_container_width=True, hide_index=True)


def admin_delivery_monitoring():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🚚 Delivery Monitoring</div>', unsafe_allow_html=True)
    deliveries = t.get_deliveries()

    if not deliveries:
        st.info("No deliveries recorded yet.")
        return

    rows = [{
        "ID":         dl["id"],
        "Food":       dl.get("food_name","—")[:25],
        "Recipient":  dl.get("recipient_name","—")[:25],
        "Assigned Qty": dl.get("allocated_quantity","—"),
        "Actual Qty": dl.get("actual_quantity","—") or "—",
        "Status":     dl.get("status","—"),
        "Acknowledged": "✅" if dl.get("recipient_acknowledged") else "❌",
        "Pickup At":  fmt_dt(dl.get("pickup_at")),
        "Delivered":  fmt_dt(dl.get("delivered_at")),
    } for dl in deliveries]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def admin_impact_report():
    user = require_role("admin")
    import tools as t

    st.markdown('<div class="section-title">📈 Impact Analytics</div>', unsafe_allow_html=True)
    report = t.generate_impact_report()

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(report.get("total_donations",0),   "Total Donations")
        + kpi_card(report.get("delivered_donations",0),"Delivered", "teal")
        + kpi_card(report.get("confirmed_meals",0),    "Confirmed Meals", "coral")
        + kpi_card(report.get("orgs_served",0),        "Orgs Served")
        + kpi_card(report.get("volunteers_engaged",0), "Volunteers Engaged")
        + '</div>', unsafe_allow_html=True
    )

    if report.get("narrative"):
        st.markdown(f'<div class="alert-info">🤖 <strong>AI Summary:</strong> {report["narrative"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="alert-info">📊 <strong>Summary:</strong> Anna Setu has processed '
            f'{report.get("total_donations",0)} donations, confirming '
            f'{report.get("confirmed_meals",0)} meals delivered to '
            f'{report.get("orgs_served",0)} organisations with the help of '
            f'{report.get("volunteers_engaged",0)} volunteers. '
            f'(All statistics derived from confirmed PostgreSQL records only.)</div>',
            unsafe_allow_html=True
        )

    st.caption(f"Report generated: {fmt_dt(report.get('generated_at'))} | Source: {report.get('source','database')}")


def admin_audit_logs():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">📝 Audit Logs</div>', unsafe_allow_html=True)
    logs = t.get_audit_logs(limit=100)
    if not logs:
        st.info("No audit events yet.")
        return
    rows = [{
        "ID": l["id"], "User": l.get("username","—"), "Role": l.get("role","—"),
        "Action": l.get("action","—"), "Entity": l.get("entity_type","—"),
        "EntityID": l.get("entity_id","—"),
        "Time": fmt_dt(l.get("created_at"))
    } for l in logs]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def admin_agent_logs():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🤖 Agent Activity Logs</div>', unsafe_allow_html=True)
    logs = t.get_agent_logs(limit=100)
    if not logs:
        st.info("No agent activity yet.")
        return
    rows = [{
        "ID": l["id"], "Agent": l.get("agent_name","—"),
        "Action": l.get("action","—"), "Entity": l.get("entity_type","—"),
        "Model": l.get("model_used","—"),
        "Success": "✅" if l.get("success") else "❌",
        "Output": (l.get("output_summary","") or "")[:60],
        "Time": fmt_dt(l.get("created_at"))
    } for l in logs]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def admin_volunteers():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🚴 Volunteer Management</div>', unsafe_allow_html=True)
    vols = t.get_all_volunteers()
    if not vols:
        st.info("No volunteers registered.")
        return
    rows = [{
        "ID": v["id"], "Name": v["full_name"], "City": v.get("city","—"),
        "Vehicle": v.get("vehicle_type","—"), "Capacity": v.get("vehicle_capacity_meals","—"),
        "Available": "✅" if v.get("is_available") else "❌",
    } for v in vols]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def admin_recipients():
    user = require_role("admin")
    import tools as t
    import pandas as pd

    st.markdown('<div class="section-title">🏠 Recipient Organisation Management</div>', unsafe_allow_html=True)
    orgs = t.get_all_recipient_orgs()
    if not orgs:
        st.info("No recipient organisations.")
        return
    rows = [{
        "ID": o["id"], "Name": o["name"], "Type": o.get("org_type","—"),
        "City": o.get("city","—"), "Capacity/Day": o.get("capacity_meals_per_day","—"),
        "Dietary": o.get("dietary_restrictions","any"),
    } for o in orgs]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def admin_run_demo():
    user = require_role("admin")
    import tools as t
    from agents import run_donation_workflow, run_logistics_workflow
    from database import log_audit

    st.markdown('<div class="section-title">🎬 Run Live Demo Scenario</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="as-card">
    <strong>Demo Scenario:</strong> Royal Orchid Wedding Hall registers 100 vegetarian meal packets.
    <ul>
    <li>Agent 1 validates and screens the donation</li>
    <li>Agent 2 matches 70 packets to a shelter and 30 to a community kitchen</li>
    <li>Admin approves the matches</li>
    <li>Agent 3 assigns volunteers and transport</li>
    <li>Agent 4 tracks deliveries</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Execute Full Demo Workflow"):
        # Find donor org
        donor_orgs = t.get_all_donor_orgs()
        wedding_hall = next((d for d in donor_orgs if "Royal Orchid" in d["name"]), None)
        if not wedding_hall:
            st.error("Royal Orchid Wedding Hall not found in database. Run seed data first.")
            return

        from database import execute_query
        demo_user = execute_query("SELECT id FROM as_users WHERE username='donor_raj'")
        donor_user_id = demo_user[0]["id"] if demo_user else user["id"]

        pickup_deadline = datetime.now(timezone.utc) + timedelta(hours=6)
        prep_time       = datetime.now(timezone.utc) - timedelta(hours=1)

        with st.spinner("Step 1/4: Agent 1 — Registering & screening donation…"):
            result = t.register_donation(
                donor_org_id=wedding_hall["id"],
                donor_user_id=donor_user_id,
                food_name="Vegetarian Wedding Meal Packets (DEMO)",
                food_category="cooked_meals",
                dietary_type="vegetarian",
                quantity=100,
                unit="meals",
                preparation_time=prep_time,
                pickup_deadline=pickup_deadline,
                location="Indiranagar, Bengaluru",
                city="Bengaluru",
                packaging="sealed",
                storage_condition="ambient",
                allergen_info="Contains dairy",
                notes="[DEMO DATA] Wedding banquet surplus — 100 vegetarian meals",
                is_demo=True,
            )
            donation_id = result["donation_id"]
            workflow_state = run_donation_workflow(donation_id)
            screening = workflow_state.get("screening_result","—")

        st.markdown(f'<div class="alert-{"safe" if screening=="eligible" else "warn"}">Step 1 ✅ — Screening result: <strong>{screening}</strong></div>', unsafe_allow_html=True)

        matches_proposed = workflow_state.get("proposed_matches", [])
        match_ids = workflow_state.get("match_ids", [])

        if matches_proposed:
            st.markdown(f'<div class="alert-info">Step 2 ✅ — Agent 2 proposed {len(matches_proposed)} matches:</div>', unsafe_allow_html=True)
            for m in matches_proposed:
                st.markdown(f'&nbsp;&nbsp;🏠 **{m["recipient_name"]}** — {m["allocated_quantity"]} meals (score {m["match_score"]:.1f})')

        if match_ids:
            st.markdown('<div class="alert-warn">Step 3 — Admin approval required. Approving now…</div>', unsafe_allow_html=True)
            with st.spinner("Approving matches and running Agent 3 & 4…"):
                for mid in match_ids:
                    t.approve_match(mid, user["id"])
                logistics_state = run_logistics_workflow(donation_id, match_ids)

            assignments = logistics_state.get("assignment_details", [])
            if assignments:
                st.markdown(f'<div class="alert-safe">Step 3 ✅ — Agent 3 created {len(assignments)} assignments:</div>', unsafe_allow_html=True)
                for a in assignments:
                    st.markdown(f'&nbsp;&nbsp;🚴 Volunteer: **{a.get("volunteer","—")}** | Transport: {a.get("transport","—")} | Pickup: {fmt_dt(a.get("pickup_time"))}')

            impact = logistics_state.get("impact_report", {})
            st.markdown(
                f'<div class="alert-info">Step 4 ✅ — Agent 4 tracking active.<br>'
                f'Platform totals: <strong>{impact.get("confirmed_meals",0)}</strong> confirmed meals | '
                f'<strong>{impact.get("orgs_served",0)}</strong> orgs served</div>',
                unsafe_allow_html=True
            )

        log_audit(user["id"], user["username"], "admin", "run_demo", "donation", donation_id)
        st.success(f"✅ Demo workflow complete! Donation ID: {donation_id}")


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:

        # ── 1. Elegant Brand Header Card ──
        st.markdown("""
        <div style="padding: 0.85rem 0.75rem 0.75rem; text-align: center;
                    border-bottom: 1px solid rgba(178,106,245,0.22);
                    margin-bottom: 0.75rem; background: rgba(255,255,255,0.03);
                    border-radius: 14px;">
            <div style="display: inline-flex; align-items: center; justify-content: center;
                        width: 46px; height: 46px; border-radius: 12px;
                        background: linear-gradient(135deg, rgba(135,61,245,0.35), rgba(240,120,134,0.25));
                        border: 1px solid rgba(178,106,245,0.35); font-size: 1.5rem; margin-bottom: 6px;
                        box-shadow: 0 4px 12px rgba(135,61,245,0.2);">
                🌾
            </div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF;
                        line-height: 1.15; letter-spacing: -0.01em;">Anna Setu</div>
            <div style="font-size: 0.65rem; color: #B26AF5; font-weight: 700;
                        letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px;">
                Karnataka Food Rescue
            </div>
            <div style="display: inline-block; margin-top: 6px; padding: 2px 8px; border-radius: 999px;
                        background: rgba(22,166,154,0.15); border: 1px solid rgba(22,166,154,0.35);
                        font-size: 0.62rem; color: #16A69A; font-weight: 600;">
                🟢 Live Network · Bengaluru
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 2. User Profile or Guest Access Pill ──
        if st.session_state.get("authenticated"):
            user = st.session_state["user"]
            role = user["role"]
            role_colors = {"donor":"#16A69A","recipient":"#F07886","volunteer":"#B26AF5","admin":"#F07886"}
            role_icons  = {"donor":"🌾","recipient":"🏠","volunteer":"🚴","admin":"⚙️"}
            chip_col = role_colors.get(role, "#B26AF5")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'background:rgba(255,255,255,0.07);border-radius:10px;'
                f'padding:8px 12px;margin:0 4px 8px;border:1px solid rgba(255,255,255,0.1)">'
                f'<span style="font-size:1.2rem">{role_icons.get(role,"👤")}</span>'
                f'<div style="min-width:0">'
                f'<div style="font-size:.85rem;font-weight:700;color:#FFFFFF;'
                f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
                f'{user["full_name"]}</div>'
                f'<div style="font-size:.65rem;color:{chip_col};font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.05em">{role}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:10px;
                        background:rgba(255,255,255,0.05);border-radius:10px;
                        padding:7px 12px;margin:0 4px 8px;border:1px solid rgba(255,255,255,0.08)">
                <span style="font-size:1.15rem">🌐</span>
                <div>
                    <div style="font-size:.82rem;font-weight:700;color:#FFFFFF">Public Guest Access</div>
                    <div style="font-size:.62rem;color:#B26AF5">Emergency Discovery & Directory Active</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── 3. Navigation Header & Options ──
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;color:#A78BFA;'
            'text-transform:uppercase;letter-spacing:0.06em;margin:6px 6px 4px;">'
            '🧭 Navigation Menu</div>',
            unsafe_allow_html=True
        )

        common_options = [
            "🚨 Find Immediate Food Support",
            "🚚 Track Food Delivery & Driver",
            "🔍 Explore Organisations",
        ]

        if not st.session_state.get("authenticated"):
            nav_options = [
                "🏠 Home",
                "🚨 Find Immediate Food Support",
                "🚚 Track Food Delivery & Driver",
                "🔍 Explore Organisations",
                "🔑 Login",
            ]
        else:
            role = st.session_state["user"]["role"]
            if role == "admin":
                nav_options = [
                    "🏠 Command Center Dashboard",
                    "🚚 Fleet Command & Driver Tracking",
                    "🏛️ Organisations Directory",
                    "✅ Match Approvals",
                    "🚨 Safety Alerts",
                    "🚚 Delivery Monitor",
                    "🏠 Recipients",
                    "🚴 Volunteers",
                    "📈 Impact Report",
                    "🤖 Agent Logs",
                    "📝 Audit Logs",
                    "🎬 Run Demo",
                ] + common_options
            elif role == "donor":
                nav_options = [
                    "🏠 Donor Dashboard",
                    "🍱 Register Donation",
                    "📋 My Donations",
                    "🚚 Live Delivery Tracking",
                ] + common_options
            elif role == "recipient":
                nav_options = [
                    "🏠 Recipient Dashboard",
                    "🚚 Track Food Delivery & Driver",
                    "🎯 Available Matches",
                    "✅ Incoming Deliveries & Handover",
                    "🚨 Find Immediate Food Support",
                    "🔍 Explore Organisations",
                ]
            elif role == "volunteer":
                nav_options = [
                    "🏠 Volunteer Dashboard",
                    "📍 Delivery Destinations & Routes",
                    "🚚 Driver Trip Console & GPS",
                    "🔍 Explore Organisations",
                ]
            else:
                nav_options = ["🏠 Dashboard"] + common_options

            nav_options.append("🚪 Logout")

        override = st.session_state.pop("nav_override", None)
        default_idx = nav_options.index(override) if override in nav_options else 0
        nav = st.radio("nav", nav_options, index=default_idx, label_visibility="collapsed")

        # ── 4. 24/7 Crisis Helplines Quick Widget ──
        st.markdown("""
        <div style="margin: 14px 4px 6px; padding: 10px 12px;
                    background: rgba(240,120,134,0.08); border: 1px solid rgba(240,120,134,0.25);
                    border-radius: 12px;">
            <div style="font-size:0.72rem; font-weight:700; color:#F07886;
                        text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;
                        display:flex; align-items:center; gap:5px;">
                🚨 24/7 Crisis Helplines
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px;">
                <a href="tel:112" style="text-decoration:none; display:flex; align-items:center; gap:5px;
                           background:rgba(0,0,0,0.22); padding:5px 8px; border-radius:8px;
                           border:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:0.8rem;">📞</span>
                    <div>
                        <div style="font-size:0.75rem; font-weight:800; color:#FFFFFF;">112</div>
                        <div style="font-size:0.56rem; color:#EAE0F8;">Emergency</div>
                    </div>
                </a>
                <a href="tel:1098" style="text-decoration:none; display:flex; align-items:center; gap:5px;
                           background:rgba(0,0,0,0.22); padding:5px 8px; border-radius:8px;
                           border:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:0.8rem;">🧒</span>
                    <div>
                        <div style="font-size:0.75rem; font-weight:800; color:#FFFFFF;">1098</div>
                        <div style="font-size:0.56rem; color:#EAE0F8;">Childline</div>
                    </div>
                </a>
                <a href="tel:14567" style="text-decoration:none; display:flex; align-items:center; gap:5px;
                           background:rgba(0,0,0,0.22); padding:5px 8px; border-radius:8px;
                           border:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:0.8rem;">👵</span>
                    <div>
                        <div style="font-size:0.75rem; font-weight:800; color:#FFFFFF;">14567</div>
                        <div style="font-size:0.56rem; color:#EAE0F8;">Elderline</div>
                    </div>
                </a>
                <a href="tel:104" style="text-decoration:none; display:flex; align-items:center; gap:5px;
                           background:rgba(0,0,0,0.22); padding:5px 8px; border-radius:8px;
                           border:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:0.8rem;">🏥</span>
                    <div>
                        <div style="font-size:0.75rem; font-weight:800; color:#FFFFFF;">104</div>
                        <div style="font-size:0.56rem; color:#EAE0F8;">Health</div>
                    </div>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 5. Live Network Coverage Card ──
        st.markdown("""
        <div style="margin: 8px 4px 6px; padding: 10px 12px;
                    background: rgba(135,61,245,0.12); border: 1px solid rgba(178,106,245,0.22);
                    border-radius: 12px;">
            <div style="font-size:0.72rem; font-weight:700; color:#B26AF5;
                        text-transform:uppercase; letter-spacing:0.04em; margin-bottom:6px;">
                📊 Network Coverage
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="font-size:0.72rem; color:#D4B8F0;">Support Orgs:</span>
                <span style="font-size:0.72rem; font-weight:700; color:#FFFFFF;">42 Verified</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="font-size:0.72rem; color:#D4B8F0;">Localities:</span>
                <span style="font-size:0.72rem; font-weight:700; color:#FFFFFF;">15+ Covered</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.72rem; color:#D4B8F0;">Food Safety:</span>
                <span style="font-size:0.72rem; font-weight:700; color:#16A69A;">FSSAI Compliant</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 6. Multi-Agent AI Status & Refresh ──
        ai = st.session_state.get("ai_status", {})
        g_ok  = ai.get("gemini_available", False)
        gr_ok = ai.get("granite_available", False)
        g_model = (ai.get("gemini_model","") or "").replace("gemini-","").upper()
        g_col  = "#16A69A" if g_ok  else "#F07886"
        gr_col = "#16A69A" if gr_ok else "#F07886"
        st.markdown(
            f'<div style="margin:8px 4px 4px;padding:9px 12px;'
            f'background:rgba(0,0,0,0.25);border-radius:12px;'
            f'border:1px solid rgba(255,255,255,0.06);font-size:.7rem;line-height:1.7;color:#C8B8E8">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
            f'<span style="font-weight:700;color:#EAE0F8;">🤖 AI Agents Core</span>'
            f'<span style="font-size:0.62rem;color:#16A69A;font-weight:600;">4 Agents Active</span>'
            f'</div>'
            f'<span style="color:{gr_col}">●</span> '
            f'{"Granite 4.0: Online" if gr_ok else "Granite Offline"}&nbsp;&nbsp;'
            f'<span style="color:{g_col}">●</span> '
            f'{"Gemini: " + g_model if g_ok else "Gemini Standby"}'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("↺ Refresh AI Status", use_container_width=True):
            refresh_ai_status()
            st.rerun()

        # ── 7. Clean Platform Footer ──
        st.markdown("""
        <div style="text-align:center; padding: 10px 4px 6px; font-size:0.62rem;
                    color:rgba(234,224,248,0.5); line-height:1.4;">
            Anna Setu Karnataka · v2.0<br>
            Autonomous Agentic Food Rescue
        </div>
        """, unsafe_allow_html=True)

        return nav


# ─────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────

def main():
    nav = render_sidebar()

    if nav == "🏠 Home" or not nav:
        page_home()
    elif nav == "🚨 Find Immediate Food Support":
        page_find_immediate_support()
    elif nav in ("🚚 Track Food Delivery & Driver", "🚚 Track Live Delivery", "🚚 Track Delivery & Driver", "🚚 Live Delivery Tracking"):
        page_track_live_delivery()
    elif nav in ("📍 Delivery Destinations & Routes", "📍 Delivery Locations", "📍 Assigned Deliveries"):
        volunteer_delivery_destinations()
    elif nav in ("🔍 Explore Organisations", "🔍 Explore Food Support Organisations"):
        page_explore_organisations()
    elif nav in ("🤝 Driver & Fleet Registration", "🤝 Join as Volunteer / Partner", "🤝 Volunteer & Partner Onboarding"):
        page_login()
    elif nav == "🔑 Login":
        page_login()
    elif nav == "🚪 Logout":
        page_logout()
    elif not st.session_state.get("authenticated"):
        page_home()
    else:
        role = st.session_state["user"]["role"]
        if nav in ("🏠 Dashboard", "🏠 Command Center Dashboard", "🏠 Donor Dashboard", "🏠 Recipient Dashboard", "🏠 Volunteer Dashboard", "── Admin ──"):
            if role == "admin":
                admin_overview()
            elif role == "donor":
                donor_dashboard()
            elif role == "recipient":
                recipient_dashboard()
            elif role == "volunteer":
                volunteer_dashboard()
            else:
                page_home()
        elif nav in ("🚚 Fleet Command & Driver Tracking", "🚚 Logistics & Fleet Dispatch", "🚚 Logistics Dispatch"):
            admin_logistics_dispatch()
        elif nav in ("🏛️ Organisations Directory", "🏛️ Support Organisations Directory"):
            admin_support_organisations_management()
        elif nav == "🍱 Register Donation":
            donor_register_donation()
        elif nav == "📋 My Donations":
            donor_my_donations()
        elif nav in ("🚚 Live Delivery Tracking", "🚚 Delivery Tracking"):
            donor_tracking()
        elif nav == "🎯 Available Matches":
            recipient_available_matches()
        elif nav in ("✅ Incoming Deliveries & Handover", "✅ Acknowledge Delivery"):
            recipient_acknowledge_delivery()
        elif nav in ("🚚 Driver Trip Console & GPS", "📦 My Assignments"):
            volunteer_assignments()
        elif nav == "✅ Match Approvals":
            admin_match_approvals()
        elif nav == "🚨 Safety Alerts":
            admin_food_safety_alerts()
        elif nav == "🚚 Delivery Monitor":
            admin_delivery_monitoring()
        elif nav == "🏠 Recipients":
            admin_recipients()
        elif nav == "🚴 Volunteers":
            admin_volunteers()
        elif nav == "📈 Impact Report":
            admin_impact_report()
        elif nav == "🤖 Agent Logs":
            admin_agent_logs()
        elif nav == "📝 Audit Logs":
            admin_audit_logs()
        elif nav == "🎬 Run Demo":
            admin_run_demo()
        elif nav == "── Admin ──":
            admin_overview()
        else:
            page_home()



if __name__ == "__main__":
    main()
