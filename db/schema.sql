-- ER Handover Triage - Minimal FHIR R4 SQLite Schema

CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS encounters (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    encounter_class TEXT NOT NULL DEFAULT 'EMER',
    period TEXT,
    raw_transcript TEXT,
    structured_mist TEXT, -- JSON string: {mechanism, injury, signs, treatment, chief_complaint, vitals}
    esi_score INTEGER,    -- 1 (most urgent) to 5 (least urgent)
    esi_rationale TEXT,   -- JSON string: {red_flags, prelim_score, critique, final_score, rationale}
    image_tag TEXT,
    doctor_note TEXT,
    suggested_code TEXT,
    assigned_to TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS conditions (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    code TEXT NOT NULL,         -- e.g. "I10 - Essential hypertension", "E11 - Type 2 diabetes mellitus"
    recorded_date TEXT NOT NULL,
    clinical_status TEXT DEFAULT 'active',
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'HR', 'BP', 'RR', 'SpO2', 'Temp'
    value TEXT NOT NULL, -- e.g. '110 bpm', '140/90 mmHg', '94%'
    FOREIGN KEY (encounter_id) REFERENCES encounters(id)
);

CREATE TABLE IF NOT EXISTS allergies (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    substance TEXT NOT NULL, -- e.g. "Penicillin", "Latex", "Sulfa"
    reaction TEXT,           -- e.g. "Anaphylaxis", "Rash"
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
