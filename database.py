"""
Anna Setu Karnataka — Database Layer
PostgreSQL schema creation, seed data, and parameterised query helpers.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Any

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column,
    Integer, String, Text, Boolean, Numeric, DateTime,
    ForeignKey, UniqueConstraint, Index, event
)
from sqlalchemy.exc import IntegrityError

load_dotenv()
log = logging.getLogger("annasetu.db")

_DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not _DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment")

# Force sslmode=require on Neon
engine = create_engine(
    _DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "require"} if "neon" in _DATABASE_URL else {},
)

metadata = MetaData()

# ─────────────────────────────────────────────
# TABLE DEFINITIONS
# ─────────────────────────────────────────────

users_table = Table("as_users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(80), nullable=False),
    Column("password_hash", String(200), nullable=False),
    Column("role", String(20), nullable=False),          # donor | recipient | volunteer | admin
    Column("full_name", String(120)),
    Column("email", String(120)),
    Column("phone", String(20)),
    Column("org_id", Integer, nullable=True),            # links to donor/recipient org
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    UniqueConstraint("username", name="uq_as_users_username"),
)

donor_orgs_table = Table("as_donor_orgs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(120), nullable=False),
    Column("org_type", String(60)),                      # restaurant | hotel | wedding_hall | canteen
    Column("address", String(300)),
    Column("city", String(60)),
    Column("contact_name", String(120)),
    Column("contact_phone", String(20)),
    Column("fssai_number", String(40)),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

recipient_orgs_table = Table("as_recipient_orgs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(120), nullable=False),
    Column("org_type", String(60)),                      # shelter | orphanage | old_age_home | community_kitchen | ngo
    Column("address", String(300)),
    Column("city", String(60)),
    Column("contact_name", String(120)),
    Column("contact_phone", String(20)),
    Column("capacity_meals_per_day", Integer, default=50),
    Column("dietary_restrictions", String(200)),         # vegetarian | vegan | halal | jain
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

recipient_requirements_table = Table("as_recipient_requirements", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("org_id", Integer, ForeignKey("as_recipient_orgs.id"), nullable=False),
    Column("food_category", String(60)),                 # cooked_meals | raw_produce | bakery | dairy | beverages
    Column("dietary_pref", String(60)),                  # vegetarian | vegan | halal | any
    Column("quantity_needed", Integer),
    Column("unit", String(20), default="meals"),
    Column("frequency", String(40), default="daily"),
    Column("notes", Text),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

donations_table = Table("as_donations", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("donor_org_id", Integer, ForeignKey("as_donor_orgs.id"), nullable=False),
    Column("donor_user_id", Integer, ForeignKey("as_users.id"), nullable=False),
    Column("food_name", String(200), nullable=False),
    Column("food_category", String(60), nullable=False),
    Column("dietary_type", String(60)),                  # vegetarian | non_vegetarian | vegan | jain
    Column("quantity", Integer, nullable=False),
    Column("unit", String(20), default="meals"),
    Column("preparation_time", DateTime(timezone=True)),
    Column("pickup_deadline", DateTime(timezone=True)),
    Column("location", String(300)),
    Column("city", String(60)),
    Column("packaging", String(60)),                     # sealed | open | bulk
    Column("storage_condition", String(60)),             # ambient | refrigerated | frozen
    Column("allergen_info", Text),
    Column("notes", Text),
    Column("status", String(30), default="pending_screening"),
    # statuses: pending_screening | screening_passed | screening_failed |
    #           pending_review | matched | collected | delivered | cancelled
    Column("is_demo", Boolean, default=False),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

food_safety_records_table = Table("as_food_safety", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("donation_id", Integer, ForeignKey("as_donations.id"), nullable=False),
    Column("screening_result", String(30)),              # eligible | pending_review | blocked
    Column("safety_score", Numeric(4, 2)),
    Column("issues_found", Text),
    Column("recommendations", Text),
    Column("screened_by", String(60), default="agent1"),
    Column("model_used", String(60)),
    Column("human_reviewed", Boolean, default=False),
    Column("reviewer_notes", Text),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

donation_matches_table = Table("as_donation_matches", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("donation_id", Integer, ForeignKey("as_donations.id"), nullable=False),
    Column("recipient_org_id", Integer, ForeignKey("as_recipient_orgs.id"), nullable=False),
    Column("allocated_quantity", Integer, nullable=False),
    Column("match_score", Numeric(5, 2)),
    Column("match_reason", Text),
    Column("status", String(30), default="proposed"),
    # statuses: proposed | admin_approved | admin_rejected | volunteer_assigned | collected | delivered | failed
    Column("approved_by_user_id", Integer, nullable=True),
    Column("approved_at", DateTime(timezone=True), nullable=True),
    Column("is_demo", Boolean, default=False),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    UniqueConstraint("donation_id", "recipient_org_id", name="uq_match_donation_recipient"),
)

volunteers_table = Table("as_volunteers", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("as_users.id"), nullable=True),
    Column("full_name", String(120), nullable=False),
    Column("phone", String(20)),
    Column("city", String(60)),
    Column("address", String(300)),
    Column("vehicle_type", String(40)),                  # bike | car | van | tempo | none
    Column("vehicle_capacity_meals", Integer, default=0),
    Column("is_available", Boolean, default=True),
    Column("is_active", Boolean, default=True),
    Column("is_demo", Boolean, default=False),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

transport_providers_table = Table("as_transport_providers", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(120), nullable=False),
    Column("vehicle_type", String(40)),
    Column("capacity_meals", Integer),
    Column("city", String(60)),
    Column("contact_phone", String(20)),
    Column("is_available", Boolean, default=True),
    Column("cost_per_trip", Numeric(8, 2), default=0),
    Column("is_demo", Boolean, default=False),
)

collection_assignments_table = Table("as_collection_assignments", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("match_id", Integer, ForeignKey("as_donation_matches.id"), nullable=False),
    Column("volunteer_id", Integer, ForeignKey("as_volunteers.id"), nullable=True),
    Column("transport_provider_id", Integer, ForeignKey("as_transport_providers.id"), nullable=True),
    Column("pickup_time_scheduled", DateTime(timezone=True)),
    Column("pickup_time_actual", DateTime(timezone=True)),
    Column("pickup_location", String(300)),
    Column("delivery_location", String(300)),
    Column("status", String(30), default="assigned"),
    # assigned | accepted | picked_up | in_transit | delivered | delayed | failed | cancelled
    Column("volunteer_accepted", Boolean, default=False),
    Column("notes", Text),
    Column("is_demo", Boolean, default=False),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

deliveries_table = Table("as_deliveries", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("assignment_id", Integer, ForeignKey("as_collection_assignments.id"), nullable=False),
    Column("match_id", Integer, ForeignKey("as_donation_matches.id"), nullable=False),
    Column("status", String(30), default="assigned"),
    Column("pickup_at", DateTime(timezone=True)),
    Column("delivered_at", DateTime(timezone=True)),
    Column("expected_quantity", Integer),
    Column("actual_quantity", Integer),
    Column("recipient_acknowledged", Boolean, default=False),
    Column("acknowledgement_at", DateTime(timezone=True)),
    Column("acknowledgement_notes", Text),
    Column("failure_reason", Text),
    Column("is_demo", Boolean, default=False),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

human_approvals_table = Table("as_human_approvals", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("entity_type", String(40)),                  # donation | match | assignment | delivery
    Column("entity_id", Integer, nullable=False),
    Column("reason", String(300)),
    Column("status", String(20), default="pending"),    # pending | approved | rejected
    Column("requested_by", String(60)),
    Column("reviewed_by_user_id", Integer, nullable=True),
    Column("review_notes", Text),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("resolved_at", DateTime(timezone=True), nullable=True),
)

agent_logs_table = Table("as_agent_logs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("agent_name", String(40)),
    Column("action", String(100)),
    Column("entity_type", String(40)),
    Column("entity_id", Integer, nullable=True),
    Column("input_summary", Text),
    Column("output_summary", Text),
    Column("model_used", String(60)),
    Column("success", Boolean, default=True),
    Column("error_message", Text),
    Column("duration_ms", Integer),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

audit_logs_table = Table("as_audit_logs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=True),
    Column("username", String(80)),
    Column("role", String(20)),
    Column("action", String(100)),
    Column("entity_type", String(40)),
    Column("entity_id", Integer, nullable=True),
    Column("details", Text),
    Column("ip_address", String(45)),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

# ─────────────────────────────────────────────
# PHASE 2 TABLES: Emergency Food Support Discovery
# ─────────────────────────────────────────────

support_organisations_table = Table("support_organisations", metadata,
    Column("organisation_id", Integer, primary_key=True, autoincrement=True),
    Column("organisation_name", String(255), nullable=False),
    Column("organisation_type", String(60), nullable=False), # food_bank | food_rescue_org | ngo | community_kitchen | shelter | orphanage | old_age_home | food_redistribution_org
    Column("address", Text, nullable=True),
    Column("locality", String(120), nullable=True),
    Column("city", String(60), default="Bengaluru"),
    Column("pincode", String(20), nullable=True),
    Column("latitude", Numeric(10, 7), nullable=True),
    Column("longitude", Numeric(10, 7), nullable=True),
    Column("contact_phone", String(60), nullable=True),
    Column("contact_email", String(120), nullable=True),
    Column("website_url", Text, nullable=True),
    Column("food_services", Text, nullable=True),
    Column("food_categories_supported", Text, nullable=True),
    Column("beneficiary_type", String(120), nullable=True),
    Column("operating_hours", String(120), nullable=True),
    Column("service_description", Text, nullable=True),
    Column("source_name", String(150), nullable=False),
    Column("source_url", Text, nullable=False),
    Column("last_verified_at", DateTime(timezone=True), nullable=True),
    Column("verification_status", String(40), default="listed_in_source"), # listed_in_source | contact_confirmed | unverified
    Column("availability_status", String(40), default="unknown"),         # unknown | contact_to_confirm | confirmed_available | temporarily_unavailable
    Column("can_distribute_food", Boolean, default=False),
    Column("is_beneficiary_institution", Boolean, default=False),
    Column("is_synthetic", Boolean, default=False),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    UniqueConstraint("source_name", "organisation_name", "address", name="uq_support_org_source_nat"),
    Index("idx_support_org_locality", "locality"),
    Index("idx_support_org_type", "organisation_type"),
    Index("idx_support_org_active_dist", "is_active", "can_distribute_food"),
)

recipient_contact_log_table = Table("recipient_contact_log", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("request_id", Integer, nullable=True),
    Column("organisation_id", Integer, ForeignKey("support_organisations.organisation_id"), nullable=False),
    Column("action", String(40), nullable=False), # viewed | called | emailed | visited_website | opened_directions | marked_contacted
    Column("outcome", String(40), nullable=True), # got_help | no_answer | not_available | other
    Column("details", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

general_support_contacts_table = Table("general_support_contacts", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("contact_name", String(120), nullable=False),
    Column("contact_type", String(60), nullable=True),
    Column("phone", String(40), nullable=False),
    Column("description", Text, nullable=True),
    Column("source_name", String(120), nullable=False),
    Column("source_url", Text, nullable=False),
    Column("last_verified_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    UniqueConstraint("phone", "contact_name", name="uq_gen_supp_phone_name"),
)

recipient_requests_table = Table("recipient_requests", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("as_users.id"), nullable=True),
    Column("requester_name", String(120), nullable=True),
    Column("requester_phone", String(30), nullable=True),
    Column("locality", String(120), nullable=False),
    Column("city", String(60), default="Bengaluru"),
    Column("food_category", String(60), nullable=False), # cooked_meals | raw_produce | bakery | dairy | packaged | any
    Column("quantity", Integer, nullable=False),
    Column("people_count", Integer, nullable=False),
    Column("required_by_time", DateTime(timezone=True), nullable=False),
    Column("urgency_level", String(20), nullable=False), # Normal | Urgent | Critical
    Column("urgency_reason", Text, nullable=False),
    Column("special_needs", Text, nullable=True),
    Column("status", String(30), default="submitted"), # submitted | donor_matched | referred_to_org | fulfilled | cancelled
    Column("is_anonymous", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)


# ─────────────────────────────────────────────
# SCHEMA INIT
# ─────────────────────────────────────────────

def init_schema():
    """Create all tables if they don't exist. Safe to call on every startup."""
    metadata.create_all(engine, checkfirst=True)
    log.info("Schema initialised (checkfirst=True — no data dropped)")


def get_conn():
    return engine.connect()


# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def get_user_by_username(username: str) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, username, password_hash, role, full_name, email, org_id FROM as_users WHERE username = :u AND is_active = TRUE"),
            {"u": username}
        ).mappings().fetchone()
        return dict(row) if row else None


def authenticate(username: str, password: str) -> dict | None:
    user = get_user_by_username(username)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


# ─────────────────────────────────────────────
# GENERIC HELPERS
# ─────────────────────────────────────────────

def execute_query(sql: str, params: dict | None = None) -> list[dict]:
    """Read-only parameterised query."""
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params or {}).mappings().fetchall()
        return [dict(r) for r in rows]


def execute_write(sql: str, params: dict | None = None) -> int:
    """Write parameterised query, returns rowcount."""
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        conn.commit()
        return result.rowcount


def insert_row(table_name: str, data: dict) -> int:
    """Insert a row and return generated id."""
    cols = ", ".join(data.keys())
    vals = ", ".join(f":{k}" for k in data.keys())
    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({vals}) RETURNING id"
    with engine.connect() as conn:
        row = conn.execute(text(sql), data).fetchone()
        conn.commit()
        return row[0] if row else -1


def log_agent_action(agent: str, action: str, entity_type: str = "", entity_id: int | None = None,
                     input_s: str = "", output_s: str = "", model: str = "", success: bool = True,
                     error: str = "", duration_ms: int = 0):
    try:
        insert_row("as_agent_logs", {
            "agent_name": agent, "action": action, "entity_type": entity_type,
            "entity_id": entity_id, "input_summary": input_s[:500], "output_summary": output_s[:500],
            "model_used": model, "success": success, "error_message": error[:300], "duration_ms": duration_ms,
            "created_at": datetime.now(timezone.utc)
        })
    except Exception as e:
        log.warning(f"Agent log write failed: {e}")


def log_audit(user_id: int | None, username: str, role: str, action: str,
              entity_type: str = "", entity_id: int | None = None, details: str = ""):
    try:
        insert_row("as_audit_logs", {
            "user_id": user_id, "username": username, "role": role,
            "action": action, "entity_type": entity_type, "entity_id": entity_id,
            "details": details[:500], "created_at": datetime.now(timezone.utc)
        })
    except Exception as e:
        log.warning(f"Audit log write failed: {e}")


# ─────────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────────

DEMO_USERS = [
    {"username": "donor_raj",    "password": "Demo@1234", "role": "donor",     "full_name": "Rajesh Kumar",    "email": "raj@example.com"},
    {"username": "donor_priya",  "password": "Demo@1234", "role": "donor",     "full_name": "Priya Sharma",    "email": "priya@example.com"},
    {"username": "recipient_hope","password":"Demo@1234", "role": "recipient", "full_name": "Hope Foundation",  "email": "hope@example.com"},
    {"username": "volunteer_arjun","password":"Demo@1234","role": "volunteer", "full_name": "Arjun Nair",      "email": "arjun@example.com"},
    {"username": "admin",        "password": "Admin@1234","role": "admin",     "full_name": "Platform Admin",  "email": "admin@annasetu.in"},
]

def seed_demo_data():
    """Idempotent seed — skips rows that already exist."""
    with engine.connect() as conn:
        # Users
        user_ids = {}
        for u in DEMO_USERS:
            existing = conn.execute(text("SELECT id FROM as_users WHERE username=:u"), {"u": u["username"]}).fetchone()
            if existing:
                user_ids[u["username"]] = existing[0]
                continue
            ph = hash_password(u["password"])
            row = conn.execute(text(
                "INSERT INTO as_users (username,password_hash,role,full_name,email,is_active,created_at) "
                "VALUES (:u,:ph,:r,:fn,:em,TRUE,:ca) RETURNING id"
            ), {"u": u["username"], "ph": ph, "r": u["role"], "fn": u["full_name"],
                "em": u["email"], "ca": datetime.now(timezone.utc)}).fetchone()
            user_ids[u["username"]] = row[0]

        # Donor orgs
        donor_org_ids = {}
        donor_orgs = [
            {"name": "Royal Orchid Wedding Hall",   "org_type": "wedding_hall", "address": "Indiranagar, Bengaluru", "city": "Bengaluru", "contact_name": "Rajesh Kumar",   "contact_phone": "9876543210", "fssai_number": "FSSAI-KA-001"},
            {"name": "Spice Garden Restaurant",     "org_type": "restaurant",   "address": "Koramangala, Bengaluru", "city": "Bengaluru", "contact_name": "Priya Sharma",    "contact_phone": "9876543211", "fssai_number": "FSSAI-KA-002"},
            {"name": "Tech Park Canteen ITPL",      "org_type": "canteen",      "address": "Whitefield, Bengaluru",  "city": "Bengaluru", "contact_name": "Suresh Babu",     "contact_phone": "9876543212", "fssai_number": "FSSAI-KA-003"},
        ]
        for d in donor_orgs:
            existing = conn.execute(text("SELECT id FROM as_donor_orgs WHERE name=:n"), {"n": d["name"]}).fetchone()
            if existing:
                donor_org_ids[d["name"]] = existing[0]
            else:
                row = conn.execute(text(
                    "INSERT INTO as_donor_orgs (name,org_type,address,city,contact_name,contact_phone,fssai_number,is_active,created_at) "
                    "VALUES (:name,:org_type,:address,:city,:contact_name,:contact_phone,:fssai_number,TRUE,:ca) RETURNING id"
                ), {**d, "ca": datetime.now(timezone.utc)}).fetchone()
                donor_org_ids[d["name"]] = row[0]

        # Link donor users to donor orgs
        for uname, oname in [("donor_raj", "Royal Orchid Wedding Hall"), ("donor_priya", "Spice Garden Restaurant")]:
            conn.execute(text("UPDATE as_users SET org_id=:oid WHERE username=:u"), {"oid": donor_org_ids[oname], "u": uname})

        # Recipient orgs
        recip_org_ids = {}
        recip_orgs = [
            {"name": "Asha Shelter Home",        "org_type": "shelter",           "address": "Jayanagar 4th Block, Bengaluru", "city": "Bengaluru", "contact_name": "Meena Devi",     "contact_phone": "9876543220", "capacity_meals_per_day": 70,  "dietary_restrictions": "vegetarian"},
            {"name": "Bal Sangama Orphanage",    "org_type": "orphanage",         "address": "MG Road, Bengaluru",             "city": "Bengaluru", "contact_name": "Father Thomas",  "contact_phone": "9876543221", "capacity_meals_per_day": 50,  "dietary_restrictions": "vegetarian"},
            {"name": "Vruddha Niwas Old Age Home","org_type":"old_age_home",      "address": "Mysuru Road, Bengaluru",         "city": "Bengaluru", "contact_name": "Dr. Anitha Rao", "contact_phone": "9876543222", "capacity_meals_per_day": 40,  "dietary_restrictions": "vegetarian"},
            {"name": "Anna Dasoha Community Kitchen","org_type":"community_kitchen","address":"Hubballi",                     "city": "Hubballi",   "contact_name": "Ravi Kumar",     "contact_phone": "9876543223", "capacity_meals_per_day": 200, "dietary_restrictions": "any"},
        ]
        for d in recip_orgs:
            existing = conn.execute(text("SELECT id FROM as_recipient_orgs WHERE name=:n"), {"n": d["name"]}).fetchone()
            if existing:
                recip_org_ids[d["name"]] = existing[0]
            else:
                row = conn.execute(text(
                    "INSERT INTO as_recipient_orgs (name,org_type,address,city,contact_name,contact_phone,capacity_meals_per_day,dietary_restrictions,is_active,created_at) "
                    "VALUES (:name,:org_type,:address,:city,:contact_name,:contact_phone,:capacity_meals_per_day,:dietary_restrictions,TRUE,:ca) RETURNING id"
                ), {**d, "ca": datetime.now(timezone.utc)}).fetchone()
                recip_org_ids[d["name"]] = row[0]

        # Link recipient user to org
        conn.execute(text("UPDATE as_users SET org_id=:oid WHERE username=:u"),
                     {"oid": recip_org_ids["Asha Shelter Home"], "u": "recipient_hope"})

        # Recipient requirements
        reqs = [
            {"org_id": recip_org_ids["Asha Shelter Home"],         "food_category": "cooked_meals", "dietary_pref": "vegetarian", "quantity_needed": 70,  "unit": "meals"},
            {"org_id": recip_org_ids["Bal Sangama Orphanage"],     "food_category": "cooked_meals", "dietary_pref": "vegetarian", "quantity_needed": 50,  "unit": "meals"},
            {"org_id": recip_org_ids["Vruddha Niwas Old Age Home"],"food_category": "cooked_meals", "dietary_pref": "vegetarian", "quantity_needed": 40,  "unit": "meals"},
            {"org_id": recip_org_ids["Anna Dasoha Community Kitchen"],"food_category":"cooked_meals","dietary_pref": "any",       "quantity_needed": 200, "unit": "meals"},
        ]
        for r in reqs:
            existing = conn.execute(text("SELECT id FROM as_recipient_requirements WHERE org_id=:oid"), {"oid": r["org_id"]}).fetchone()
            if not existing:
                conn.execute(text(
                    "INSERT INTO as_recipient_requirements (org_id,food_category,dietary_pref,quantity_needed,unit,frequency,updated_at) "
                    "VALUES (:org_id,:food_category,:dietary_pref,:quantity_needed,:unit,'daily',:ua)"
                ), {**r, "ua": datetime.now(timezone.utc)})

        # Volunteers
        vol_ids = {}
        volunteers = [
            {"full_name": "Arjun Nair",     "phone": "9900001111", "city": "Bengaluru", "address": "Indiranagar",    "vehicle_type": "bike",  "vehicle_capacity_meals": 20,  "user_id": user_ids.get("volunteer_arjun")},
            {"full_name": "Kavya Reddy",    "phone": "9900002222", "city": "Bengaluru", "address": "Koramangala",    "vehicle_type": "car",   "vehicle_capacity_meals": 50},
            {"full_name": "Manjunath B S",  "phone": "9900003333", "city": "Bengaluru", "address": "Whitefield",     "vehicle_type": "van",   "vehicle_capacity_meals": 100},
            {"full_name": "Deepika Murthy", "phone": "9900004444", "city": "Bengaluru", "address": "Jayanagar",      "vehicle_type": "bike",  "vehicle_capacity_meals": 20},
        ]
        for v in volunteers:
            existing = conn.execute(text("SELECT id FROM as_volunteers WHERE full_name=:fn"), {"fn": v["full_name"]}).fetchone()
            if existing:
                vol_ids[v["full_name"]] = existing[0]
            else:
                uid = v.pop("user_id", None)
                row = conn.execute(text(
                    "INSERT INTO as_volunteers (full_name,phone,city,address,vehicle_type,vehicle_capacity_meals,user_id,is_available,is_active,is_demo,created_at) "
                    "VALUES (:full_name,:phone,:city,:address,:vehicle_type,:vehicle_capacity_meals,:user_id,TRUE,TRUE,TRUE,:ca) RETURNING id"
                ), {**v, "user_id": uid, "ca": datetime.now(timezone.utc)}).fetchone()
                vol_ids[v["full_name"]] = row[0]

        # Transport providers
        transports = [
            {"name": "City Cargo Tempo",        "vehicle_type": "tempo",  "capacity_meals": 300, "city": "Bengaluru", "contact_phone": "9800001111", "is_available": True, "cost_per_trip": 0},
            {"name": "Quick Rider Two-Wheeler",  "vehicle_type": "bike",   "capacity_meals": 30,  "city": "Bengaluru", "contact_phone": "9800002222", "is_available": True, "cost_per_trip": 0},
        ]
        for t in transports:
            existing = conn.execute(text("SELECT id FROM as_transport_providers WHERE name=:n"), {"n": t["name"]}).fetchone()
            if not existing:
                conn.execute(text(
                    "INSERT INTO as_transport_providers (name,vehicle_type,capacity_meals,city,contact_phone,is_available,cost_per_trip,is_demo) "
                    "VALUES (:name,:vehicle_type,:capacity_meals,:city,:contact_phone,:is_available,:cost_per_trip,TRUE)"
                ), t)

        # Seed Phase 2 support organisations & helplines
        try:
            from seed_organisations import seed_all
            seed_all()
        except Exception as e:
            log.warning(f"Support organisations seeding check failed: {e}")

        conn.commit()
    log.info("Seed data loaded (idempotent)")
    return user_ids, donor_org_ids, recip_org_ids, vol_ids
