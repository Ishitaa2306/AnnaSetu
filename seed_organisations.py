"""
Anna Setu Karnataka — Support Organisations & General Contacts Seeder
Idempotent seeding from data/organisations.csv into PostgreSQL.
"""

import os
import csv
import logging
from datetime import datetime, timezone
from sqlalchemy import text
import database as db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("annasetu.seed")

GENERAL_CONTACTS = [
    {
        "contact_name": "National Emergency Response System",
        "contact_type": "emergency",
        "phone": "112",
        "description": "All-in-one national emergency helpline for immediate police, fire, and medical crisis response.",
        "source_name": "Ministry of Home Affairs, Govt. of India",
        "source_url": "https://112.gov.in",
        "last_verified_at": datetime.now(timezone.utc),
        "is_active": True,
    },
    {
        "contact_name": "CHILDLINE (Emergency Child Protection)",
        "contact_type": "childline",
        "phone": "1098",
        "description": "Toll-free 24/7 emergency service for children in need of care, protection, and emergency shelter/food assistance.",
        "source_name": "Ministry of Women and Child Development",
        "source_url": "https://wcd.nic.in/childline-1098",
        "last_verified_at": datetime.now(timezone.utc),
        "is_active": True,
    },
    {
        "contact_name": "Elderline (National Helpline for Senior Citizens)",
        "contact_type": "elderline",
        "phone": "14567",
        "description": "Toll-free helpline providing elder care, rescue, shelter referrals, and emergency assistance for senior citizens.",
        "source_name": "Ministry of Social Justice and Empowerment",
        "source_url": "https://elderline.dosje.gov.in",
        "last_verified_at": datetime.now(timezone.utc),
        "is_active": True,
    },
    {
        "contact_name": "Karnataka Arogya Sahayavani (Health Helpline)",
        "contact_type": "health_helpline",
        "phone": "104",
        "description": "Govt of Karnataka 24x7 health helpline providing emergency medical advice, food poisoning reporting, and ambulance support.",
        "source_name": "Health and Family Welfare Dept, Govt of Karnataka",
        "source_url": "https://hfw.karnataka.gov.in",
        "last_verified_at": datetime.now(timezone.utc),
        "is_active": True,
    },
]


def seed_general_contacts():
    """Idempotently seed verified general support contacts."""
    sql = text("""
        INSERT INTO general_support_contacts (
            contact_name, contact_type, phone, description,
            source_name, source_url, last_verified_at, is_active
        ) VALUES (
            :contact_name, :contact_type, :phone, :description,
            :source_name, :source_url, :last_verified_at, :is_active
        )
        ON CONFLICT (phone, contact_name) DO UPDATE SET
            contact_type = EXCLUDED.contact_type,
            description = EXCLUDED.description,
            source_name = EXCLUDED.source_name,
            source_url = EXCLUDED.source_url,
            last_verified_at = EXCLUDED.last_verified_at,
            is_active = EXCLUDED.is_active;
    """)
    with db.engine.connect() as conn:
        for c in GENERAL_CONTACTS:
            conn.execute(sql, c)
        conn.commit()
    log.info(f"Seeded {len(GENERAL_CONTACTS)} general support contacts.")


def seed_support_organisations(csv_path: str = "data/organisations.csv"):
    """Idempotently seed organisations from CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Organisations dataset not found at {csv_path}")

    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "organisation_name": row["organisation_name"].strip(),
                "organisation_type": row["organisation_type"].strip(),
                "address": row["address"].strip() or None,
                "locality": row["locality"].strip() or "Bengaluru Urban",
                "city": row.get("city", "Bengaluru").strip() or "Bengaluru",
                "pincode": row.get("pincode", "").strip() or None,
                "latitude": float(row["latitude"]) if row.get("latitude") else None,
                "longitude": float(row["longitude"]) if row.get("longitude") else None,
                "contact_phone": row.get("contact_phone", "").strip() or None,
                "contact_email": row.get("contact_email", "").strip() or None,
                "website_url": row.get("website_url", "").strip() or None,
                "food_services": row.get("food_services", "").strip() or None,
                "food_categories_supported": row.get("food_categories_supported", "").strip() or None,
                "beneficiary_type": row.get("beneficiary_type", "").strip() or None,
                "operating_hours": row.get("operating_hours", "").strip() or None,
                "service_description": row.get("service_description", "").strip() or None,
                "source_name": row["source_name"].strip(),
                "source_url": row["source_url"].strip(),
                "last_verified_at": datetime.now(timezone.utc),
                "verification_status": row.get("verification_status", "listed_in_source").strip(),
                "availability_status": row.get("availability_status", "unknown").strip(),
                "can_distribute_food": row.get("can_distribute_food", "false").lower() in ("true", "1", "t"),
                "is_beneficiary_institution": row.get("is_beneficiary_institution", "false").lower() in ("true", "1", "t"),
                "is_synthetic": row.get("is_synthetic", "false").lower() in ("true", "1", "t"),
                "is_active": True,
            })

    sql = text("""
        INSERT INTO support_organisations (
            organisation_name, organisation_type, address, locality, city, pincode,
            latitude, longitude, contact_phone, contact_email, website_url,
            food_services, food_categories_supported, beneficiary_type, operating_hours,
            service_description, source_name, source_url, last_verified_at,
            verification_status, availability_status, can_distribute_food,
            is_beneficiary_institution, is_synthetic, is_active, updated_at
        ) VALUES (
            :organisation_name, :organisation_type, :address, :locality, :city, :pincode,
            :latitude, :longitude, :contact_phone, :contact_email, :website_url,
            :food_services, :food_categories_supported, :beneficiary_type, :operating_hours,
            :service_description, :source_name, :source_url, :last_verified_at,
            :verification_status, :availability_status, :can_distribute_food,
            :is_beneficiary_institution, :is_synthetic, :is_active, NOW()
        )
        ON CONFLICT (source_name, organisation_name, address) DO UPDATE SET
            organisation_type = EXCLUDED.organisation_type,
            locality = EXCLUDED.locality,
            city = EXCLUDED.city,
            pincode = EXCLUDED.pincode,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            contact_phone = EXCLUDED.contact_phone,
            contact_email = EXCLUDED.contact_email,
            website_url = EXCLUDED.website_url,
            food_services = EXCLUDED.food_services,
            food_categories_supported = EXCLUDED.food_categories_supported,
            beneficiary_type = EXCLUDED.beneficiary_type,
            operating_hours = EXCLUDED.operating_hours,
            service_description = EXCLUDED.service_description,
            source_url = EXCLUDED.source_url,
            last_verified_at = EXCLUDED.last_verified_at,
            verification_status = EXCLUDED.verification_status,
            availability_status = EXCLUDED.availability_status,
            can_distribute_food = EXCLUDED.can_distribute_food,
            is_beneficiary_institution = EXCLUDED.is_beneficiary_institution,
            is_synthetic = EXCLUDED.is_synthetic,
            is_active = EXCLUDED.is_active,
            updated_at = NOW();
    """)

    with db.engine.connect() as conn:
        for r in records:
            conn.execute(sql, r)
        conn.commit()

    # Query counts for verification
    with db.engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM support_organisations")).scalar()
        real_count = conn.execute(text("SELECT COUNT(*) FROM support_organisations WHERE is_synthetic = FALSE")).scalar()
        syn_count = conn.execute(text("SELECT COUNT(*) FROM support_organisations WHERE is_synthetic = TRUE")).scalar()
        distrib_count = conn.execute(text("SELECT COUNT(*) FROM support_organisations WHERE can_distribute_food = TRUE AND is_synthetic = FALSE")).scalar()
        ben_count = conn.execute(text("SELECT COUNT(*) FROM support_organisations WHERE is_beneficiary_institution = TRUE AND is_synthetic = FALSE")).scalar()

    log.info(f"Support organisations seeded: Total={total} | Real={real_count} | Synthetic={syn_count} | Providers={distrib_count} | Beneficiaries={ben_count}")
    return {
        "total": total,
        "real": real_count,
        "synthetic": syn_count,
        "distributors": distrib_count,
        "beneficiaries": ben_count,
    }


def seed_all():
    db.init_schema()
    seed_general_contacts()
    return seed_support_organisations()


if __name__ == "__main__":
    print("Seeding Anna Setu Karnataka Phase 2 Organisations & Helplines...")
    res = seed_all()
    print("Seed complete:", res)
