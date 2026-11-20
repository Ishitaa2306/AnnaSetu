"""
Anna Setu Karnataka — Four Specialised Agents + LangGraph Orchestration
Agents: 1=Donation&Safety, 2=Matching&Priority, 3=Collection&Logistics, 4=Delivery&Impact
"""

import os
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any, TypedDict, Annotated, Literal

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("annasetu.agents")

# ─────────────────────────────────────────────
# LLM CLIENTS — with availability detection
# ─────────────────────────────────────────────

_gemini_client = None
_gemini_model  = None
_granite_model = None

_ai_status = {
    "gemini_available":  False,
    "granite_available": False,
    "gemini_error":      "",
    "granite_error":     "",
}


# Ordered preference list — fast responding models first
_GEMINI_MODEL_PREFERENCE = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
]


def _probe_gemini_model(client, model_id: str) -> bool:
    """Return True if the model responds within 3.5 s."""
    import threading
    result = [False]
    err = [None]

    def _call():
        try:
            resp = client.models.generate_content(model=model_id, contents="ping")
            if resp and (resp.text is not None):
                result[0] = True
        except Exception as exc:
            err[0] = exc

    t = threading.Thread(target=_call, daemon=True)
    t.start()
    t.join(timeout=3.5)
    if not result[0] and err[0]:
        log.debug(f"Gemini probe {model_id}: {str(err[0])[:80]}")
    return result[0]


def _init_gemini():
    global _gemini_client, _gemini_model
    try:
        from google import genai
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            raise ValueError("GEMINI_API_KEY not set")
        _gemini_client = genai.Client(api_key=key)

        # Determine which model to use:
        # 1. Try the model from .env first (if set and not a known-removed name)
        env_model = os.environ.get("GEMINI_MODEL_ID", "").strip()
        _REMOVED_MODELS = {"gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro",
                           "gemini-1.0-pro", "gemini-pro", "gemini-2.5-flash"}
        candidates = []
        if env_model and env_model not in _REMOVED_MODELS:
            candidates = [env_model] + [m for m in _GEMINI_MODEL_PREFERENCE if m != env_model]
        else:
            candidates = _GEMINI_MODEL_PREFERENCE

        selected = None
        for model_id in candidates:
            log.info(f"Probing Gemini model: {model_id}")
            if _probe_gemini_model(_gemini_client, model_id):
                selected = model_id
                break
            else:
                log.warning(f"Gemini model {model_id} not available, trying next")

        if selected is None:
            raise RuntimeError(
                f"No working Gemini model found. Tried: {candidates}. "
                "API may be experiencing issues or key may be invalid."
            )

        _gemini_model = selected
        _ai_status["gemini_available"] = True
        log.info(f"Gemini initialised OK — using model: {_gemini_model}")
    except Exception as e:
        _ai_status["gemini_error"] = str(e)[:200]
        log.warning(f"Gemini unavailable: {e}")


def _init_granite():
    global _granite_model
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        creds = Credentials(
            url=os.environ.get("WATSONX_URL", ""),
            api_key=os.environ.get("WATSONX_API_KEY", "")
        )
        model_id  = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-4-h-small")
        project_id = os.environ.get("WATSONX_PROJECT_ID", "")
        _granite_model = ModelInference(
            model_id=model_id, credentials=creds, project_id=project_id
        )
        # Quick probe
        _granite_model.chat(messages=[{"role":"user","content":"ping"}], params={"max_new_tokens": 5})
        _ai_status["granite_available"] = True
        log.info("IBM Granite initialised OK")
    except Exception as e:
        _ai_status["granite_error"] = str(e)[:120]
        log.warning(f"Granite unavailable: {e}")


def get_ai_status() -> dict:
    status = dict(_ai_status)
    status["gemini_model"] = _gemini_model or "none"
    return status


def call_gemini(prompt: str, max_tokens: int = 512) -> str:
    if not _ai_status["gemini_available"] or _gemini_client is None:
        return ""
    try:
        from google.genai import types as gtypes
        resp = _gemini_client.models.generate_content(
            model=_gemini_model,
            contents=prompt,
            config=gtypes.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        # sdk v2: resp.text is a str or None
        if resp is None:
            return ""
        text = getattr(resp, "text", None)
        if text is None:
            # Try candidates path (older SDK shape)
            try:
                text = resp.candidates[0].content.parts[0].text
            except Exception:
                text = ""
        return text.strip() if text else ""
    except Exception as e:
        log.warning(f"Gemini call failed: {e}")
        return ""


def call_granite(prompt: str, max_tokens: int = 512) -> str:
    if not _ai_status["granite_available"] or _granite_model is None:
        return ""
    try:
        # Use chat API (generate_text is deprecated in newer SDK)
        messages = [{"role": "user", "content": prompt}]
        response = _granite_model.chat(
            messages=messages,
            params={"max_new_tokens": min(max_tokens, 1024)}
        )
        # Extract text from chat response
        text = ""
        if isinstance(response, dict):
            choices = response.get("choices", response.get("results", []))
            if choices:
                msg = choices[0]
                text = msg.get("message", {}).get("content", "") if isinstance(msg, dict) else str(msg)
        elif hasattr(response, "text"):
            text = response.text or ""
        elif isinstance(response, str):
            text = response
        return text.strip() if text else ""
    except Exception as e:
        log.warning(f"Granite call failed: {e}")
        return ""


def llm_call(prompt: str, prefer: str = "gemini", max_tokens: int = 400) -> tuple[str, str]:
    """Call preferred LLM, fall back to other, then return empty + 'rules' label."""
    if prefer == "granite":
        result = call_granite(prompt, max_tokens)
        if result:
            return result, "granite"
        result = call_gemini(prompt, max_tokens)
        if result:
            return result, "gemini"
    else:
        result = call_gemini(prompt, max_tokens)
        if result:
            return result, "gemini"
        result = call_granite(prompt, max_tokens)
        if result:
            return result, "granite"
    return "", "rules"


# ─────────────────────────────────────────────
# LANGGRAPH STATE
# ─────────────────────────────────────────────

class AnnaSetu_State(TypedDict):
    # Input
    donation_id:        int
    # Agent 1 output
    screening_result:   str            # eligible | pending_review | blocked
    safety_record_id:   int
    safety_issues:      str
    # Agent 2 output
    proposed_matches:   list[dict]
    match_ids:          list[int]
    approval_requested: bool
    # Agent 3 output
    assignment_ids:     list[int]
    assignment_details: list[dict]
    # Agent 4 output
    delivery_ids:       list[int]
    impact_report:      dict
    # Control
    current_agent:      str
    errors:             list[str]
    human_review_needed: bool
    iterations:         int
    workflow_complete:  bool
    model_used:         str


# ─────────────────────────────────────────────
# AGENT 1 — Donation & Food Safety
# ─────────────────────────────────────────────

def _build_safety_prompt(donation: dict) -> str:
    return f"""You are a food safety expert using FSSAI guidelines.
Analyse this food donation for safety risks:

Food: {donation.get('food_name')}
Category: {donation.get('food_category')}
Dietary type: {donation.get('dietary_type')}
Quantity: {donation.get('quantity')} {donation.get('unit','')}
Preparation time: {donation.get('preparation_time','unknown')}
Pickup deadline: {donation.get('pickup_deadline')}
Packaging: {donation.get('packaging','unknown')}
Storage: {donation.get('storage_condition','unknown')}
Allergens: {donation.get('allergen_info','none stated')}
Notes: {donation.get('notes','')}

Respond with JSON ONLY in this format:
{{"result":"eligible|pending_review|blocked","score":0-10,"issues":"...","recommendations":"..."}}
where score 7-10=eligible, 4-6=pending_review, 0-3=blocked.
Never certify as safe without sufficient information. Flag unknown prep time as pending_review."""


def _rules_based_safety(donation: dict) -> dict:
    """Deterministic fallback when no LLM is available."""
    issues = []
    score = 8.0
    result = "eligible"

    if not donation.get("preparation_time"):
        issues.append("Preparation time not provided")
        score -= 2.0

    deadline = donation.get("pickup_deadline")
    if deadline:
        if isinstance(deadline, str):
            try:
                deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            except Exception:
                deadline = None
        if deadline:
            hours_left = (deadline - datetime.now(timezone.utc)).total_seconds() / 3600
            if hours_left < 2:
                issues.append("Pickup deadline is very soon (< 2 hours)")
                score -= 2.0
            elif hours_left < 0:
                issues.append("Pickup deadline has passed")
                score -= 5.0
                result = "blocked"

    if donation.get("packaging") == "open":
        issues.append("Open packaging — higher contamination risk")
        score -= 1.5

    if donation.get("storage_condition") not in ("refrigerated", "frozen", "ambient"):
        issues.append("Storage condition unclear")
        score -= 1.0

    score = max(0.0, min(10.0, score))
    if score < 4:
        result = "blocked"
    elif score < 7:
        result = "pending_review"

    return {
        "result": result,
        "score": round(score, 1),
        "issues": "; ".join(issues) if issues else "No major issues detected (rule-based)",
        "recommendations": "[RULE-BASED — not AI-generated] Verify preparation time and packaging before dispatch.",
    }


def agent1_donation_safety(state: AnnaSetu_State) -> AnnaSetu_State:
    from tools import get_donation, update_donation_status, save_food_safety_record, request_human_review
    from guardrails import check_iteration_limit, requires_human_safety_review

    state = dict(state)
    state["current_agent"] = "agent1"
    state["iterations"] = state.get("iterations", 0) + 1

    ok, msg = check_iteration_limit(state["iterations"])
    if not ok:
        state["errors"] = state.get("errors", []) + [msg]
        state["workflow_complete"] = True
        return state

    t0 = time.time()
    donation_id = state["donation_id"]
    donation = get_donation(donation_id)

    if not donation:
        state["errors"] = [f"Donation {donation_id} not found"]
        state["workflow_complete"] = True
        return state

    # LLM safety analysis (Granite preferred for classification)
    prompt = _build_safety_prompt(donation)
    llm_text, model = llm_call(prompt, prefer="granite", max_tokens=256)

    safety = {}
    if llm_text:
        import json, re
        # Extract JSON from LLM response
        match = re.search(r'\{.*\}', llm_text, re.DOTALL)
        if match:
            try:
                safety = json.loads(match.group())
            except Exception:
                pass

    if not safety:
        safety = _rules_based_safety(donation)
        model = "rules"

    screening_result = safety.get("result", "pending_review")
    safety_score     = float(safety.get("score", 5.0))
    issues           = str(safety.get("issues", ""))
    recommendations  = str(safety.get("recommendations", ""))

    # Save safety record
    safety_record_id = save_food_safety_record(
        donation_id, screening_result, safety_score, issues, recommendations, model
    )

    # Update donation status
    if screening_result == "eligible":
        update_donation_status(donation_id, "screening_passed", "agent1")
    elif screening_result == "blocked":
        update_donation_status(donation_id, "screening_failed", "agent1")
    else:
        update_donation_status(donation_id, "pending_review", "agent1")

    # Human review?
    needs_review, reason = requires_human_safety_review({"screening_result": screening_result, "issues_found": issues})
    if needs_review:
        request_human_review("donation", donation_id, reason, "agent1")
        state["human_review_needed"] = True

    duration = int((time.time() - t0) * 1000)
    from database import log_agent_action
    log_agent_action("agent1", "safety_screening", "donation", donation_id,
                     input_s=f"food={donation.get('food_name')}", output_s=screening_result,
                     model=model, success=True, duration_ms=duration)

    state.update({
        "screening_result": screening_result,
        "safety_record_id": safety_record_id,
        "safety_issues": issues,
        "model_used": model,
        "errors": state.get("errors", []),
    })
    return state


# ─────────────────────────────────────────────
# AGENT 2 — Recipient Matching & Priority
# ─────────────────────────────────────────────

def _score_recipient(donation: dict, recip_org: dict, req: dict | None, already_allocated: int) -> dict:
    """Pure-Python scoring — LLM used only for explanation text."""
    score = 0.0
    reasons = []

    total_qty = donation.get("quantity", 0)
    remaining  = total_qty - already_allocated
    cap        = recip_org.get("capacity_meals_per_day", 50)
    needed     = req.get("quantity_needed", cap) if req else cap

    # Hard eligibility
    if remaining <= 0:
        return {"eligible": False, "reason": "No remaining quantity"}
    if cap <= 0:
        return {"eligible": False, "reason": "Recipient has no capacity"}

    # Dietary compatibility
    donor_diet  = donation.get("dietary_type", "any").lower()
    recip_diet  = (recip_org.get("dietary_restrictions") or "any").lower()
    if recip_diet != "any":
        if donor_diet == "non_vegetarian" and recip_diet in ("vegetarian", "vegan", "jain"):
            return {"eligible": False, "reason": "Dietary incompatibility: recipient requires vegetarian/vegan food"}
        if donor_diet == "non_vegetarian" and recip_diet == "halal":
            # Could be ok but flag
            reasons.append("Non-vegetarian food to halal org — requires human check")
            score -= 1

    score += 3  # base
    reasons.append("Dietary compatibility OK")

    # Category match
    if req and req.get("food_category") == donation.get("food_category"):
        score += 2
        reasons.append("Food category match")

    # Urgency / deadline
    deadline = donation.get("pickup_deadline")
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        except Exception:
            deadline = None
    if deadline:
        hours = (deadline - datetime.now(timezone.utc)).total_seconds() / 3600
        if hours < 4:
            score += 2
            reasons.append("Urgent — pickup within 4h")
        elif hours < 8:
            score += 1
            reasons.append("Moderate urgency")

    # Capacity fit
    max_alloc = min(remaining, cap, needed)
    if max_alloc <= 0:
        return {"eligible": False, "reason": "Insufficient quantity for recipient"}
    score += 1
    reasons.append(f"Can supply {max_alloc} meals")

    return {
        "eligible": True,
        "score": round(score, 2),
        "allocated_quantity": max_alloc,
        "reason": "; ".join(reasons),
    }


def agent2_matching_priority(state: AnnaSetu_State) -> AnnaSetu_State:
    from tools import (get_donation, get_recipient_orgs, get_recipient_requirements,
                       get_already_allocated, save_matches, request_admin_approval,
                       update_donation_status)
    from guardrails import validate_match_output, check_iteration_limit

    state = dict(state)
    state["current_agent"] = "agent2"
    state["iterations"] = state.get("iterations", 0) + 1

    ok, msg = check_iteration_limit(state["iterations"])
    if not ok:
        state["errors"] = state.get("errors", []) + [msg]
        return state

    donation_id = state["donation_id"]
    donation = get_donation(donation_id)
    if not donation:
        state["errors"] = state.get("errors", []) + [f"Donation {donation_id} not found in agent2"]
        return state

    recip_orgs = get_recipient_orgs(city=donation.get("city"))
    if not recip_orgs:
        recip_orgs = get_recipient_orgs()  # any city fallback

    all_reqs = {r["org_id"]: r for r in get_recipient_requirements()}
    already_allocated = get_already_allocated(donation_id)
    total_qty = donation.get("quantity", 0)
    remaining = total_qty - already_allocated

    candidates = []
    for org in recip_orgs:
        req = all_reqs.get(org["id"])
        result = _score_recipient(donation, org, req, already_allocated)
        if result.get("eligible"):
            candidates.append({
                "recipient_org_id": org["id"],
                "recipient_name":   org["name"],
                "recipient_capacity": org.get("capacity_meals_per_day", 50),
                "allocated_quantity": result["allocated_quantity"],
                "match_score":       result["score"],
                "match_reason":      result["reason"],
                "donation_id":       donation_id,
                "is_demo":           donation.get("is_demo", False),
            })
        already_allocated += result.get("allocated_quantity", 0)

    # Sort by score descending
    candidates.sort(key=lambda x: x["match_score"], reverse=True)

    # Recalculate allocation with running sum
    running = get_already_allocated(donation_id)
    final_matches = []
    for c in candidates:
        avail = total_qty - running
        if avail <= 0:
            break
        alloc = min(c["allocated_quantity"], avail)
        c["allocated_quantity"] = alloc
        final_matches.append(c)
        running += alloc

    if not final_matches:
        state["errors"] = state.get("errors", []) + ["No suitable recipients found for this donation"]
        return state

    # Validate no over-allocation
    valid, v_errors = validate_match_output(final_matches, total_qty)
    if not valid:
        state["errors"] = state.get("errors", []) + v_errors
        return state

    # Optionally enrich match reason with Gemini
    if _ai_status["gemini_available"] and final_matches:
        food_desc = f"{donation.get('food_name')} ({donation.get('dietary_type')})"
        recip_summary = ", ".join(m["recipient_name"] for m in final_matches[:3])
        prompt = (f"Briefly explain (2 sentences) why matching surplus food '{food_desc}' "
                  f"to '{recip_summary}' is a good decision for a food rescue platform in Bengaluru, Karnataka.")
        explanation, mdl = llm_call(prompt, prefer="gemini", max_tokens=150)
        if explanation:
            for m in final_matches:
                m["match_reason"] = m["match_reason"] + f" | {explanation}"
            state["model_used"] = mdl

    # Save matches
    match_ids = save_matches(final_matches)
    update_donation_status(donation_id, "matched", "agent2")

    # Request admin approval
    request_admin_approval(match_ids, "Automated matching — requires admin review before volunteer assignment")

    from database import log_agent_action
    log_agent_action("agent2", "propose_matches", "donation", donation_id,
                     output_s=f"{len(match_ids)} matches proposed", model=state.get("model_used", "rules"))

    state.update({
        "proposed_matches": final_matches,
        "match_ids": match_ids,
        "approval_requested": True,
        "errors": state.get("errors", []),
    })
    return state


# ─────────────────────────────────────────────
# AGENT 3 — Collection & Logistics
# ─────────────────────────────────────────────

def agent3_logistics(state: AnnaSetu_State) -> AnnaSetu_State:
    from tools import (get_approved_matches, get_available_volunteers, get_transport_providers,
                       create_assignment, notify_volunteer, get_donation, estimate_bengaluru_route)
    from guardrails import check_iteration_limit

    state = dict(state)
    state["current_agent"] = "agent3"
    state["iterations"] = state.get("iterations", 0) + 1

    ok, msg = check_iteration_limit(state["iterations"])
    if not ok:
        state["errors"] = state.get("errors", []) + [msg]
        return state

    match_ids = state.get("match_ids", [])
    if not match_ids:
        # Look up approved matches from DB
        approved = get_approved_matches()
        match_ids = [m["id"] for m in approved if m["donation_id"] == state["donation_id"]]

    if not match_ids:
        state["errors"] = state.get("errors", []) + ["No approved matches found for logistics"]
        return state

    donation = get_donation(state["donation_id"])
    city = donation.get("city", "Bengaluru") if donation else "Bengaluru"

    volunteers = get_available_volunteers(city=city) or get_available_volunteers()
    transports  = get_transport_providers(city=city) or get_transport_providers()

    assignment_ids = []
    assignment_details = []

    for idx, match_id in enumerate(match_ids):
        from tools import get_match
        match = get_match(match_id)
        if not match or match.get("status") != "admin_approved":
            continue

        alloc_qty = match.get("allocated_quantity", 0)
        pickup_location   = donation.get("location", "Donor location") if donation else "Donor location"
        delivery_location = match.get("recipient_address", match.get("delivery_location", "Recipient location"))

        # Route and distance estimation using Bengaluru corridor model
        route_info = estimate_bengaluru_route(pickup_location, delivery_location)
        dist_km = route_info["distance_km"]
        transit_mins = route_info["transit_mins"]
        route_summary = route_info["summary"]

        # Hybrid Logistics Model:
        # 1. Nearby / Community Volunteer for meal quantities <= 80
        # 2. NGO fleet or CSR sponsored transport for larger loads or when no volunteer
        # 3. Commercial logistics partner when bulk meals (> 150) or paid dispatch
        chosen_vol  = None
        chosen_trans = None
        transport_mode = "volunteer"
        delivery_cost = 0.0
        sponsor_name = ""

        if alloc_qty <= 80:
            for v in volunteers:
                if v.get("vehicle_capacity_meals", 0) >= alloc_qty:
                    chosen_vol = v
                    break
            if not chosen_vol and volunteers:
                chosen_vol = volunteers[0]

        if not chosen_vol:
            # Check for NGO or CSR transport first
            for t in transports:
                if t.get("capacity_meals", 0) >= alloc_qty:
                    if t.get("service_type") in ("NGO Vehicle", "CSR Sponsored"):
                        chosen_trans = t
                        break
            if not chosen_trans:
                for t in transports:
                    if t.get("capacity_meals", 0) >= alloc_qty:
                        chosen_trans = t
                        break
            if not chosen_trans and transports:
                chosen_trans = transports[0]

            if chosen_trans:
                stype = chosen_trans.get("service_type", "Commercial")
                if stype == "NGO Vehicle":
                    transport_mode = "ngo_vehicle"
                elif stype == "CSR Sponsored":
                    transport_mode = "sponsored_transport"
                    sponsor_name = "Infosys Foundation CSR Food Transport Grant"
                else:
                    transport_mode = "paid_logistics"
                    base = float(chosen_trans.get("base_rate") or 150.0)
                    per_km = float(chosen_trans.get("per_km_rate") or 15.0)
                    delivery_cost = round(base + (dist_km * per_km), 2)
            else:
                transport_mode = "unassigned_alert"
        else:
            transport_mode = "volunteer"

        # Schedule pickup in next 1.5 - 2 hours
        pickup_time = datetime.now(timezone.utc) + timedelta(hours=2)
        is_demo = match.get("is_demo", False)

        aid = create_assignment(
            match_id              = match_id,
            volunteer_id          = chosen_vol["id"] if chosen_vol else None,
            transport_provider_id = chosen_trans["id"] if chosen_trans else None,
            pickup_location       = pickup_location,
            delivery_location     = delivery_location,
            pickup_time_scheduled = pickup_time,
            notes                 = f"[{'DEMO ' if is_demo else ''}Agent 3 Dispatch: {transport_mode}]",
            is_demo               = is_demo,
            transport_mode        = transport_mode,
            route_summary         = route_summary,
            estimated_distance_km = dist_km,
            estimated_transit_mins= transit_mins,
            delivery_cost         = delivery_cost,
            sponsor_name          = sponsor_name,
        )

        if chosen_vol:
            notify_volunteer(chosen_vol["id"],
                             f"You have a new pickup assignment #{aid}. {route_summary}. Pickup: {pickup_location}")

        assignment_ids.append(aid)
        assignment_details.append({
            "assignment_id": aid,
            "match_id": match_id,
            "volunteer": chosen_vol.get("full_name") if chosen_vol else "UNASSIGNED",
            "transport": chosen_trans.get("name") if chosen_trans else "None (Volunteer Handover)",
            "transport_mode": transport_mode,
            "route": route_summary,
            "distance_km": dist_km,
            "transit_mins": transit_mins,
            "cost": delivery_cost,
            "pickup_time": pickup_time.isoformat(),
        })

    from database import log_agent_action
    log_agent_action("agent3", "create_assignments", "donation", state["donation_id"],
                     output_s=f"{len(assignment_ids)} assignments ({', '.join(a['transport_mode'] for a in assignment_details)})")

    state.update({
        "assignment_ids": assignment_ids,
        "assignment_details": assignment_details,
        "errors": state.get("errors", []),
    })
    return state


# ─────────────────────────────────────────────
# AGENT 4 — Delivery Tracking & Impact
# ─────────────────────────────────────────────

def agent4_delivery_impact(state: AnnaSetu_State) -> AnnaSetu_State:
    from tools import get_assignments, get_deliveries, generate_impact_report, alert_admin
    from guardrails import check_iteration_limit

    state = dict(state)
    state["current_agent"] = "agent4"
    state["iterations"] = state.get("iterations", 0) + 1

    ok, msg = check_iteration_limit(state["iterations"])
    if not ok:
        state["errors"] = state.get("errors", []) + [msg]
        return state

    assignment_ids = state.get("assignment_ids", [])
    delivery_ids   = []

    from tools import execute_query as _eq
    for aid in assignment_ids:
        rows = _eq("SELECT id FROM as_deliveries WHERE assignment_id=:aid", {"aid": aid})
        delivery_ids.extend(r["id"] for r in rows)

    # Check for delayed deliveries
    now = datetime.now(timezone.utc)
    for aid in assignment_ids:
        from tools import get_assignment
        assignment = get_assignment(aid)
        if not assignment:
            continue
        sched = assignment.get("pickup_time_scheduled")
        if sched and isinstance(sched, str):
            try:
                sched = datetime.fromisoformat(sched.replace("Z", "+00:00"))
            except Exception:
                sched = None
        if sched and sched < now and assignment.get("status") == "assigned":
            alert_admin(f"Assignment #{aid} overdue — pickup not yet confirmed", "assignment", aid)

    # Generate impact report from confirmed DB records
    report = generate_impact_report()

    # Optionally generate narrative with Gemini
    if _ai_status["gemini_available"] and report.get("confirmed_meals", 0) > 0:
        prompt = (
            f"Generate a 2-sentence impact summary for Anna Setu Karnataka food rescue platform:\n"
            f"Confirmed meals redistributed: {report.get('confirmed_meals',0)}\n"
            f"Organisations served: {report.get('orgs_served',0)}\n"
            f"Volunteers engaged: {report.get('volunteers_engaged',0)}\n"
            f"Keep it warm, factual and community-focused."
        )
        narrative, mdl = llm_call(prompt, prefer="gemini", max_tokens=120)
        if narrative:
            report["narrative"] = narrative
            report["narrative_model"] = mdl

    from database import log_agent_action
    log_agent_action("agent4", "delivery_tracking_impact", "donation", state["donation_id"],
                     output_s=f"deliveries={len(delivery_ids)}, meals={report.get('confirmed_meals',0)}")

    state.update({
        "delivery_ids": delivery_ids,
        "impact_report": report,
        "workflow_complete": True,
        "errors": state.get("errors", []),
    })
    return state


# ─────────────────────────────────────────────
# CONDITIONAL ROUTING
# ─────────────────────────────────────────────

def route_after_agent1(state: AnnaSetu_State) -> str:
    if state.get("workflow_complete"):
        return "end"
    result = state.get("screening_result", "")
    if result == "eligible":
        return "agent2"
    elif result == "pending_review":
        return "human_review"
    else:
        return "end"  # blocked


def route_after_agent2(state: AnnaSetu_State) -> str:
    if state.get("workflow_complete"):
        return "end"
    if state.get("errors"):
        return "end"
    return "wait_approval"   # human must approve before agent3


def route_after_approval(state: AnnaSetu_State) -> str:
    return "agent3"


def route_after_agent3(state: AnnaSetu_State) -> str:
    if state.get("workflow_complete"):
        return "end"
    if not state.get("assignment_ids"):
        return "end"
    return "agent4"


# ─────────────────────────────────────────────
# BUILD LANGGRAPH
# ─────────────────────────────────────────────

def build_workflow():
    from langgraph.graph import StateGraph, END

    builder = StateGraph(AnnaSetu_State)

    builder.add_node("agent1", agent1_donation_safety)
    builder.add_node("agent2", agent2_matching_priority)
    builder.add_node("agent3", agent3_logistics)
    builder.add_node("agent4", agent4_delivery_impact)

    # Human-in-the-loop nodes are lightweight pass-throughs
    # (actual review happens via admin UI; these log the pause)
    def human_review_node(state):
        s = dict(state)
        from database import log_agent_action
        log_agent_action("system", "human_review_pause", "donation", s.get("donation_id"),
                         output_s="Awaiting human safety review")
        s["workflow_complete"] = True  # pause — resume manually
        return s

    def wait_approval_node(state):
        s = dict(state)
        from database import log_agent_action
        log_agent_action("system", "admin_approval_pause", "donation", s.get("donation_id"),
                         output_s="Awaiting admin match approval")
        s["workflow_complete"] = True  # pause — resume manually
        return s

    builder.add_node("human_review", human_review_node)
    builder.add_node("wait_approval", wait_approval_node)

    builder.set_entry_point("agent1")

    builder.add_conditional_edges("agent1", route_after_agent1, {
        "agent2": "agent2",
        "human_review": "human_review",
        "end": END,
    })
    builder.add_conditional_edges("agent2", route_after_agent2, {
        "wait_approval": "wait_approval",
        "end": END,
    })
    builder.add_edge("wait_approval", END)
    builder.add_edge("human_review", END)
    builder.add_conditional_edges("agent3", route_after_agent3, {
        "agent4": "agent4",
        "end": END,
    })
    builder.add_edge("agent4", END)

    return builder.compile()


_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow


def run_donation_workflow(donation_id: int) -> AnnaSetu_State:
    """Entry point: run the full agent pipeline for a donation."""
    wf = get_workflow()
    initial_state: AnnaSetu_State = {
        "donation_id":       donation_id,
        "screening_result":  "",
        "safety_record_id":  0,
        "safety_issues":     "",
        "proposed_matches":  [],
        "match_ids":         [],
        "approval_requested": False,
        "assignment_ids":    [],
        "assignment_details": [],
        "delivery_ids":      [],
        "impact_report":     {},
        "current_agent":     "",
        "errors":            [],
        "human_review_needed": False,
        "iterations":        0,
        "workflow_complete": False,
        "model_used":        "rules",
    }
    result = wf.invoke(initial_state)
    return result


def run_logistics_workflow(donation_id: int, match_ids: list[int]) -> dict:
    """Resume from agent3 after admin approval."""
    state: AnnaSetu_State = {
        "donation_id":        donation_id,
        "screening_result":   "eligible",
        "safety_record_id":   0,
        "safety_issues":      "",
        "proposed_matches":   [],
        "match_ids":          match_ids,
        "approval_requested": True,
        "assignment_ids":     [],
        "assignment_details": [],
        "delivery_ids":       [],
        "impact_report":      {},
        "current_agent":      "",
        "errors":             [],
        "human_review_needed": False,
        "iterations":         0,
        "workflow_complete":  False,
        "model_used":         "rules",
    }
    state = agent3_logistics(state)
    if not state.get("workflow_complete"):
        state = agent4_delivery_impact(state)
    return state


# ─────────────────────────────────────────────
# PHASE 2: RECIPIENT EMERGENCY WORKFLOW (STILL 4 AGENTS)
# ─────────────────────────────────────────────

class RecipientEmergencyState(TypedDict):
    request_data:            dict
    request_id:              int
    urgency_level:           str
    urgency_reason:          str
    validation_passed:       bool
    donor_matches:           list[dict]
    donor_match_found:       bool
    discovered_organisations: list[dict]
    general_contacts:        list[dict]
    fallback_triggered:      bool
    banner_message:          str
    errors:                  list[str]
    model_used:              str
    current_agent:           str
    iterations:              int


def agent1_recipient_intake(state: RecipientEmergencyState) -> RecipientEmergencyState:
    """Agent 1: Recipient Request Intake & Urgency Determination."""
    import guardrails as g
    import tools as t
    from database import log_agent_action

    state = dict(state)
    state["current_agent"] = "agent1"
    state["iterations"] = state.get("iterations", 0) + 1
    t0 = time.time()

    req_data = state["request_data"]

    # Compute deterministic urgency first (rules guarantee prompt injection cannot alter urgency)
    urgency, reason = g.calculate_deterministic_urgency(
        req_data.get("required_by_time"),
        req_data.get("special_needs", ""),
        req_data.get("urgency_level", "Normal")
    )
    state["urgency_level"] = urgency
    state["urgency_reason"] = reason

    valid, errors = g.validate_recipient_request_input(req_data)
    if not valid:
        state["validation_passed"] = False
        state["errors"] = errors
        return state

    state["validation_passed"] = True

    # Register request in database
    try:
        rid = t.register_recipient_request(
            locality=req_data["locality"],
            food_category=req_data["food_category"],
            quantity=int(req_data["quantity"]),
            people_count=int(req_data["people_count"]),
            required_by_time=req_data["required_by_time"],
            urgency_level=urgency,
            urgency_reason=reason,
            special_needs=req_data.get("special_needs", ""),
            requester_name=req_data.get("requester_name"),
            requester_phone=req_data.get("requester_phone"),
            user_id=req_data.get("user_id"),
            is_anonymous=req_data.get("is_anonymous", True),
        )
        state["request_id"] = rid
    except Exception as e:
        log.warning(f"Failed to persist recipient request: {e}")
        state["request_id"] = 0

    duration = int((time.time() - t0) * 1000)
    log_agent_action(
        "agent1",
        "recipient_request_intake",
        "recipient_request",
        state.get("request_id"),
        input_s=f"locality={req_data.get('locality')}, qty={req_data.get('quantity')}",
        output_s=f"urgency={urgency}; reason={reason}",
        model="rules",
        success=True,
        duration_ms=duration
    )
    return state


def agent2_donor_search(state: RecipientEmergencyState) -> RecipientEmergencyState:
    """Agent 2: Search active donor offers matching request constraints."""
    import tools as t
    from database import log_agent_action

    state = dict(state)
    state["current_agent"] = "agent2"
    t0 = time.time()

    req_data = state["request_data"]
    donor_matches = t.get_active_donor_matches_for_request(
        locality=req_data["locality"],
        food_category=req_data["food_category"],
        quantity=int(req_data["quantity"]),
        city=req_data.get("city", "Bengaluru")
    )

    if donor_matches:
        state["donor_matches"] = donor_matches
        state["donor_match_found"] = True
        state["fallback_triggered"] = False
        state["banner_message"] = "Active donor offers found matching your request criteria."
    else:
        state["donor_matches"] = []
        state["donor_match_found"] = False

    duration = int((time.time() - t0) * 1000)
    log_agent_action(
        "agent2",
        "search_active_donor_offers",
        "recipient_request",
        state.get("request_id"),
        input_s=f"loc={req_data.get('locality')}, cat={req_data.get('food_category')}",
        output_s=f"matches_found={len(donor_matches)}",
        model="rules",
        success=True,
        duration_ms=duration
    )
    return state


def route_after_donor_search(state: RecipientEmergencyState) -> Literal["donor_matched_end", "agent2_org_discovery"]:
    """LangGraph conditional edge: donor match found? -> yes: finish / no: run org discovery inside Agent 2."""
    if state.get("donor_match_found"):
        return "donor_matched_end"
    return "agent2_org_discovery"


def agent2_org_discovery(state: RecipientEmergencyState) -> RecipientEmergencyState:
    """Agent 2: Organisation Discovery Fallback when NO active donor matches exist."""
    import tools as t
    from database import log_agent_action

    state = dict(state)
    state["current_agent"] = "agent2"
    t0 = time.time()
    req_data = state["request_data"]
    include_demo = req_data.get("include_demo", False)

    # Hard banner requirement:
    # "No suitable active donor match was found for your request. Here are existing food-support organisations you can contact."
    state["banner_message"] = (
        "No suitable active donor match was found for your request. "
        "Here are existing food-support organisations you can contact."
    )
    state["fallback_triggered"] = True

    orgs = t.discover_support_organisations(
        locality=req_data["locality"],
        food_category=req_data["food_category"],
        urgency_level=state.get("urgency_level", "Normal"),
        city=req_data.get("city", "Bengaluru"),
        include_demo=include_demo,
        limit=10
    )

    if orgs:
        # Grounded LLM explanation enrichment if available
        model_used = "rules"
        if _ai_status["granite_available"] or _ai_status["gemini_available"]:
            try:
                top_org = orgs[0]
                facts = f"Name: {top_org['organisation_name']}, Locality: {top_org.get('locality')}, Food services: {top_org.get('food_services')}, Availability: {top_org.get('availability_status')}"
                prompt = (
                    f"Given only these factual organization details from PostgreSQL:\n{facts}\n"
                    f"Explain in one sentence why this organization can be contacted for a food request in {req_data['locality']}. "
                    f"DO NOT invent any address, phone number, website, or availability."
                )
                explanation, mdl = llm_call(prompt, prefer="granite", max_tokens=100)
                if explanation and not any(bad in explanation.lower() for bad in ["http", "phone", "91"]):
                    top_org["llm_explanation"] = explanation
                    model_used = mdl
            except Exception as e:
                log.warning(f"LLM explanation enrichment failed: {e}")

        state["discovered_organisations"] = orgs
        state["model_used"] = model_used
    else:
        # Honest message if no organisation matched + verified general contacts
        state["discovered_organisations"] = []
        state["banner_message"] = (
            "No verified food support organisation match was found in our directory for this specific criteria. "
            "Please reach out directly to verified national and state support helplines below."
        )
        state["general_contacts"] = t.get_general_support_contacts()
        state["model_used"] = "rules"

    duration = int((time.time() - t0) * 1000)
    log_agent_action(
        "agent2",
        "emergency_organisation_discovery",
        "recipient_request",
        state.get("request_id"),
        input_s=f"loc={req_data.get('locality')}, cat={req_data.get('food_category')}",
        output_s=f"discovered={len(orgs)}",
        model=state["model_used"],
        success=True,
        duration_ms=duration
    )
    return state


def build_recipient_discovery_workflow():
    """Build LangGraph StateGraph for Recipient Emergency Food Discovery."""
    from langgraph.graph import StateGraph, END

    builder = StateGraph(RecipientEmergencyState)

    builder.add_node("agent1_intake", agent1_recipient_intake)
    builder.add_node("agent2_donor_search", agent2_donor_search)
    builder.add_node("agent2_org_discovery", agent2_org_discovery)

    def donor_matched_end_node(state):
        return state

    builder.add_node("donor_matched_end", donor_matched_end_node)

    builder.set_entry_point("agent1_intake")
    builder.add_edge("agent1_intake", "agent2_donor_search")
    builder.add_conditional_edges("agent2_donor_search", route_after_donor_search, {
        "donor_matched_end": "donor_matched_end",
        "agent2_org_discovery": "agent2_org_discovery",
    })
    builder.add_edge("donor_matched_end", END)
    builder.add_edge("agent2_org_discovery", END)

    return builder.compile()


_recipient_workflow = None


def get_recipient_workflow():
    global _recipient_workflow
    if _recipient_workflow is None:
        _recipient_workflow = build_recipient_discovery_workflow()
    return _recipient_workflow


def run_recipient_emergency_workflow(request_data: dict, include_demo: bool = False) -> RecipientEmergencyState:
    """Entry point for recipient food support discovery (LangGraph executed)."""
    wf = get_recipient_workflow()
    req = dict(request_data)
    req["include_demo"] = include_demo
    initial_state: RecipientEmergencyState = {
        "request_data":            req,
        "request_id":              0,
        "urgency_level":           "Normal",
        "urgency_reason":          "",
        "validation_passed":       False,
        "donor_matches":           [],
        "donor_match_found":       False,
        "discovered_organisations": [],
        "general_contacts":        [],
        "fallback_triggered":      False,
        "banner_message":          "",
        "errors":                  [],
        "model_used":              "rules",
        "current_agent":           "",
        "iterations":              0,
    }
    return wf.invoke(initial_state)



# ─────────────────────────────────────────────
# STARTUP INIT
# ─────────────────────────────────────────────

def initialise_agents():
    """Call once at app startup."""
    _init_gemini()
    _init_granite()
    log.info(f"AI status: {_ai_status}")
