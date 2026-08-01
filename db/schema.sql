-- T1: minimal FHIR R4-lite schema for the ER handover demo.
-- See .steering/requirements.md §4 for the field-level spec this implements.

CREATE TABLE IF NOT EXISTS patients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    birth_date  TEXT NOT NULL,   -- ISO 8601 date
    gender      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS encounters (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL REFERENCES patients(id),
    status           TEXT NOT NULL,   -- e.g. "active", "finished"
    class            TEXT NOT NULL,   -- e.g. "emergency"
    period_start     TEXT NOT NULL,   -- ISO 8601 datetime
    period_end       TEXT,            -- ISO 8601 datetime, NULL while active
    raw_transcript   TEXT,            -- B1: paramedic's dictated notes
    image_tag        TEXT,            -- B2: PaliGemma visual tag
    structured_mist  TEXT,            -- B3: JSON — Mechanism/Injury/Signs/Treatment/etc.
    esi_score        INTEGER,         -- C3: 1 (most urgent) - 5 (least urgent)
    esi_rationale    TEXT,            -- C3: Chain-of-Verification output (JSON or text)
    assigned_to      TEXT,            -- D2 (stretch): staff member assigned
    doctor_note      TEXT,            -- D3 (stretch): structured dictated note
    suggested_code   TEXT,            -- D3 (stretch): suggested ICD-10-style code
    esi_override_score   INTEGER,     -- nurse override of esi_score, per-encounter; AI's esi_score/esi_rationale stay untouched
    esi_override_reason  TEXT         -- required justification for the override, dictated or typed
);

CREATE TABLE IF NOT EXISTS conditions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id     INTEGER NOT NULL REFERENCES patients(id),
    code           TEXT NOT NULL,   -- text-based / ICD-10-style code
    recorded_date  TEXT NOT NULL    -- ISO 8601 date
);

CREATE TABLE IF NOT EXISTS observations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    encounter_id  INTEGER NOT NULL REFERENCES encounters(id),
    type          TEXT NOT NULL,   -- HR | BP | RR | SpO2 | temp
    value         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS allergies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id  INTEGER NOT NULL REFERENCES patients(id),
    substance   TEXT NOT NULL
);
