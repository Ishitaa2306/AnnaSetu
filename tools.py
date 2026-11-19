"""
Anna Setu Karnataka — Tool Implementations
Agent-callable functions with strict parameterised queries.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from database import engine, insert_row, execute_query, log_agent_action, log_audit

log = logging.getLogger("annasetu.tools")

# ─────────────────────────────────────────────
# AGENT 1 TOOLS — Donation & Food Safety
# ─────────────────────────────────────────────

def register_donation(donor_org_id: int, donor_user_id: int, food_name: str,
                      food_category: str, dietary_type: str, quantity: int, unit: str,
                      preparation_time: datetime | None, pickup_deadline: datetime,
                      location: str, city: str, packaging: str, storage_condition: str,
                      allergen_info: str = "", notes: str = "", is_demo: bool = False) -> dict:
    """Register a new donation. Returns {'donation_id': int, 'status': str}."""
    now = datetime.now(timezone.utc)
    data = {
        "donor_org_id": donor_org_id,
        "donor_user_id": donor_user_id,
        "food_name": food_name,
        "food_category": food_category,
        "dietary_type": dietary_type,
        "quantity": quantity,
        "unit": unit,
        "preparation_time": preparation_time,
        "pickup_deadline": pickup_deadline,
        "location": location,
        "city": city,
        "packaging": packaging,
        "storage_condition": storage_condition,
        "allergen_info": allergen_info,
        "notes": notes,
        "status": "pending_screening",
        "is_demo": is_demo,
        "created_at": now,
        "updated_at": now,
    }
    did = insert_row("as_donations", data)
    log_agent_action("agent1", "register_donation", "donation", did,
                     input_s=f"food={food_name}, qty={quantity}", output_s=f"donation_id={did}")
    return {"donation_id": did, "status": "pending_screening"}


def get_donation(donation_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM as_donations WHERE id = :id", {"id": donation_id})
    return rows[0] if rows else None


def get_donor_org(donor_org_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM as_donor_orgs WHERE id = :id", {"id": donor_org_id})
    return rows[0] if rows else None


def update_donation_status(donation_id: int, status: str, agent: str = "agent1") -> bool:
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE as_donations SET status=:s, updated_at=:u WHERE id=:id"
        ), {"s": status, "u": datetime.now(timezone.utc), "id": donation_id})
        conn.commit()
    log_agent_action(agent, f"update_status→{status}", "donation", donation_id)
    return True


def save_food_safety_record(donation_id: int, screening_result: str, safety_score: float,
                            issues_found: str, recommendations: str, model_used: str) -> int:
    """Save food safety screening result. Returns record id."""
    return insert_row("as_food_safety", {
        "donation_id": donation_id,
        "screening_result": screening_result,
        "safety_score": safety_score,
        "issues_found": issues_found,
        "recommendations": recommendations,
        "screened_by": "agent1",
        "model_used": model_used,
        "human_reviewed": False,
        "created_at": datetime.now(timezone.utc),
    })


def request_human_review(entity_type: str, entity_id: int, reason: str, requested_by: str = "agent1") -> int:
    return insert_row("as_human_approvals", {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "reason": reason[:300],
        "status": "pending",
        "requested_by": requested_by,
        "created_at": datetime.now(timezone.utc),
    })


def get_food_safety_record(donation_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM as_food_safety WHERE donation_id=:id ORDER BY id DESC LIMIT 1", {"id": donation_id})
    return rows[0] if rows else None


# ─────────────────────────────────────────────
# AGENT 2 TOOLS — Recipient Matching & Priority
# ─────────────────────────────────────────────

def get_eligible_donations() -> list[dict]:
    return execute_query(
        "SELECT * FROM as_donations WHERE status='screening_passed' ORDER BY pickup_deadline ASC"
    )


def get_recipient_orgs(city: str | None = None) -> list[dict]:
    if city:
        return execute_query("SELECT * FROM as_recipient_orgs WHERE is_active=TRUE AND city=:c", {"c": city})
    return execute_query("SELECT * FROM as_recipient_orgs WHERE is_active=TRUE ORDER BY name")


def get_recipient_requirements(org_id: int | None = None) -> list[dict]:
    if org_id:
        return execute_query("SELECT * FROM as_recipient_requirements WHERE org_id=:id", {"id": org_id})
    return execute_query("SELECT * FROM as_recipient_requirements")


def get_already_allocated(donation_id: int) -> int:
    """Return quantity already matched for a donation."""
    rows = execute_query(
        "SELECT COALESCE(SUM(allocated_quantity),0) AS total FROM as_donation_matches "
        "WHERE donation_id=:id AND status NOT IN ('admin_rejected','failed')",
        {"id": donation_id}
    )
    return int(rows[0]["total"]) if rows else 0


def save_matches(matches: list[dict]) -> list[int]:
    """Save proposed matches. Returns list of inserted IDs."""
    ids = []
    now = datetime.now(timezone.utc)
    for m in matches:
        try:
            mid = insert_row("as_donation_matches", {
                "donation_id": m["donation_id"],
                "recipient_org_id": m["recipient_org_id"],
                "allocated_quantity": m["allocated_quantity"],
                "match_score": m.get("match_score", 0),
                "match_reason": m.get("match_reason", "")[:1000],
                "status": "proposed",
                "is_demo": m.get("is_demo", False),
                "created_at": now,
                "updated_at": now,
            })
            ids.append(mid)
        except Exception as e:
            log.warning(f"Save match failed: {e}")
    return ids


def request_admin_approval(match_ids: list[int], reason: str) -> list[int]:
    approval_ids = []
    for mid in match_ids:
        aid = request_human_review("match", mid, reason, "agent2")
        approval_ids.append(aid)
    return approval_ids


def get_match(match_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM as_donation_matches WHERE id=:id", {"id": match_id})
    return rows[0] if rows else None


def get_matches_for_donation(donation_id: int) -> list[dict]:
    return execute_query("SELECT * FROM as_donation_matches WHERE donation_id=:id ORDER BY match_score DESC", {"id": donation_id})


def approve_match(match_id: int, approver_user_id: int) -> bool:
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE as_donation_matches SET status='admin_approved', approved_by_user_id=:uid, "
            "approved_at=:at, updated_at=:u WHERE id=:id"
        ), {"uid": approver_user_id, "at": datetime.now(timezone.utc),
            "u": datetime.now(timezone.utc), "id": match_id})
        # Also update associated human approval
        conn.execute(text(
            "UPDATE as_human_approvals SET status='approved', reviewed_by_user_id=:uid, "
            "resolved_at=:at WHERE entity_type='match' AND entity_id=:mid AND status='pending'"
        ), {"uid": approver_user_id, "at": datetime.now(timezone.utc), "mid": match_id})
        conn.commit()
    return True


def reject_match(match_id: int, approver_user_id: int, notes: str = "") -> bool:
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE as_donation_matches SET status='admin_rejected', approved_by_user_id=:uid, "
            "approved_at=:at, updated_at=:u WHERE id=:id"
        ), {"uid": approver_user_id, "at": datetime.now(timezone.utc),
            "u": datetime.now(timezone.utc), "id": match_id})
        conn.execute(text(
            "UPDATE as_human_approvals SET status='rejected', reviewed_by_user_id=:uid, "
            "review_notes=:notes, resolved_at=:at "
            "WHERE entity_type='match' AND entity_id=:mid AND status='pending'"
        ), {"uid": approver_user_id, "notes": notes, "at": datetime.now(timezone.utc), "mid": match_id})
        conn.commit()
    return True


# ─────────────────────────────────────────────
# AGENT 3 TOOLS — Collection & Logistics
# ─────────────────────────────────────────────

def get_approved_matches() -> list[dict]:
    return execute_query(
        "SELECT dm.*, d.food_name, d.quantity, d.location, d.city, d.pickup_deadline, "
        "ro.name AS recipient_name, ro.address AS recipient_address "
        "FROM as_donation_matches dm "
        "JOIN as_donations d ON dm.donation_id=d.id "
        "JOIN as_recipient_orgs ro ON dm.recipient_org_id=ro.id "
        "WHERE dm.status='admin_approved'"
    )


def get_available_volunteers(city: str | None = None) -> list[dict]:
    if city:
        return execute_query(
            "SELECT * FROM as_volunteers WHERE is_available=TRUE AND is_active=TRUE AND city=:c",
            {"c": city}
        )
    return execute_query("SELECT * FROM as_volunteers WHERE is_available=TRUE AND is_active=TRUE")


def get_transport_providers(city: str | None = None) -> list[dict]:
    if city:
        return execute_query("SELECT * FROM as_transport_providers WHERE is_available=TRUE AND city=:c", {"c": city})
    return execute_query("SELECT * FROM as_transport_providers WHERE is_available=TRUE")


def create_assignment(match_id: int, volunteer_id: int | None, transport_provider_id: int | None,
                      pickup_location: str, delivery_location: str,
                      pickup_time_scheduled: datetime, notes: str = "", is_demo: bool = False) -> int:
    now = datetime.now(timezone.utc)
    aid = insert_row("as_collection_assignments", {
        "match_id": match_id,
        "volunteer_id": volunteer_id,
        "transport_provider_id": transport_provider_id,
        "pickup_time_scheduled": pickup_time_scheduled,
        "pickup_location": pickup_location,
        "delivery_location": delivery_location,
        "status": "assigned",
        "volunteer_accepted": False,
        "notes": notes,
        "is_demo": is_demo,
        "created_at": now,
        "updated_at": now,
    })
    # Also create delivery record
    insert_row("as_deliveries", {
        "assignment_id": aid,
        "match_id": match_id,
        "status": "assigned",
        "is_demo": is_demo,
        "created_at": now,
        "updated_at": now,
    })
    # Update match status
    with engine.connect() as conn:
        conn.execute(text("UPDATE as_donation_matches SET status='volunteer_assigned', updated_at=:u WHERE id=:id"),
                     {"u": now, "id": match_id})
        conn.commit()
    log_agent_action("agent3", "create_assignment", "assignment", aid,
                     output_s=f"match_id={match_id}, vol={volunteer_id}")
    return aid


def update_assignment_status(assignment_id: int, status: str, notes: str = "") -> bool:
    now = datetime.now(timezone.utc)
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE as_collection_assignments SET status=:s, updated_at=:u "
            + (", volunteer_accepted=TRUE" if status == "accepted" else "")
            + " WHERE id=:id"
        ), {"s": status, "u": now, "id": assignment_id})
        conn.commit()
    return True


def volunteer_accept_assignment(assignment_id: int) -> bool:
    return update_assignment_status(assignment_id, "accepted")


def notify_volunteer(volunteer_id: int, message: str) -> bool:
    # In production: SMS/push notification. Here: audit log.
    log.info(f"[NOTIFY] Volunteer {volunteer_id}: {message}")
    return True


def get_assignment(assignment_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM as_collection_assignments WHERE id=:id", {"id": assignment_id})
    return rows[0] if rows else None


def get_assignments_for_volunteer(volunteer_id: int) -> list[dict]:
    return execute_query(
        "SELECT ca.*, dm.donation_id, dm.allocated_quantity, dm.recipient_org_id, "
        "ro.name AS recipient_name, ro.address AS delivery_address "
        "FROM as_collection_assignments ca "
        "JOIN as_donation_matches dm ON ca.match_id=dm.id "
        "JOIN as_recipient_orgs ro ON dm.recipient_org_id=ro.id "
        "WHERE ca.volunteer_id=:vid ORDER BY ca.created_at DESC",
        {"vid": volunteer_id}
    )


# ─────────────────────────────────────────────
# AGENT 4 TOOLS — Delivery Tracking & Impact
# ─────────────────────────────────────────────

def get_deliveries(filters: dict | None = None) -> list[dict]:
    base = (
        "SELECT dl.*, ca.pickup_location, ca.delivery_location, ca.pickup_time_scheduled, "
        "ca.volunteer_id, dm.donation_id, dm.allocated_quantity, dm.recipient_org_id, "
        "ro.name AS recipient_name, d.food_name, d.dietary_type "
        "FROM as_deliveries dl "
        "JOIN as_collection_assignments ca ON dl.assignment_id=ca.id "
        "JOIN as_donation_matches dm ON dl.match_id=dm.id "
        "JOIN as_recipient_orgs ro ON dm.recipient_org_id=ro.id "
        "JOIN as_donations d ON dm.donation_id=d.id "
    )
    if filters and filters.get("status"):
        return execute_query(base + "WHERE dl.status=:s ORDER BY dl.created_at DESC", {"s": filters["status"]})
    return execute_query(base + "ORDER BY dl.created_at DESC")


def get_assignments(filters: dict | None = None) -> list[dict]:
    base = "SELECT * FROM as_collection_assignments "
    if filters and filters.get("status"):
        return execute_query(base + "WHERE status=:s ORDER BY created_at DESC", {"s": filters["status"]})
    return execute_query(base + "ORDER BY created_at DESC")


def update_delivery_status(delivery_id: int, status: str, actual_quantity: int | None = None,
                           failure_reason: str = "") -> bool:
    now = datetime.now(timezone.utc)
    updates = {"s": status, "u": now, "id": delivery_id}
    extra_sql = ""
    if status == "picked_up":
        extra_sql = ", pickup_at=:pu"
        updates["pu"] = now
        # Also update assignment
        with engine.connect() as conn:
            conn.execute(text(
                "UPDATE as_collection_assignments SET status='picked_up', updated_at=:u "
                "WHERE id=(SELECT assignment_id FROM as_deliveries WHERE id=:did)"
            ), {"u": now, "did": delivery_id})
            conn.commit()
    if status in ("delivered", "failed"):
        extra_sql += ", delivered_at=:da"
        updates["da"] = now
        if actual_quantity is not None:
            extra_sql += ", actual_quantity=:aq"
            updates["aq"] = actual_quantity
        if failure_reason:
            extra_sql += ", failure_reason=:fr"
            updates["fr"] = failure_reason[:300]
    with engine.connect() as conn:
        conn.execute(text(
            f"UPDATE as_deliveries SET status=:s{extra_sql}, updated_at=:u WHERE id=:id"
        ), updates)
        conn.commit()
    log_agent_action("agent4", f"delivery→{status}", "delivery", delivery_id)
    return True


def record_acknowledgement(delivery_id: int, actual_quantity: int, notes: str = "") -> bool:
    now = datetime.now(timezone.utc)
    with engine.connect() as conn:
        conn.execute(text(
            "UPDATE as_deliveries SET recipient_acknowledged=TRUE, acknowledgement_at=:at, "
            "acknowledgement_notes=:notes, actual_quantity=:aq, status='delivered', updated_at=:u "
            "WHERE id=:id"
        ), {"at": now, "notes": notes[:300], "aq": actual_quantity, "u": now, "id": delivery_id})
        # Update match status
        conn.execute(text(
            "UPDATE as_donation_matches SET status='delivered', updated_at=:u "
            "WHERE id=(SELECT match_id FROM as_deliveries WHERE id=:did)"
        ), {"u": now, "did": delivery_id})
        conn.commit()
    log_agent_action("agent4", "record_acknowledgement", "delivery", delivery_id,
                     output_s=f"qty={actual_quantity}")
    return True


def alert_admin(message: str, entity_type: str = "", entity_id: int | None = None):
    log.warning(f"[ADMIN ALERT] {entity_type}#{entity_id}: {message}")
    request_human_review(entity_type or "delivery", entity_id or 0, message, "agent4")


def generate_impact_report() -> dict:
    """Generate impact stats from confirmed DB records only."""
    rows = execute_query("""
        SELECT
            COUNT(DISTINCT d.id)                                        AS total_donations,
            COUNT(DISTINCT CASE WHEN d.status='delivered' THEN d.id END) AS delivered_donations,
            COALESCE(SUM(CASE WHEN dl.recipient_acknowledged THEN dl.actual_quantity ELSE 0 END), 0) AS confirmed_meals,
            COUNT(DISTINCT CASE WHEN dl.recipient_acknowledged THEN dm.recipient_org_id END)       AS orgs_served,
            COUNT(DISTINCT CASE WHEN ca.volunteer_id IS NOT NULL THEN ca.volunteer_id END)         AS volunteers_engaged
        FROM as_donations d
        LEFT JOIN as_donation_matches dm ON dm.donation_id=d.id
        LEFT JOIN as_collection_assignments ca ON ca.match_id=dm.id
        LEFT JOIN as_deliveries dl ON dl.assignment_id=ca.id
    """)
    stats = dict(rows[0]) if rows else {}
    # Delivery status breakdown
    status_rows = execute_query(
        "SELECT status, COUNT(*) AS cnt FROM as_deliveries GROUP BY status"
    )
    stats["delivery_breakdown"] = {r["status"]: r["cnt"] for r in status_rows}
    stats["source"] = "database"
    stats["simulated"] = False
    stats["generated_at"] = datetime.now(timezone.utc).isoformat()
    return stats


# ─────────────────────────────────────────────
# SHARED QUERY HELPERS
# ─────────────────────────────────────────────

def get_human_approvals(status: str | None = None) -> list[dict]:
    if status:
        return execute_query(
            "SELECT * FROM as_human_approvals WHERE status=:s ORDER BY created_at DESC",
            {"s": status}
        )
    return execute_query("SELECT * FROM as_human_approvals ORDER BY created_at DESC")


def get_agent_logs(limit: int = 100) -> list[dict]:
    return execute_query(
        "SELECT * FROM as_agent_logs ORDER BY created_at DESC LIMIT :lim", {"lim": limit}
    )


def get_audit_logs(limit: int = 100) -> list[dict]:
    return execute_query(
        "SELECT * FROM as_audit_logs ORDER BY created_at DESC LIMIT :lim", {"lim": limit}
    )


def get_donations_for_donor(donor_org_id: int) -> list[dict]:
    return execute_query(
        "SELECT * FROM as_donations WHERE donor_org_id=:id ORDER BY created_at DESC",
        {"id": donor_org_id}
    )


def get_all_donations(limit: int = 200) -> list[dict]:
    return execute_query(
        "SELECT d.*, dorg.name AS donor_name FROM as_donations d "
        "JOIN as_donor_orgs dorg ON d.donor_org_id=dorg.id ORDER BY d.created_at DESC LIMIT :lim",
        {"lim": limit}
    )


def get_volunteer_by_user_id(user_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM as_volunteers WHERE user_id=:uid", {"uid": user_id})
    return rows[0] if rows else None


def get_all_volunteers() -> list[dict]:
    return execute_query("SELECT * FROM as_volunteers ORDER BY full_name")


def get_all_recipient_orgs() -> list[dict]:
    return execute_query("SELECT * FROM as_recipient_orgs WHERE is_active=TRUE ORDER BY name")


def get_all_donor_orgs() -> list[dict]:
    return execute_query("SELECT * FROM as_donor_orgs WHERE is_active=TRUE ORDER BY name")


def get_matches_with_details() -> list[dict]:
    return execute_query("""
        SELECT dm.*, d.food_name, d.quantity AS total_quantity, d.dietary_type,
               dorg.name AS donor_name, ro.name AS recipient_name,
               ro.city AS recipient_city
        FROM as_donation_matches dm
        JOIN as_donations d ON dm.donation_id=d.id
        JOIN as_donor_orgs dorg ON d.donor_org_id=dorg.id
        JOIN as_recipient_orgs ro ON dm.recipient_org_id=ro.id
        ORDER BY dm.created_at DESC
    """)


# ─────────────────────────────────────────────
# PHASE 2: EMERGENCY FOOD SUPPORT DISCOVERY TOOLS
# ─────────────────────────────────────────────

import urllib.parse
import math


def build_directions_url(name: str, address: str = "", city: str = "Bengaluru") -> str:
    """Build URL-encoded Google Maps search link."""
    parts = [p for p in [name, address, city] if p]
    query = " ".join(parts)
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"


def get_general_support_contacts() -> list[dict]:
    """Retrieve verified national/state emergency and crisis helplines."""
    return execute_query("""
        SELECT * FROM general_support_contacts
        WHERE is_active = TRUE
        ORDER BY id ASC
    """)


def get_organisation_counts() -> dict:
    """Return counts of registered support organisations for KPIs."""
    rows = execute_query("""
        SELECT
            COUNT(*) AS total,
            COUNT(CASE WHEN is_synthetic = FALSE THEN 1 END) AS real_count,
            COUNT(CASE WHEN is_synthetic = TRUE THEN 1 END) AS demo_count,
            COUNT(CASE WHEN can_distribute_food = TRUE AND is_synthetic = FALSE THEN 1 END) AS providers,
            COUNT(CASE WHEN is_beneficiary_institution = TRUE AND is_synthetic = FALSE THEN 1 END) AS beneficiaries
        FROM support_organisations
        WHERE is_active = TRUE
    """)
    return rows[0] if rows else {
        "total": 0, "real_count": 0, "demo_count": 0, "providers": 0, "beneficiaries": 0
    }


def get_support_organisations_directory(
    locality: str | None = None,
    org_type: str | None = None,
    food_category: str | None = None,
    availability_status: str | None = None,
    search_query: str | None = None,
    include_demo: bool = False,
    is_beneficiary_only: bool | None = None,
    limit: int = 200,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """
    Search and filter organisations directory without requiring an active request.
    Returns (records, total_count). Uses safe parameterised queries.
    """
    conditions = ["is_active = TRUE"]
    params: dict[str, Any] = {"limit": limit, "offset": offset}

    if not include_demo:
        conditions.append("is_synthetic = FALSE")

    if locality and locality.strip() and locality != "All":
        conditions.append("LOWER(locality) = LOWER(:locality)")
        params["locality"] = locality.strip()

    if org_type and org_type.strip() and org_type != "All":
        conditions.append("organisation_type = :org_type")
        params["org_type"] = org_type.strip()

    if availability_status and availability_status.strip() and availability_status != "All":
        conditions.append("availability_status = :avail")
        params["avail"] = availability_status.strip()

    if is_beneficiary_only is not None:
        if is_beneficiary_only:
            conditions.append("is_beneficiary_institution = TRUE")
        else:
            conditions.append("can_distribute_food = TRUE")

    if food_category and food_category.strip() and food_category != "All":
        conditions.append("(food_categories_supported ILIKE :cat OR food_services ILIKE :cat)")
        params["cat"] = f"%{food_category.strip()}%"

    if search_query and search_query.strip():
        conditions.append(
            "(organisation_name ILIKE :q OR address ILIKE :q OR locality ILIKE :q OR service_description ILIKE :q)"
        )
        params["q"] = f"%{search_query.strip()}%"

    where_clause = " AND ".join(conditions)
    count_sql = f"SELECT COUNT(*) AS c FROM support_organisations WHERE {where_clause}"
    count_res = execute_query(count_sql, params)
    total_count = count_res[0]["c"] if count_res else 0

    query_sql = f"""
        SELECT * FROM support_organisations
        WHERE {where_clause}
        ORDER BY
            is_synthetic ASC,
            CASE WHEN can_distribute_food = TRUE THEN 0 ELSE 1 END,
            organisation_name ASC
        LIMIT :limit OFFSET :offset
    """
    records = execute_query(query_sql, params)
    return records, total_count


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in km between two coordinate pairs."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def discover_support_organisations(
    locality: str,
    food_category: str = "cooked_meals",
    urgency_level: str = "Normal",
    city: str = "Bengaluru",
    recipient_lat: float | None = None,
    recipient_lon: float | None = None,
    include_demo: bool = False,
    limit: int = 10,
) -> list[dict]:
    """
    Transparent, deterministic organisation discovery for emergency food referrals.
    Hard filters:
      - is_active = TRUE
      - can_distribute_food = TRUE (must be an active food provider/distributor)
      - availability_status != 'temporarily_unavailable'
      - is_synthetic = FALSE (unless include_demo = TRUE)
      - city match
    Then scores (Section 7):
      - Locality match: 40 (exact 40; partial/region 25; city-only 10)
      - Service relevance: 30 (stated category 30; unknown/general 10)
      - Availability status: 15 (confirmed 15; contact_to_confirm 8; unknown 5)
      - Contact info present: 10 (phone/email/website; phone prioritized when Critical)
      - Source reliability: 5 (official program 5; directory 3)
    """
    from guardrails import validate_organisation_filter_args
    ok, err = validate_organisation_filter_args({
        "locality": locality,
        "food_category": food_category,
        "urgency_level": urgency_level,
        "city": city
    })
    if not ok:
        log.warning(f"Organisation filter argument guardrail tripped: {err}")
        return []

    conditions = [
        "is_active = TRUE",
        "can_distribute_food = TRUE",
        "availability_status != 'temporarily_unavailable'",
        "LOWER(city) = LOWER(:city)",
    ]
    params: dict[str, Any] = {"city": city.strip()}

    if not include_demo:
        conditions.append("is_synthetic = FALSE")

    sql = f"""
        SELECT * FROM support_organisations
        WHERE {' AND '.join(conditions)}
    """
    candidates = execute_query(sql, params)

    locality_clean = locality.strip().lower()
    cat_clean = food_category.strip().lower()

    scored_orgs = []
    for org in candidates:
        score = 0.0
        reasons = []

        # 1. Locality match (40)
        org_loc = (org.get("locality") or "").strip().lower()
        org_addr = (org.get("address") or "").strip().lower()
        if locality_clean and (locality_clean == org_loc or locality_clean in org_addr):
            score += 40.0
            reasons.append(f"Same locality ({org.get('locality')})")
        elif org_loc and org_loc in ("bengaluru urban", "bangalore urban"):
            score += 25.0
            reasons.append("City-wide redistribution network")
        else:
            score += 10.0
            reasons.append(f"Bengaluru city provider ({org.get('locality') or 'Bengaluru'})")

        # 2. Food category / service match (30)
        supported_cats = (org.get("food_categories_supported") or "").lower()
        services = (org.get("food_services") or "").lower()
        if cat_clean in supported_cats or cat_clean in services:
            score += 30.0
            reasons.append(f"Lists matching food category ({food_category})")
        elif not supported_cats or "not stated" in supported_cats:
            score += 10.0
            reasons.append("Food categories not explicitly stated in directory")
        else:
            score += 5.0
            reasons.append("Food services available")

        # 3. Availability status (15)
        avail = org.get("availability_status", "unknown")
        if avail == "confirmed_available":
            score += 15.0
            reasons.append("Availability confirmed by source")
        elif avail == "contact_to_confirm":
            score += 8.0
            reasons.append("Contact organisation to confirm current capacity")
        else:
            score += 5.0
            reasons.append("Availability not confirmed — contact organisation")

        # 4. Contact info present (10)
        has_phone = bool(org.get("contact_phone"))
        has_email = bool(org.get("contact_email"))
        has_web = bool(org.get("website_url"))
        contact_score = 0.0
        if has_phone:
            contact_score += 6.0
            reasons.append("Direct phone available")
        if has_email:
            contact_score += 2.0
            if not has_phone:
                reasons.append("Email available")
        if has_web:
            contact_score += 2.0
        score += contact_score

        # 5. Source reliability (5)
        source = (org.get("source_name") or "").lower()
        if "official" in source or "fssai" in source or "bangalore food bank" in source:
            score += 5.0
        else:
            score += 3.0

        # Distance calculation: only if BOTH have real coordinates
        distance_str = "Distance not available"
        if (
            recipient_lat is not None
            and recipient_lon is not None
            and org.get("latitude") is not None
            and org.get("longitude") is not None
        ):
            try:
                dist_km = calculate_haversine_distance(
                    float(recipient_lat), float(recipient_lon),
                    float(org["latitude"]), float(org["longitude"])
                )
                distance_str = f"{round(dist_km, 1)} km"
            except Exception:
                distance_str = "Distance not available"

        # Action links
        directions_url = build_directions_url(
            org.get("organisation_name", ""),
            org.get("address", "") or org.get("locality", ""),
            org.get("city", "Bengaluru")
        )
        phone = org.get("contact_phone")
        tel_link = f"tel:{phone.replace(' ', '').replace('-', '')}" if phone else ""
        email = org.get("contact_email")
        mailto_link = f"mailto:{email}" if email else ""

        scored_orgs.append({
            **org,
            "match_score": round(score, 1),
            "match_reason": " | ".join(reasons),
            "distance_str": distance_str,
            "directions_url": directions_url,
            "tel_link": tel_link,
            "mailto_link": mailto_link,
        })

    # Sort: If Critical urgency, prioritize records with contact_phone first, then score descending
    if urgency_level == "Critical":
        scored_orgs.sort(
            key=lambda x: (1 if x.get("contact_phone") else 0, x["match_score"]),
            reverse=True
        )
    else:
        scored_orgs.sort(key=lambda x: x["match_score"], reverse=True)

    log_agent_action(
        "agent2",
        "discover_support_organisations",
        "discovery",
        None,
        input_s=f"locality={locality}, cat={food_category}, urgency={urgency_level}",
        output_s=f"found={len(scored_orgs)} organizations",
        duration_ms=0,
    )

    return scored_orgs[:limit]


def register_recipient_request(
    locality: str,
    food_category: str,
    quantity: int,
    people_count: int,
    required_by_time: datetime,
    urgency_level: str,
    urgency_reason: str,
    special_needs: str = "",
    requester_name: str | None = None,
    requester_phone: str | None = None,
    user_id: int | None = None,
    is_anonymous: bool = True,
) -> int:
    """Store an emergency recipient request."""
    now = datetime.now(timezone.utc)
    data = {
        "user_id": user_id,
        "requester_name": requester_name,
        "requester_phone": requester_phone,
        "locality": locality,
        "city": "Bengaluru",
        "food_category": food_category,
        "quantity": quantity,
        "people_count": people_count,
        "required_by_time": required_by_time,
        "urgency_level": urgency_level,
        "urgency_reason": urgency_reason,
        "special_needs": special_needs,
        "status": "submitted",
        "is_anonymous": is_anonymous,
        "created_at": now,
        "updated_at": now,
    }
    req_id = insert_row("recipient_requests", data)
    log_audit(
        user_id,
        requester_name or "Anonymous Recipient",
        "recipient",
        "submit_emergency_request",
        "recipient_request",
        req_id,
        f"locality={locality}, qty={quantity}, urgency={urgency_level}"
    )
    return req_id


def get_recipient_request(request_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM recipient_requests WHERE id = :id", {"id": request_id})
    return rows[0] if rows else None


def get_active_donor_matches_for_request(
    locality: str,
    food_category: str,
    quantity: int,
    city: str = "Bengaluru",
) -> list[dict]:
    """
    Search active donor offers (screening_passed) matching request constraints.
    Returns compatible active donations if any exist.
    """
    now = datetime.now(timezone.utc)
    sql = """
        SELECT d.*, dorg.name AS donor_name, dorg.address AS donor_address,
               dorg.contact_phone AS donor_phone
        FROM as_donations d
        JOIN as_donor_orgs dorg ON d.donor_org_id = dorg.id
        WHERE d.status IN ('screening_passed', 'matched')
          AND d.pickup_deadline > :now
          AND LOWER(d.city) = LOWER(:city)
        ORDER BY d.created_at DESC
    """
    donations = execute_query(sql, {"now": now, "city": city})

    matches = []
    cat_clean = food_category.strip().lower()
    for don in donations:
        don_cat = (don.get("food_category") or "").strip().lower()
        if cat_clean != "any" and don_cat != cat_clean:
            continue
        # Allocate up to available quantity
        already = get_already_allocated(don["id"])
        avail = don.get("quantity", 0) - already
        if avail > 0:
            alloc = min(avail, quantity)
            matches.append({
                **don,
                "available_quantity": avail,
                "allocated_quantity": alloc,
                "donor_name": don.get("donor_name", "Registered Donor"),
            })

    return matches


def record_recipient_contact(
    request_id: int | None,
    organisation_id: int,
    action: str,
    outcome: str | None = None,
    details: str = "",
    username: str = "Anonymous",
) -> int:
    """Record recipient-initiated contact action and log audit trail."""
    allowed_actions = {"viewed", "called", "emailed", "visited_website", "opened_directions", "marked_contacted"}
    if action not in allowed_actions:
        action = "marked_contacted"

    log_id = insert_row("recipient_contact_log", {
        "request_id": request_id,
        "organisation_id": organisation_id,
        "action": action,
        "outcome": outcome,
        "details": details[:300] if details else None,
        "created_at": datetime.now(timezone.utc),
    })

    log_audit(
        None,
        username,
        "recipient",
        f"contact_org_{action}",
        "support_organisation",
        organisation_id,
        f"request_id={request_id}, action={action}, outcome={outcome}"
    )
    return log_id


def get_support_organisation_by_id(org_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM support_organisations WHERE organisation_id = :id", {"id": org_id})
    return rows[0] if rows else None


def admin_update_organisation(org_id: int, updates: dict, admin_user_id: int, reason: str) -> bool:
    """Update support organisation with strict audit logging."""
    allowed_fields = {
        "organisation_name", "organisation_type", "address", "locality", "city",
        "pincode", "contact_phone", "contact_email", "website_url", "food_services",
        "food_categories_supported", "beneficiary_type", "operating_hours",
        "service_description", "verification_status", "availability_status",
        "can_distribute_food", "is_beneficiary_institution", "is_active"
    }
    clean_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    if not clean_updates:
        return False

    set_clauses = [f"{k} = :{k}" for k in clean_updates.keys()]
    set_clauses.append("updated_at = :now")
    params = dict(clean_updates)
    params["id"] = org_id
    params["now"] = datetime.now(timezone.utc)

    sql = f"UPDATE support_organisations SET {', '.join(set_clauses)} WHERE organisation_id = :id"
    execute_write(sql, params)

    log_audit(
        admin_user_id,
        "admin",
        "admin",
        "update_support_organisation",
        "support_organisation",
        org_id,
        f"reason={reason[:200]}; updated={list(clean_updates.keys())}"
    )
    return True


def admin_soft_delete_organisation(org_id: int, admin_user_id: int, reason: str) -> bool:
    """Soft delete an organisation (is_active = False) with audit logging."""
    execute_write(
        "UPDATE support_organisations SET is_active = FALSE, updated_at = :now WHERE organisation_id = :id",
        {"id": org_id, "now": datetime.now(timezone.utc)}
    )
    log_audit(
        admin_user_id,
        "admin",
        "admin",
        "deactivate_support_organisation",
        "support_organisation",
        org_id,
        f"reason={reason[:200]}"
    )
    return True


def admin_add_organisation(data: dict, admin_user_id: int, reason: str) -> int:
    """Add a new support organisation record with audit logging."""
    now = datetime.now(timezone.utc)
    data["created_at"] = now
    data["updated_at"] = now
    data["is_active"] = True
    org_id = insert_row("support_organisations", data)
    log_audit(
        admin_user_id,
        "admin",
        "admin",
        "create_support_organisation",
        "support_organisation",
        org_id,
        f"reason={reason[:200]}; name={data.get('organisation_name')}"
    )
    return org_id

