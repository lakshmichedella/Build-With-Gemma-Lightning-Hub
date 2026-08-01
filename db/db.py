"""T2: SQLite connection helper + CRUD used across all tabs.

Per AGENTS.md architecture conventions: no long-lived connection is held
across Gradio callbacks. Every function here opens its own connection,
does its work, and closes it.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "erhub.sqlite3")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call every startup."""
    with open(SCHEMA_PATH) as f:
        schema = f.read()
    conn = get_conn()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def is_empty():
    conn = get_conn()
    try:
        row = conn.execute("SELECT COUNT(*) AS n FROM patients").fetchone()
        return row["n"] == 0
    finally:
        conn.close()


# ---- patients ----

def create_patient(name, birth_date, gender):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO patients (name, birth_date, gender) VALUES (?, ?, ?)",
            (name, birth_date, gender),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_patient(patient_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_patients():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM patients ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---- encounters ----

def create_encounter(patient_id, status, class_, period_start, period_end=None,
                      raw_transcript=None, image_tag=None, structured_mist=None):
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO encounters
               (patient_id, status, class, period_start, period_end,
                raw_transcript, image_tag, structured_mist)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, status, class_, period_start, period_end,
             raw_transcript, image_tag, structured_mist),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_encounter(encounter_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_encounters_for_patient(patient_id, limit=None):
    conn = get_conn()
    try:
        query = "SELECT * FROM encounters WHERE patient_id = ? ORDER BY period_start DESC"
        params = [patient_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_active_encounters():
    """Active encounters joined with patient name — used by the nurse
    tab's patient picker and as the base of T14's queue query."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT e.*, p.name AS patient_name
               FROM encounters e JOIN patients p ON p.id = e.patient_id
               WHERE e.status = 'active'
               ORDER BY e.period_start ASC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_active_queue():
    """T14: all active-encounter patients ranked by ESI (1 = most urgent).
    Unscored encounters (nurse hasn't triaged yet) sort to the bottom."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT e.id AS encounter_id, e.patient_id, p.name AS patient_name,
                      e.esi_score, e.esi_rationale, e.structured_mist, e.period_start
               FROM encounters e JOIN patients p ON p.id = e.patient_id
               WHERE e.status = 'active'
               ORDER BY CASE WHEN e.esi_score IS NULL THEN 1 ELSE 0 END,
                        e.esi_score ASC, e.period_start ASC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_encounter_transcript(encounter_id, raw_transcript):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE encounters SET raw_transcript = ? WHERE id = ?",
            (raw_transcript, encounter_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_encounter_image_tag(encounter_id, image_tag):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE encounters SET image_tag = ? WHERE id = ?",
            (image_tag, encounter_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_encounter_mist(encounter_id, structured_mist):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE encounters SET structured_mist = ? WHERE id = ?",
            (structured_mist, encounter_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_encounter_esi(encounter_id, esi_score, esi_rationale):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE encounters SET esi_score = ?, esi_rationale = ? WHERE id = ?",
            (esi_score, esi_rationale, encounter_id),
        )
        conn.commit()
    finally:
        conn.close()


# ---- conditions ----

def create_condition(patient_id, code, recorded_date):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO conditions (patient_id, code, recorded_date) VALUES (?, ?, ?)",
            (patient_id, code, recorded_date),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_conditions_for_patient(patient_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM conditions WHERE patient_id = ? ORDER BY recorded_date DESC",
            (patient_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---- observations ----

def create_observation(encounter_id, obs_type, value):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO observations (encounter_id, type, value) VALUES (?, ?, ?)",
            (encounter_id, obs_type, value),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_observations_for_encounter(encounter_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM observations WHERE encounter_id = ?", (encounter_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---- lookback (T11) ----

def get_recent_history(patient_id, n=3):
    """Last n finished encounters (excludes the current active one) plus
    all known conditions/allergies for the patient — the join C2 needs."""
    conn = get_conn()
    try:
        encounters = conn.execute(
            """SELECT * FROM encounters
               WHERE patient_id = ? AND status != 'active'
               ORDER BY period_start DESC LIMIT ?""",
            (patient_id, n),
        ).fetchall()
        conditions = conn.execute(
            "SELECT * FROM conditions WHERE patient_id = ? ORDER BY recorded_date DESC",
            (patient_id,),
        ).fetchall()
        allergies = conn.execute(
            "SELECT * FROM allergies WHERE patient_id = ?", (patient_id,)
        ).fetchall()
        return {
            "encounters": [dict(e) for e in encounters],
            "conditions": [dict(c) for c in conditions],
            "allergies": [dict(a) for a in allergies],
        }
    finally:
        conn.close()


# ---- allergies ----

def create_allergy(patient_id, substance):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO allergies (patient_id, substance) VALUES (?, ?)",
            (patient_id, substance),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_allergies_for_patient(patient_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM allergies WHERE patient_id = ?", (patient_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
