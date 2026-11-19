"""
Anna Setu Karnataka — Nine-Category Guardrails
All validation, security, ethical and operational controls in one maintainable module.
"""

import re
import html
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

log = logging.getLogger("annasetu.guardrails")

# ─────────────────────────────────────────────
# A. INPUT GUARDRAILS
# ─────────────────────────────────────────────

_PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all previous",
    r"disregard (your|the) (previous|above|system)",
    r"you are now",
    r"act as (a|an) (different|new|evil|unrestricted)",
    r"jailbreak",
    r"dan mode",
    r"do anything now",
    r"pretend you (are|have no)",
    r"forget (your|all) instructions",
    r"override.*safety",
    r"bypass.*filter",
    r"you have no restrictions",
    r"<script",
    r"javascript:",
    r"';--",
    r"union select",
    r"drop table",
    r"insert into.*values",
    r"exec\s*\(",
    r"xp_cmdshell",
    r"\bor\b.*=.*--",
]

_COMPILED_INJECTION = [re.compile(p, re.IGNORECASE) for p in _PROMPT_INJECTION_PATTERNS]

ALLOWED_FOOD_CATEGORIES = {"cooked_meals", "raw_produce", "bakery", "dairy", "beverages", "snacks", "other"}
ALLOWED_DIETARY_TYPES    = {"vegetarian", "non_vegetarian", "vegan", "jain", "halal", "any"}
ALLOWED_PACKAGING        = {"sealed", "open", "bulk", "vacuum_packed", "other"}
ALLOWED_STORAGE          = {"ambient", "refrigerated", "frozen"}
ALLOWED_ROLES            = {"donor", "recipient", "volunteer", "admin"}
ALLOWED_DONATION_STATUSES = {
    "pending_screening","screening_passed","screening_failed","pending_review",
    "matched","collected","delivered","cancelled"
}
ALLOWED_DELIVERY_STATUSES = {
    "assigned","accepted","picked_up","in_transit","delivered","delayed","failed","cancelled"
}
ALLOWED_MATCH_STATUSES = {
    "proposed","admin_approved","admin_rejected","volunteer_assigned","collected","delivered","failed"
}

MAX_TEXT_LEN  = 1000
MAX_NAME_LEN  = 120
MAX_NOTES_LEN = 2000
MAX_QUANTITY  = 100_000


def check_prompt_injection(text_input: str) -> tuple[bool, str]:
    """Returns (is_safe, reason). is_safe=True means input is clean."""
    if not isinstance(text_input, str):
        return True, ""
    cleaned = text_input.strip()
    if len(cleaned) > MAX_TEXT_LEN:
        return False, f"Input too long ({len(cleaned)} chars, max {MAX_TEXT_LEN})"
    for pattern in _COMPILED_INJECTION:
        if pattern.search(cleaned):
            return False, f"Potential prompt injection or SQL injection detected"
    return True, ""


def sanitise_text(value: str, max_len: int = MAX_TEXT_LEN) -> str:
    """Strip HTML tags and limit length."""
    if not isinstance(value, str):
        return ""
    value = html.escape(value.strip())
    return value[:max_len]


def validate_donation_input(data: dict) -> tuple[bool, list[str]]:
    """Validate all required donation fields. Returns (valid, error_list)."""
    errors = []
    required = ["food_name", "food_category", "dietary_type", "quantity", "pickup_deadline", "location"]
    for field in required:
        if not data.get(field):
            errors.append(f"Required field missing: {field}")

    if data.get("food_name"):
        safe, reason = check_prompt_injection(str(data["food_name"]))
        if not safe:
            errors.append(f"food_name: {reason}")
        if len(str(data["food_name"])) > MAX_NAME_LEN:
            errors.append(f"food_name too long (max {MAX_NAME_LEN})")

    if data.get("food_category") and data["food_category"] not in ALLOWED_FOOD_CATEGORIES:
        errors.append(f"Invalid food_category: {data['food_category']}. Allowed: {ALLOWED_FOOD_CATEGORIES}")

    if data.get("dietary_type") and data["dietary_type"] not in ALLOWED_DIETARY_TYPES:
        errors.append(f"Invalid dietary_type: {data['dietary_type']}. Allowed: {ALLOWED_DIETARY_TYPES}")

    qty = data.get("quantity", 0)
    try:
        qty = int(qty)
        if qty <= 0:
            errors.append("quantity must be a positive integer")
        if qty > MAX_QUANTITY:
            errors.append(f"quantity exceeds maximum ({MAX_QUANTITY})")
    except (ValueError, TypeError):
        errors.append("quantity must be a numeric value")

    if data.get("packaging") and data["packaging"] not in ALLOWED_PACKAGING:
        errors.append(f"Invalid packaging value: {data['packaging']}")

    if data.get("storage_condition") and data["storage_condition"] not in ALLOWED_STORAGE:
        errors.append(f"Invalid storage_condition: {data['storage_condition']}")

    for text_field in ["notes", "allergen_info"]:
        if data.get(text_field):
            safe, reason = check_prompt_injection(str(data[text_field]))
            if not safe:
                errors.append(f"{text_field}: {reason}")

    return len(errors) == 0, errors





def validate_text_field(value: str, field_name: str, max_len: int = MAX_TEXT_LEN) -> tuple[bool, str]:
    if not value or not value.strip():
        return False, f"{field_name} is required"
    safe, reason = check_prompt_injection(value)
    if not safe:
        return False, f"{field_name}: {reason}"
    if len(value) > max_len:
        return False, f"{field_name} too long (max {max_len})"
    return True, ""


# ─────────────────────────────────────────────
# B. OUTPUT GUARDRAILS
# ─────────────────────────────────────────────

def validate_match_output(proposed_matches: list[dict], donation_quantity: int) -> tuple[bool, list[str]]:
    """Ensure no match set exceeds total donation quantity or recipient capacity."""
    errors = []
    total_allocated = sum(m.get("allocated_quantity", 0) for m in proposed_matches)
    if total_allocated > donation_quantity:
        errors.append(
            f"Over-allocation: proposed {total_allocated} but donation has only {donation_quantity}"
        )
    for m in proposed_matches:
        aq = m.get("allocated_quantity", 0)
        cap = m.get("recipient_capacity", float("inf"))
        if aq > cap:
            errors.append(f"Recipient {m.get('recipient_name','?')} capacity {cap} exceeded by allocation {aq}")
        if aq <= 0:
            errors.append(f"Allocation for {m.get('recipient_name','?')} must be > 0")
    return len(errors) == 0, errors





def validate_delivery_status_transition(current: str, new: str) -> tuple[bool, str]:
    """Enforce valid delivery status transitions."""
    transitions = {
        "assigned":   {"accepted", "cancelled"},
        "accepted":   {"picked_up", "cancelled"},
        "picked_up":  {"in_transit"},
        "in_transit": {"delivered", "delayed", "failed"},
        "delayed":    {"delivered", "failed"},
        "delivered":  set(),   # terminal
        "failed":     set(),   # terminal
        "cancelled":  set(),   # terminal
    }
    allowed = transitions.get(current, set())
    if new not in allowed:
        return False, f"Invalid status transition: {current!r} → {new!r}. Allowed: {allowed}"
    return True, ""


def validate_delivery_completion(delivery: dict) -> tuple[bool, str]:
    """Delivery cannot be marked complete without recipient acknowledgement."""
    if not delivery.get("recipient_acknowledged"):
        return False, "Delivery cannot be marked complete: recipient acknowledgement required"
    if not delivery.get("actual_quantity"):
        return False, "Delivery cannot be marked complete: actual quantity not recorded"
    return True, ""


def mask_sensitive_fields(data: dict, role: str) -> dict:
    """Remove fields that should not be visible to a given role."""
    out = dict(data)
    if role not in ("admin",):
        out.pop("password_hash", None)
        out.pop("fssai_number", None)
    if role in ("volunteer",):
        out.pop("email", None)
    return out


# ─────────────────────────────────────────────
# C. TOOL EXECUTION GUARDRAILS
# ─────────────────────────────────────────────

AGENT_TOOL_PERMISSIONS = {
    "agent1": {
        "allowed": {"register_donation", "screen_food_safety", "request_human_review",
                    "get_donation", "update_donation_status", "log_agent_action", "get_donor_org"},
        "denied":  {"approve_match", "assign_volunteer", "mark_delivered", "get_all_users"},
    },
    "agent2": {
        "allowed": {"get_eligible_donations", "get_recipient_orgs", "get_recipient_requirements",
                    "propose_matches", "save_matches", "request_admin_approval",
                    "log_agent_action", "get_donation"},
        "denied":  {"register_donation", "assign_volunteer", "mark_delivered", "get_all_users"},
    },
    "agent3": {
        "allowed": {"get_approved_matches", "get_available_volunteers", "get_transport_providers",
                    "create_assignment", "update_assignment_status", "log_agent_action",
                    "get_donation", "notify_volunteer"},
        "denied":  {"register_donation", "approve_match", "mark_delivered", "get_all_users"},
    },
    "agent4": {
        "allowed": {"get_assignments", "update_delivery_status", "record_acknowledgement",
                    "generate_impact_report", "log_agent_action", "get_donation",
                    "get_deliveries", "alert_admin"},
        "denied":  {"register_donation", "approve_match", "assign_volunteer", "get_all_users"},
    },
}


def check_tool_permission(agent_name: str, tool_name: str) -> tuple[bool, str]:
    perms = AGENT_TOOL_PERMISSIONS.get(agent_name)
    if perms is None:
        return False, f"Unknown agent: {agent_name}"
    if tool_name in perms["denied"]:
        return False, f"Agent {agent_name} is not permitted to use tool: {tool_name}"
    return True, ""


def validate_tool_args(tool_name: str, args: dict) -> tuple[bool, list[str]]:
    errors = []
    if tool_name == "register_donation":
        return validate_donation_input(args)
    if tool_name in ("update_donation_status", "update_delivery_status", "update_assignment_status"):
        if not args.get("id"):
            errors.append("id is required")
        if not args.get("status"):
            errors.append("status is required")
    if tool_name == "propose_matches":
        if not isinstance(args.get("matches"), list):
            errors.append("matches must be a list")
    return len(errors) == 0, errors





# ─────────────────────────────────────────────
# D. DATA GUARDRAILS
# ─────────────────────────────────────────────

ROLE_READ_PERMISSIONS = {
    "donor":     {"as_donations", "as_donor_orgs", "as_donation_matches", "as_deliveries"},
    "recipient": {"as_recipient_orgs", "as_donation_matches", "as_deliveries", "as_recipient_requirements"},
    "volunteer": {"as_volunteers", "as_collection_assignments", "as_deliveries"},
    "admin":     {"*"},  # all tables
}

ROLE_WRITE_PERMISSIONS = {
    "donor":     {"as_donations"},
    "recipient": {"as_recipient_requirements", "as_deliveries"},  # only acknowledgement
    "volunteer": {"as_collection_assignments", "as_deliveries"},
    "admin":     {"*"},
}


def check_data_access(role: str, table: str, operation: str = "read") -> bool:
    perm_map = ROLE_READ_PERMISSIONS if operation == "read" else ROLE_WRITE_PERMISSIONS
    allowed = perm_map.get(role, set())
    return "*" in allowed or table in allowed


def check_org_ownership(user: dict, record_org_id: int | None) -> bool:
    """Non-admin users may only access records belonging to their organisation."""
    if user["role"] == "admin":
        return True
    if record_org_id is None:
        return True
    return user.get("org_id") == record_org_id


# ─────────────────────────────────────────────
# E. SECURITY GUARDRAILS
# ─────────────────────────────────────────────

def validate_session(session_state: dict) -> bool:
    return bool(session_state.get("authenticated") and session_state.get("user"))


def validate_role_access(session_state: dict, required_role: str | list) -> tuple[bool, str]:
    if not validate_session(session_state):
        return False, "Not authenticated"
    user = session_state.get("user", {})
    allowed = required_role if isinstance(required_role, list) else [required_role]
    if user.get("role") not in allowed:
        return False, f"Role '{user.get('role')}' cannot access this resource"
    return True, ""


SAFE_SQL_PARAM_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\. ]+$')


def validate_sql_param(value: str) -> bool:
    """Reject values that look like SQL injection attempts (belt+suspenders beyond parameterised queries)."""
    if not isinstance(value, str):
        return True  # non-strings are handled by SQLAlchemy typing
    dangerous = ["'", '"', ";", "--", "/*", "*/", "xp_", "union", "select", "drop", "insert", "exec"]
    lower = value.lower()
    return not any(d in lower for d in dangerous)


# ─────────────────────────────────────────────
# F. OPERATIONAL GUARDRAILS
# ─────────────────────────────────────────────

AGENT_MAX_ITERATIONS = 5
AGENT_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
MAX_LLM_TOKENS = 1024


def bounded_retry(func, retries: int = MAX_RETRIES, default=None):
    """Call func up to retries times, return default on all failures."""
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            log.warning(f"Retry {attempt+1}/{retries} failed: {e}")
    log.error(f"All {retries} retries exhausted, returning default")
    return default


# ─────────────────────────────────────────────
# G. HUMAN-IN-THE-LOOP GUARDRAILS
# ─────────────────────────────────────────────

SAFETY_REVIEW_TRIGGERS = [
    "reheated",
    "expired",
    "unknown prep time",
    "open packaging",
    "unsafe temperature",
    "unverified source",
    "no fssai",
    "allergen",
    "unclear storage",
    "potentially unsafe",
]


def requires_human_safety_review(screening_result: dict) -> tuple[bool, str]:
    """Flag donations that must have human review before matching."""
    result = screening_result.get("screening_result", "").lower()
    if result == "blocked":
        return True, "Food safety screening result is BLOCKED — requires admin review before any action"
    if result == "pending_review":
        return True, "Food safety screening flagged for human review"
    issues = screening_result.get("issues_found", "").lower()
    for trigger in SAFETY_REVIEW_TRIGGERS:
        if trigger in issues:
            return True, f"Safety concern detected: '{trigger}' — human review required"
    return False, ""


def requires_admin_approval_for_match(match: dict) -> tuple[bool, str]:
    if match.get("allocated_quantity", 0) > 500:
        return True, "Large allocation (>500) requires admin approval"
    return False, ""


# ─────────────────────────────────────────────
# H. MULTI-AGENT GUARDRAILS
# ─────────────────────────────────────────────

AUTHORISED_AGENTS = {"agent1", "agent2", "agent3", "agent4"}
MAX_GRAPH_ITERATIONS = 20


def validate_agent_identity(agent_name: str) -> bool:
    return agent_name in AUTHORISED_AGENTS


def validate_handoff(from_agent: str, to_agent: str, state: dict) -> tuple[bool, str]:
    """Check that handoff is valid given the current workflow state."""
    valid_transitions = {
        "agent1": {"agent2"},
        "agent2": {"agent3"},
        "agent3": {"agent4"},
        "agent4": set(),
    }
    if from_agent not in valid_transitions:
        return False, f"Unknown agent: {from_agent}"
    if to_agent not in valid_transitions[from_agent]:
        return False, f"Invalid handoff: {from_agent} → {to_agent}"
    return True, ""


def check_iteration_limit(iterations: int) -> tuple[bool, str]:
    if iterations >= MAX_GRAPH_ITERATIONS:
        return False, f"Maximum agent iterations ({MAX_GRAPH_ITERATIONS}) reached — stopping"
    return True, ""


# ─────────────────────────────────────────────
# I. ETHICAL AND COMPLIANCE GUARDRAILS
# ─────────────────────────────────────────────

PROHIBITED_RANKING_FACTORS = {
    "caste", "religion", "race", "gender", "political", "nationality"
}


def validate_matching_fairness(match_reason: str) -> tuple[bool, str]:
    """Ensure matching decisions don't use prohibited discriminatory factors."""
    lower = match_reason.lower()
    for factor in PROHIBITED_RANKING_FACTORS:
        if factor in lower:
            return False, f"Match reason references prohibited factor: '{factor}'"
    return True, ""


def validate_impact_data_source(report: dict) -> tuple[bool, str]:
    """Impact statistics must be grounded in confirmed DB records."""
    if report.get("source") not in ("database", "confirmed_records"):
        return False, "Impact report must be derived from confirmed PostgreSQL records only"
    if report.get("simulated", False):
        return False, "Impact report cannot contain simulated statistics"
    return True, ""


# ─────────────────────────────────────────────
# COMPOSITE: Pre-flight check for donation registration
# ─────────────────────────────────────────────

def pre_flight_donation(data: dict, user: dict) -> tuple[bool, list[str]]:
    """Run all relevant input + security + data guardrails before saving a donation."""
    errors = []

    # Role check
    if user.get("role") not in ("donor", "admin"):
        errors.append("Only donors or admins can register donations")

    # Input validation
    valid, field_errors = validate_donation_input(data)
    errors.extend(field_errors)

    # Org ownership
    if user.get("role") == "donor" and not user.get("org_id"):
        errors.append("Donor account must be linked to an organisation")

    return len(errors) == 0, errors

# ─────────────────────────────────────────────
# PHASE 2: RECIPIENT EMERGENCY REQUEST GUARDRAILS
# ─────────────────────────────────────────────

# PRODUCT RULES (editable), not regulatory standards
CRITICAL_HOURS_THRESHOLD = 3.0
URGENT_HOURS_THRESHOLD   = 12.0
SEVERITY_ORDER = {"Normal": 1, "Urgent": 2, "Critical": 3}

ALLOWED_RECIPIENT_CATEGORIES = {
    "cooked_meals", "raw_produce", "packaged", "dairy", "bakery", "beverages", "grains", "any"
}

VULNERABLE_URGENCY_KEYWORDS = [
    r"no meal\b.*today",
    r"no food\b.*today",
    r"starv",
    r"children\b.*(hungry|no food|no meal)",
    r"infant\b.*(no food|no milk)",
    r"baby\b.*(no food|no milk)",
    r"elderly\b.*(no food|no meal|sick)",
    r"sick\b.*(no food|no meal)",
    r"haven't eaten\b.*today",
    r"nothing to eat",
]
_COMPILED_VULNERABLE = [re.compile(p, re.IGNORECASE) for p in VULNERABLE_URGENCY_KEYWORDS]


def calculate_deterministic_urgency(
    required_by_time: datetime | str,
    special_needs: str = "",
    user_selected: str = "Normal"
) -> tuple[str, str]:
    """
    PRODUCT RULES (editable), not regulatory standards:
    - CRITICAL: needed within 3 hours, OR request states no meal today for children, elderly, sick.
    - URGENT: needed within 12 hours.
    - NORMAL: otherwise.
    Final level = max(rule_level, user_selected). LLM or user cannot downgrade rule-based severity.
    Returns (urgency_level, urgency_reason).
    """
    now = datetime.now(timezone.utc)
    target_dt = required_by_time
    if isinstance(target_dt, str):
        try:
            target_dt = datetime.fromisoformat(target_dt.replace("Z", "+00:00"))
        except Exception:
            target_dt = now + timedelta(hours=2) # safe fallback

    if target_dt.tzinfo is None:
        target_dt = target_dt.replace(tzinfo=timezone.utc)

    hours_left = (target_dt - now).total_seconds() / 3600.0

    rule_level = "Normal"
    rule_reasons = []

    # Check vulnerability text
    vulnerable_match = False
    if special_needs:
        for pat in _COMPILED_VULNERABLE:
            if pat.search(special_needs):
                vulnerable_match = True
                break

    if hours_left <= CRITICAL_HOURS_THRESHOLD or vulnerable_match:
        rule_level = "Critical"
        if hours_left <= CRITICAL_HOURS_THRESHOLD:
            rule_reasons.append(f"Critical because food needed within {max(0, round(hours_left, 1))} hours (threshold: <= {CRITICAL_HOURS_THRESHOLD}h)")
        if vulnerable_match:
            rule_reasons.append("Critical because request states vulnerable beneficiaries (children/elderly/sick) have no meal available today")
    elif hours_left <= URGENT_HOURS_THRESHOLD:
        rule_level = "Urgent"
        rule_reasons.append(f"Urgent because food needed within {round(hours_left, 1)} hours (threshold: <= {URGENT_HOURS_THRESHOLD}h)")
    else:
        rule_level = "Normal"
        rule_reasons.append(f"Normal priority (needed in {round(hours_left, 1)} hours)")

    # The final level = higher of (rules, explicit user selection)
    user_level = user_selected.capitalize() if user_selected else "Normal"
    if user_level not in SEVERITY_ORDER:
        user_level = "Normal"

    if SEVERITY_ORDER[user_level] > SEVERITY_ORDER[rule_level]:
        final_level = user_level
        rule_reasons.append(f"Elevated to {user_level} based on explicit recipient selection")
    else:
        final_level = rule_level

    reason_str = " | ".join(rule_reasons)
    return final_level, reason_str


def validate_recipient_request_input(data: dict) -> tuple[bool, list[str]]:
    """Validate all fields for urgent recipient food discovery request."""
    errors = []
    
    # Locality
    locality = str(data.get("locality", "")).strip()
    if not locality:
        errors.append("Locality is required")
    else:
        safe, reason = check_prompt_injection(locality)
        if not safe:
            errors.append(f"locality: {reason}")
        if len(locality) > 120:
            errors.append("locality too long (max 120 chars)")

    # Food Category
    category = data.get("food_category", "cooked_meals")
    if category not in ALLOWED_RECIPIENT_CATEGORIES:
        errors.append(f"Invalid food category '{category}'. Allowed: {ALLOWED_RECIPIENT_CATEGORIES}")

    # Quantity
    try:
        qty = int(data.get("quantity", 0))
        if qty <= 0:
            errors.append("quantity must be greater than 0")
        elif qty > 100_000:
            errors.append("quantity exceeds maximum allowed (100,000)")
    except (ValueError, TypeError):
        errors.append("quantity must be an integer")

    # People count
    try:
        people = int(data.get("people_count", 0))
        if people <= 0:
            errors.append("number of people must be greater than 0")
        elif people > 50_000:
            errors.append("people_count exceeds maximum allowed (50,000)")
    except (ValueError, TypeError):
        errors.append("number of people must be an integer")

    # Required by time
    req_time = data.get("required_by_time")
    if not req_time:
        errors.append("required_by_time is required")
    else:
        now = datetime.now(timezone.utc)
        if isinstance(req_time, str):
            try:
                req_time = datetime.fromisoformat(req_time.replace("Z", "+00:00"))
            except Exception:
                errors.append("required_by_time is not a valid ISO timestamp")
        if isinstance(req_time, datetime):
            if req_time.tzinfo is None:
                req_time = req_time.replace(tzinfo=timezone.utc)
            if req_time <= now - timedelta(minutes=5):
                errors.append("required_by_time must be in the future")

    # Special needs
    special_needs = data.get("special_needs")
    if special_needs:
        safe, reason = check_prompt_injection(str(special_needs))
        if not safe:
            errors.append(f"special_needs: {reason}")
        if len(str(special_needs)) > 2000:
            errors.append("special_needs too long (max 2000 chars)")

    return len(errors) == 0, errors


def validate_organisation_filter_args(args: dict) -> tuple[bool, str]:
    """Validate arguments for discovery tool to prevent SQL injection or malformed filters."""
    for key, val in args.items():
        if val is not None and isinstance(val, str):
            safe, reason = check_prompt_injection(val)
            if not safe:
                return False, f"Invalid characters in filter '{key}': {reason}"
    return True, ""
