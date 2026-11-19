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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-start:   #F8E9FC;
    --bg-end:     #FCECF4;
    --primary:    #24112F;
    --purple:     #873DF5;
    --purple-lt:  #B26AF5;
    --coral:      #F07886;
    --teal:       #16A69A;
    --card-bg:    rgba(255,255,255,0.75);
    --border:     rgba(135,61,245,0.15);
    --muted:      #57606a;
    --radius:     16px;
    --shadow:     0 2px 16px rgba(135,61,245,0.08);
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    color: var(--primary);
}

.main .block-container {
    background: linear-gradient(135deg, var(--bg-start), var(--bg-end));
    padding: 1.5rem 2rem 3rem;
    max-width: 1280px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1A0929 0%, #2D1050 100%);
    color: white;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label { color: #d4b8f0 !important; }

/* Cards */
.as-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.as-card-sm {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: var(--shadow);
}

/* KPI metric cards */
.kpi-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.kpi { flex: 1; min-width: 150px; background: var(--card-bg);
       border-radius: 14px; padding: 1rem 1.25rem;
       border-left: 4px solid var(--purple); box-shadow: var(--shadow); }
.kpi .kpi-val { font-size: 2rem; font-weight: 800; color: var(--purple); }
.kpi .kpi-lbl { font-size: 0.78rem; color: var(--muted); margin-top: 2px; font-weight: 500; }
.kpi-teal  { border-left-color: var(--teal) !important; }
.kpi-teal .kpi-val { color: var(--teal) !important; }
.kpi-coral { border-left-color: var(--coral) !important; }
.kpi-coral .kpi-val { color: var(--coral) !important; }

/* Badges */
.badge { display: inline-block; padding: 2px 10px; border-radius: 999px;
         font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-yellow { background: #fef9c3; color: #854d0e; }
.badge-purple { background: #ede9fe; color: #5b21b6; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-teal   { background: #ccfbf1; color: #0f766e; }
.badge-gray   { background: #f3f4f6; color: #374151; }

/* Hero */
.hero { text-align: center; padding: 3rem 1rem 2rem; }
.hero h1 { font-size: 3.2rem; font-weight: 800; color: var(--primary);
           line-height: 1.15; margin-bottom: 1rem; }
.hero h1 span { color: var(--purple); }
.hero p { font-size: 1.15rem; color: var(--muted); max-width: 600px; margin: 0 auto 2rem; }

/* Section headers */
.section-title { font-size: 1.3rem; font-weight: 700; color: var(--primary);
                 margin-bottom: 1rem; padding-bottom: .4rem;
                 border-bottom: 2px solid var(--border); }

/* Status alert */
.alert-safe   { background: #d1fae5; border-radius: 10px; padding: .75rem 1rem; color: #065f46; font-weight: 500; }
.alert-warn   { background: #fef9c3; border-radius: 10px; padding: .75rem 1rem; color: #854d0e; font-weight: 500; }
.alert-danger { background: #fee2e2; border-radius: 10px; padding: .75rem 1rem; color: #991b1b; font-weight: 500; }
.alert-info   { background: #dbeafe; border-radius: 10px; padding: .75rem 1rem; color: #1d4ed8; font-weight: 500; }

/* Table tweaks */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--purple), var(--purple-lt));
    color: white; border: none; border-radius: 10px;
    font-weight: 600; padding: .5rem 1.5rem;
    transition: opacity .2s;
}
.stButton > button:hover { opacity: 0.88; }

/* Agent activity strip */
.agent-strip { display: flex; gap: .5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.agent-pill { padding: 4px 14px; border-radius: 999px; font-size: .78rem; font-weight: 600; }
.a1 { background: #ede9fe; color: #5b21b6; }
.a2 { background: #ccfbf1; color: #0f766e; }
.a3 { background: #fef9c3; color: #854d0e; }
.a4 { background: #dbeafe; color: #1d4ed8; }
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
    # Always fetch fresh AI status (not cached) so model discovery result is current
    import agents as _ag_check
    if not _ag_check._ai_status.get("gemini_available") and not _ag_check._ai_status.get("granite_available"):
        # Agents haven't been initialised yet in this process — initialise now
        _ag_check.initialise_agents()
    st.session_state["ai_status"] = _ag_check.get_ai_status()
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
        "picked_up":         ("teal",   "Picked Up"),
        "in_transit":        ("blue",   "In Transit"),
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
    st.markdown("""
    <div class="hero">
        <h1>Rescue surplus food.<br><span>Deliver hope where it matters.</span></h1>
        <p>Connecting food donors, community organisations and volunteers through intelligent food redistribution — powered by AI agents across Karnataka.</p>
    </div>
    """, unsafe_allow_html=True)

    # TWO PROMINENT ACTION BUTTONS (usable without login)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚨 Find Immediate Food Support", use_container_width=True, key="home_btn_emergency"):
            st.session_state["nav_override"] = "🚨 Find Immediate Food Support"
            st.rerun()
    with btn_col2:
        if st.button("🔍 Explore Food Support Organisations", use_container_width=True, key="home_btn_explore"):
            st.session_state["nav_override"] = "🔍 Explore Food Support Organisations"
            st.rerun()

    st.write("")

    # Impact and System KPI strip
    import tools as t
    import database as db
    report = t.generate_impact_report()
    org_counts = t.get_organisation_counts()
    reg_donors = len(t.get_all_donor_orgs())
    all_donations = t.get_all_donations()
    active_donations = len([d for d in all_donations if d.get("status") in ("pending_screening", "screening_passed", "matched")])
    try:
        active_requests = db.execute_query("SELECT COUNT(*) AS c FROM recipient_requests WHERE status IN ('submitted', 'referred_to_org')")[0]['c']
        urgent_requests = db.execute_query("SELECT COUNT(*) AS c FROM recipient_requests WHERE urgency_level IN ('Urgent', 'Critical')")[0]['c']
    except Exception:
        active_requests = 0
        urgent_requests = 0
    recent_matches = len(t.get_matches_with_details())

    st.markdown(
        f'<div class="kpi-row">'
        + kpi_card(reg_donors, "Registered Donors")
        + kpi_card(active_donations, "Active Donations", "teal")
        + kpi_card(active_requests, "Active Recipient Requests")
        + kpi_card(f"{org_counts['real_count']} <small style='font-size:0.8rem'>({org_counts['demo_count']} demo)</small>", "Support Organisations", "coral")
        + kpi_card(urgent_requests, "Urgent Requests", "coral")
        + kpi_card(recent_matches, "Recent Matches", "teal")
        + '</div>',
        unsafe_allow_html=True
    )

    ai_status_bar()


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


    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="as-card">
        <div class="section-title">🌾 About Anna Setu Karnataka</div>
        <p>
        Anna Setu (<em>অন্ন সেতু</em> — Bridge of Food) is an intelligent food rescue coordination
        platform that connects surplus food from restaurants, hotels, wedding halls and canteens to
        shelters, orphanages, old-age homes and community kitchens across Karnataka.
        </p>
        <ul>
        <li>🤖 Four specialised AI agents coordinate the full donation lifecycle</li>
        <li>🛡️ Nine-category guardrails ensure food safety and data security</li>
        <li>🗺️ Volunteer and transport coordination for Bengaluru and beyond</li>
        <li>📊 Real-time impact tracking with confirmed delivery data</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="as-card">
        <div class="section-title">🔑 Demo Credentials</div>
        <table style="width:100%;font-size:.85rem;border-collapse:collapse">
        <tr style="border-bottom:1px solid #e5e7eb">
            <th style="text-align:left;padding:4px 8px;color:#873DF5">Username</th>
            <th style="text-align:left;padding:4px 8px;color:#873DF5">Password</th>
            <th style="text-align:left;padding:4px 8px;color:#873DF5">Role</th>
        </tr>
        <tr><td style="padding:4px 8px">donor_raj</td><td>Demo@1234</td><td>Donor</td></tr>
        <tr><td style="padding:4px 8px">donor_priya</td><td>Demo@1234</td><td>Donor</td></tr>
        <tr><td style="padding:4px 8px">recipient_hope</td><td>Demo@1234</td><td>Recipient</td></tr>
        <tr><td style="padding:4px 8px">volunteer_arjun</td><td>Demo@1234</td><td>Volunteer</td></tr>
        <tr><td style="padding:4px 8px">admin</td><td>Admin@1234</td><td>Admin</td></tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="as-card">
    <div class="section-title">🔄 Four Coordinated AI Agents</div>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem">
    <div class="as-card-sm">
        <strong style="color:#873DF5">Agent 1 — Donation & Safety</strong><br>
        <small>Registers donations, runs FSSAI-guided food safety screening, flags concerns for human review</small>
    </div>
    <div class="as-card-sm">
        <strong style="color:#16A69A">Agent 2 — Matching & Priority</strong><br>
        <small>Matches food to recipients by dietary needs, capacity and urgency with explainable scoring</small>
    </div>
    <div class="as-card-sm">
        <strong style="color:#F07886">Agent 3 — Collection & Logistics</strong><br>
        <small>Assigns volunteers and transport, coordinates pickup schedules, handles cancellations</small>
    </div>
    <div class="as-card-sm">
        <strong style="color:#3b82d4">Agent 4 — Delivery & Impact</strong><br>
        <small>Tracks deliveries, records acknowledgements, generates impact reports from confirmed records</small>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)


def page_login():
    st.markdown('<div class="section-title">🔑 Login to Anna Setu Karnataka</div>', unsafe_allow_html=True)
    from database import authenticate
    from guardrails import sanitise_text

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        u = sanitise_text(username, 80)
        if not u or not password:
            st.error("Username and password are required.")
            return
        from guardrails import check_prompt_injection
        safe, reason = check_prompt_injection(u)
        if not safe:
            st.error(f"Invalid input: {reason}")
            return
        user = authenticate(u, password)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            from database import log_audit
            log_audit(user["id"], user["username"], user["role"], "login")
            st.success(f"Welcome, {user['full_name']}! ({user['role'].title()})")
            st.rerun()
        else:
            st.error("Invalid username or password.")


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
    org_id = user.get("org_id")
    donations = t.get_donations_for_donor(org_id) if org_id else []

    total = len(donations)
    delivered = sum(1 for d in donations if d.get("status") == "delivered")
    pending   = sum(1 for d in donations if d.get("status") in ("pending_screening","matched","collected"))

    st.markdown('<div class="section-title">🏠 Donor Dashboard</div>', unsafe_allow_html=True)
    ai_status_bar()
    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(total,     "Total Donations")
        + kpi_card(delivered, "Delivered", "teal")
        + kpi_card(pending,   "In Progress", "coral")
        + '</div>', unsafe_allow_html=True
    )

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
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No donations yet. Register your first donation!")


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

    st.markdown('<div class="section-title">🚚 Pickup & Delivery Tracking</div>', unsafe_allow_html=True)

    if not donation_ids:
        st.info("No donations to track.")
        return

    deliveries = t.get_deliveries()
    my_deliveries = [dl for dl in deliveries if dl.get("donation_id") in donation_ids]

    if not my_deliveries:
        st.info("No delivery records found yet.")
        return

    for dl in my_deliveries:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{dl.get('food_name','—')}** → {dl.get('recipient_name','—')}")
                st.caption(f"📍 {dl.get('pickup_location','—')} → {dl.get('delivery_location','—')}")
            with col2:
                st.markdown(status_badge(dl.get("status","")), unsafe_allow_html=True)
                if dl.get("recipient_acknowledged"):
                    st.caption(f"✅ Acknowledged: {dl.get('actual_quantity','—')} meals")
            with col3:
                st.caption(f"Scheduled: {fmt_dt(dl.get('pickup_time_scheduled'))}")
            st.divider()


# ══════════════════════════════════════════════
# RECIPIENT PAGES
# ══════════════════════════════════════════════

def recipient_dashboard():
    user = require_role("recipient", "admin")
    import tools as t

    org_id = user.get("org_id")
    matches = []
    if org_id:
        all_matches = t.get_matches_with_details()
        matches = [m for m in all_matches if m.get("recipient_org_id") == org_id]

    pending_deliveries = [m for m in matches if m.get("status") not in ("delivered","failed","admin_rejected")]

    st.markdown('<div class="section-title">🏥 Recipient Dashboard</div>', unsafe_allow_html=True)
    ai_status_bar()
    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(len(matches),           "Total Matches")
        + kpi_card(len(pending_deliveries), "Active Deliveries", "teal")
        + kpi_card(sum(1 for m in matches if m.get("status")=="delivered"), "Received", "coral")
        + '</div>', unsafe_allow_html=True
    )


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
                     if dl.get("recipient_org_id") == org_id
                     and dl.get("status") in ("in_transit","picked_up","assigned","accepted")]

    st.markdown('<div class="section-title">✅ Acknowledge Delivery</div>', unsafe_allow_html=True)
    if not my_deliveries:
        st.info("No deliveries awaiting acknowledgement.")
        return

    for dl in my_deliveries:
        with st.expander(f"Delivery #{dl['id']} — {dl.get('food_name','—')} ({dl.get('status','')})", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Expected quantity:** {dl.get('allocated_quantity','—')} meals")
                st.write(f"**Recipient:** {dl.get('recipient_name','—')}")
                st.write(f"**Status:** {dl.get('status','—')}")
            with col2:
                actual = st.number_input(f"Actual quantity received", min_value=0,
                                         max_value=int(dl.get("allocated_quantity", 1000)),
                                         key=f"ack_qty_{dl['id']}")
                notes  = st.text_input("Notes", key=f"ack_notes_{dl['id']}")
                if st.button(f"Confirm Acknowledgement", key=f"ack_btn_{dl['id']}"):
                    t.record_acknowledgement(dl["id"], actual, notes)
                    from database import log_audit
                    log_audit(user["id"], user["username"], user["role"],
                              "acknowledge_delivery", "delivery", dl["id"],
                              f"actual_qty={actual}")
                    st.success("✅ Delivery acknowledged! Thank you.")
                    st.rerun()


# ══════════════════════════════════════════════
# VOLUNTEER PAGES
# ══════════════════════════════════════════════

def volunteer_dashboard():
    user = require_role("volunteer", "admin")
    import tools as t

    vol = t.get_volunteer_by_user_id(user["id"])
    assignments = t.get_assignments_for_volunteer(vol["id"]) if vol else []

    active = [a for a in assignments if a.get("status") not in ("delivered","failed","cancelled")]

    st.markdown('<div class="section-title">🚴 Volunteer Dashboard</div>', unsafe_allow_html=True)
    ai_status_bar()

    if vol:
        avail_color = "green" if vol.get("is_available") else "red"
        st.markdown(
            f'<div class="as-card">'
            f'<strong>{vol["full_name"]}</strong> | '
            f'Vehicle: {vol.get("vehicle_type","—")} (capacity: {vol.get("vehicle_capacity_meals","—")} meals) | '
            f'<span class="badge badge-{avail_color}">{"Available" if vol.get("is_available") else "Unavailable"}</span>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown(
        '<div class="kpi-row">'
        + kpi_card(len(assignments), "Total Assignments")
        + kpi_card(len(active),      "Active Assignments", "teal")
        + kpi_card(sum(1 for a in assignments if a.get("status")=="delivered"), "Completed", "coral")
        + '</div>', unsafe_allow_html=True
    )


def volunteer_assignments():
    user = require_role("volunteer", "admin")
    import tools as t
    from guardrails import validate_delivery_status_transition

    vol = t.get_volunteer_by_user_id(user["id"])
    if not vol:
        st.warning("Your account is not linked to a volunteer profile. Contact admin.")
        return

    assignments = t.get_assignments_for_volunteer(vol["id"])
    st.markdown('<div class="section-title">📦 My Assignments</div>', unsafe_allow_html=True)

    if not assignments:
        st.info("No assignments yet.")
        return

    for a in assignments:
        status = a.get("status", "assigned")
        with st.expander(f"Assignment #{a['id']} — {a.get('recipient_name','—')} | {status}", expanded=(status not in ("delivered","failed"))):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Pickup:** {a.get('pickup_location','—')}")
                st.write(f"**Delivery:** {a.get('delivery_address','—')}")
                st.write(f"**Quantity:** {a.get('allocated_quantity','—')} meals")
                st.write(f"**Scheduled:** {fmt_dt(a.get('pickup_time_scheduled'))}")
            with col2:
                st.markdown(status_badge(status), unsafe_allow_html=True)
                if status == "assigned":
                    if st.button("Accept Assignment ✓", key=f"accept_{a['id']}"):
                        t.volunteer_accept_assignment(a["id"])
                        st.success("Assignment accepted!")
                        st.rerun()
                if status in ("accepted", "assigned"):
                    if st.button("Mark Picked Up 📦", key=f"pickup_{a['id']}"):
                        # Find delivery
                        from database import execute_query
                        rows = execute_query("SELECT id FROM as_deliveries WHERE assignment_id=:aid", {"aid": a["id"]})
                        if rows:
                            t.update_delivery_status(rows[0]["id"], "picked_up")
                            t.update_assignment_status(a["id"], "picked_up")
                            st.success("Pickup recorded!")
                            st.rerun()
                if status == "picked_up":
                    if st.button("Mark In Transit 🚚", key=f"transit_{a['id']}"):
                        from database import execute_query
                        rows = execute_query("SELECT id FROM as_deliveries WHERE assignment_id=:aid", {"aid": a["id"]})
                        if rows:
                            t.update_delivery_status(rows[0]["id"], "in_transit")
                            t.update_assignment_status(a["id"], "in_transit")
                            st.success("Status updated: in transit!")
                            st.rerun()


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

    st.markdown('<div class="section-title">📊 Admin Overview Dashboard</div>', unsafe_allow_html=True)
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
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 1.5rem">
            <div style="font-size:2.5rem">🌾</div>
            <div style="font-size:1.2rem;font-weight:800;color:white">Anna Setu</div>
            <div style="font-size:.75rem;color:#B26AF5;margin-top:2px">Karnataka Food Rescue</div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.get("authenticated"):
            public_options = [
                "🏠 Home",
                "🚨 Find Immediate Food Support",
                "🔍 Explore Food Support Organisations",
                "🔑 Login",
            ]
            override = st.session_state.pop("nav_override", None)
            default_idx = public_options.index(override) if override in public_options else 0
            nav = st.radio("Navigation", public_options, index=default_idx, label_visibility="collapsed")
            return nav

        user = st.session_state["user"]
        role = user["role"]
        st.markdown(f'<div style="text-align:center;margin-bottom:1rem">'
                    f'<div style="font-weight:700">{user["full_name"]}</div>'
                    f'<div style="font-size:.75rem;color:#B26AF5">{role.title()}</div>'
                    f'</div>', unsafe_allow_html=True)

        # Public discovery entry points always accessible
        common_options = [
            "🚨 Find Immediate Food Support",
            "🔍 Explore Food Support Organisations",
        ]

        if role in ("donor", "admin"):
            nav_options = [
                "🏠 Dashboard", "🍱 Register Donation", "📋 My Donations",
                "🚚 Delivery Tracking"
            ] + common_options
        elif role == "recipient":
            nav_options = [
                "🏠 Dashboard", "🎯 Available Matches", "✅ Acknowledge Delivery"
            ] + common_options
        elif role == "volunteer":
            nav_options = [
                "🏠 Dashboard", "📦 My Assignments"
            ] + common_options
        else:
            nav_options = ["🏠 Dashboard"] + common_options

        if role == "admin":
            nav_options += [
                "── Admin ──",
                "🏛️ Support Organisations Directory",
                "✅ Match Approvals",
                "🚨 Safety Alerts",
                "🚚 Delivery Monitor",
                "🏠 Recipients",
                "🚴 Volunteers",
                "📈 Impact Report",
                "🤖 Agent Logs",
                "📝 Audit Logs",
                "🎬 Run Demo",
            ]

        nav_options.append("🚪 Logout")

        override = st.session_state.pop("nav_override", None)
        default_idx = nav_options.index(override) if override in nav_options else 0
        nav = st.radio("Navigation", nav_options, index=default_idx, label_visibility="collapsed")

        # AI status indicator at bottom of sidebar
        st.divider()
        ai = st.session_state.get("ai_status", {})
        g_ok = ai.get("gemini_available", False)
        gr_ok = ai.get("granite_available", False)
        g_model = ai.get("gemini_model", "—")
        st.markdown(
            f'<div style="font-size:.75rem;line-height:1.8">'
            f'<span style="color:{"#16A69A" if g_ok else "#F07886"}">{"●" if g_ok else "●"}</span> '
            f'Gemini: {"<b>" + g_model + "</b>" if g_ok else "<i>Offline</i>"}<br>'
            f'<span style="color:{"#16A69A" if gr_ok else "#F07886"}">●</span> '
            f'Granite: {"<b>Online</b>" if gr_ok else "<i>Offline</i>"}'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("🔄 Refresh AI Status", use_container_width=True):
            refresh_ai_status()
            st.rerun()

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
    elif nav == "🔍 Explore Food Support Organisations":
        page_explore_organisations()
    elif nav == "🔑 Login":
        page_login()
    elif nav == "🚪 Logout":
        page_logout()
    elif not st.session_state.get("authenticated"):
        page_home()
    else:
        role = st.session_state["user"]["role"]
        if nav == "🏠 Dashboard":
            if role in ("donor", "admin"):
                donor_dashboard()
            elif role == "recipient":
                recipient_dashboard()
            elif role == "volunteer":
                volunteer_dashboard()
        elif nav == "🏛️ Support Organisations Directory":
            admin_support_organisations_management()
        elif nav == "🍱 Register Donation":
            donor_register_donation()
        elif nav == "📋 My Donations":
            donor_my_donations()
        elif nav == "🚚 Delivery Tracking":
            donor_tracking()
        elif nav == "🎯 Available Matches":
            recipient_available_matches()
        elif nav == "✅ Acknowledge Delivery":
            recipient_acknowledge_delivery()
        elif nav == "📦 My Assignments":
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
