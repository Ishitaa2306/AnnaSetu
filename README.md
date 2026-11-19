# Anna Setu Karnataka (ಅನ್ನ ಸೇತು ಕರ್ನಾಟಕ)
### Intelligent Agentic Food Rescue Coordination & Emergency Food Support Discovery Platform

---

## 📌 Executive Summary

**Anna Setu Karnataka** is a production-grade multi-agent platform designed to bridge surplus food from commercial donors (hotels, wedding halls, restaurants, canteens) to vulnerable communities, orphanages, shelters, and old-age homes across Bengaluru and Karnataka.

In **Phase 2**, Anna Setu was extended with **Emergency Food Support Discovery**: an emergency lifeline that works even when **zero active food donors** are registered on the platform. Any recipient or citizen in urgent need can find immediate, verified food assistance without waiting for a donor match, with full source attribution, transparent ranking, and strict availability honesty rules.

---

## 🚀 Key Phase 2 Features

### 1. Two Public Entry Points (Usable Without Login)
- **🚨 Find Immediate Food Support:** An urgent request intake form that accepts location, category, headcount, time window, and vulnerability context. It assigns deterministic urgency, searches active donor offers first, and if none exist, seamlessly discovers and ranks verified local food support organizations.
- **🔍 Explore Food Support Organisations:** An open, browsable directory of verified food banks, community kitchens, redistribution networks, and beneficiary institutions in Bengaluru with filters for locality, organization type, food category, availability status, and keyword search.

### 2. Emergency Fallback Flow
1. Recipient submits an emergency requirement.
2. **Agent 1** validates input against security guardrails and assigns deterministic urgency (*Critical*, *Urgent*, *Normal*).
3. **Agent 2** searches active donor offers satisfying dietary, safety, and quantity constraints.
4. If suitable donor offers exist, they are displayed first.
5. If **NONE** exist, Agent 2 immediately triggers PostgreSQL organization discovery and renders the required banner:
   > **"No suitable active donor match was found for your request. Here are existing food-support organisations you can contact."**
6. Shows ranked cards with **Call (`tel:`)**, **Email (`mailto:`)**, **Website**, and **Directions (Google Maps)** actions.
7. Recipient can record *"I contacted this organisation"*, logging the outcome into the audit trail.

### 3. Strict Honesty Rules (Zero Hallucination Guarantee)
- **Referral ≠ Guarantee:** Cards clearly state referrals are not food guarantees.
- **Availability Labeling:** Unless `availability_status = 'confirmed_available'`, cards display:
  > **"Availability not confirmed — contact organisation"**
- **Beneficiary Segregation:** Partner beneficiary institutions (`is_beneficiary_institution = true`, `can_distribute_food = false`) never appear as food provider results in emergency recommendations.
- **Verified Emergency Helplines:** If no local organization matches, the system displays verified national and state helplines:
  - **112** — National Emergency Response Support System (ERS)
  - **1098** — CHILDLINE (Children in crisis)
  - **14567** — Elderline (National Helpline for Senior Citizens)
  - **104** — Karnataka Arogya Sahayavani (Health Helpline)

---

## 🤖 Four-Agent Architecture (LangGraph)

The platform strictly maintains **exactly four specialized agents**:

| Agent | Responsibilities | Phase 2 Extension |
|---|---|---|
| **Agent 1: Donation & Food Safety** | FSSAI-guided safety screening, allergen checks, shelf-life verification | Handles recipient emergency request intake, field validation, and deterministic urgency scoring. |
| **Agent 2: Recipient Matching & Priority** | Dietary matching, capacity allocation, donor-to-recipient scoring | Active donor offer search first; fallback to PostgreSQL organization discovery tool when zero donors exist. |
| **Agent 3: Collection & Logistics** | Volunteer dispatch, vehicle capacity matching, pickup route planning | Unchanged. |
| **Agent 4: Delivery Tracking & Impact** | Delivery acknowledgement, audit logging, impact reporting | Tracks recipient-initiated referrals alongside deliveries. |

### Deterministic Urgency Rules (Configurable Product Rules)
- **CRITICAL:** Food needed within **3 hours**, OR request indicates vulnerable groups (children, elderly, sick) have no meal today.
- **URGENT:** Food needed within **12 hours**.
- **NORMAL:** All other standard requests.
- *Rule-based calculation cannot be downgraded by LLMs or prompt injection.*

---

## 📊 Provenance Dataset (`data/organisations.csv`)

Built directly from real provenance sources:
1. **Bangalore Food Bank Partner Directory:** 34 beneficiary institutions with real names, addresses, localities, and beneficiary counts.
2. **India Food Sharing Alliance (FSSAI) Karnataka Directory:** Real redistributors and food banks (Feeding India, Robin Hood Army, Rays of Hope Hennur, Rise Against Hunger, Roti Ghar, IFBN, Vidyaranya).
3. **Bangalore Food Bank HQ:** Food Rescue & Feeding program head office in Yelahanka.
4. **3 Fictional Demo Records:** Clearly badged with `is_synthetic = true` and `DEMO DATA — not a real organisation`, excluded from real emergency recommendations.

### Dataset Breakdown
- **Total Records:** 45
- **Real Records:** 42 (8 Food Providers/Distributors, 34 Beneficiary Institutions)
- **Synthetic Demo Records:** 3
- **Records with Direct Phone / Email:** 11 real contact numbers / emails (Zero fabricated contacts)
- **Verified Date:** 2026-11-19

---

## 🗄️ Database Schema Additions (Additive & Safe)

1. `support_organisations`: Holds directory of food support providers and beneficiary NGOs.
2. `recipient_contact_log`: Logs recipient contact attempts (*viewed*, *called*, *emailed*, *directions*, *marked_contacted*).
3. `general_support_contacts`: Verified emergency numbers (112, 1098, 14567, 104).
4. `recipient_requests`: Stores emergency recipient requests (anonymous or registered).

---

## 🛠️ Quick Start & Running Locally

### 1. Environment Setup
```bash
# Clone and enter directory
cd "d:\ibm final"

# Ensure .venv is activated
.\.venv\Scripts\Activate.ps1
```

### 2. Idempotent Seeding
```bash
python seed_organisations.py
```

### 3. Run Automated Phase 2 Test Suite (11 Tests)
```bash
python -m unittest tests/test_phase2.py
```

### 4. Run Phase 1 Regression Smoke Test
```bash
python smoke_test.py
```

### 5. Start the Streamlit Application
```bash
streamlit run app.py
```

---

## 🧪 Automated Test Verification

| Test # | Test Name | Status | Verified Behavior |
|---|---|---|---|
| **1** | Active Donor Match | ✅ PASS | Compatible donor offers are matched first; discovery is bypassed. |
| **2** | No Donor, Organisations Exist | ✅ PASS | Fallback banner displayed, Bangalore Food Bank ranked #1 for Yelahanka Critical request with valid `tel:`, `mailto:`, and Google Maps links. |
| **3** | Preloaded Directory | ✅ PASS | Browse directory without submitting any request (42+ real records). |
| **4** | Multi-Filter Search | ✅ PASS | Filtering by locality, type, food category, and availability status works accurately. |
| **5** | Unknown Availability | ✅ PASS | Card displays strictly *"Availability not confirmed — contact organisation"*. |
| **6** | Honest Fallback (No Match) | ✅ PASS | Non-existent location displays honest no-match message and verified 112, 1098, 14567, 104 helplines. |
| **7** | Duplicate Seed Prevention | ✅ PASS | Running seed multiple times produces identical row count (45 records, 0 duplicates). |
| **8** | System Resilience | ✅ PASS | Graceful fallback on LLM unavailability without application crashes. |
| **9** | Data Integrity | ✅ PASS | Beneficiary NGOs excluded from provider results; demo records excluded from live recommendations. |
| **10** | Security & Prompt Injection | ✅ PASS | SQL injection in search neutralized; prompt injection cannot downgrade urgency. |
| **11** | Phase 1 Regression | ✅ PASS | End-to-end donation screening, matching, and logistics workflows continue to pass. |

---

## 🔑 Demo Credentials

| Role | Username | Password |
|---|---|---|
| **Donor** | `donor_raj` | `Demo@1234` |
| **Donor** | `donor_priya` | `Demo@1234` |
| **Recipient** | `recipient_hope` | `Demo@1234` |
| **Volunteer** | `volunteer_arjun` | `Demo@1234` |
| **Admin** | `admin` | `Admin@1234` |
