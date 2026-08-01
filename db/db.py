import os
import sqlite3
import json
from pathlib import Path

DEFAULT_DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "er_triage.db"))

def get_connection(db_path: str = None) -> sqlite3.Connection:
    target_path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = None) -> None:
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_file, "r") as f:
        schema_sql = f.read()
    
    conn = get_connection(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

def get_all_patients(db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_patient(patient_id: str, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_patient(patient_id: str, name: str, birth_date: str, gender: str, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients (id, name, birth_date, gender) VALUES (?, ?, ?, ?)",
            (patient_id, name, birth_date, gender)
        )
        conn.commit()
        return patient_id
    finally:
        conn.close()

def create_encounter(patient_id: str, raw_transcript: str = "", image_tag: str = "", encounter_id: str = None, db_path: str = None):
    import uuid
    enc_id = encounter_id or f"ENC-{uuid.uuid4().hex[:8].upper()}"
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO encounters (id, patient_id, raw_transcript, image_tag, status)
               VALUES (?, ?, ?, ?, 'active')""",
            (enc_id, patient_id, raw_transcript, image_tag)
        )
        conn.commit()
        return enc_id
    finally:
        conn.close()

def update_encounter_mist(encounter_id: str, structured_mist: dict, db_path: str = None):
    mist_json = json.dumps(structured_mist) if isinstance(structured_mist, dict) else structured_mist
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE encounters SET structured_mist = ? WHERE id = ?",
            (mist_json, encounter_id)
        )
        conn.commit()
    finally:
        conn.close()

def update_encounter_image_tag(encounter_id: str, image_tag: str, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE encounters SET image_tag = ? WHERE id = ?",
            (image_tag, encounter_id)
        )
        conn.commit()
    finally:
        conn.close()

def update_encounter_esi(encounter_id: str, esi_score: int, esi_rationale: dict, db_path: str = None):
    rationale_json = json.dumps(esi_rationale) if isinstance(esi_rationale, dict) else esi_rationale
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE encounters SET esi_score = ?, esi_rationale = ? WHERE id = ?",
            (esi_score, rationale_json, encounter_id)
        )
        conn.commit()
    finally:
        conn.close()

def update_encounter_doctor_note(encounter_id: str, doctor_note: str, suggested_code: str = "", db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE encounters SET doctor_note = ?, suggested_code = ? WHERE id = ?",
            (doctor_note, suggested_code, encounter_id)
        )
        conn.commit()
    finally:
        conn.close()

def assign_staff(encounter_id: str, staff_name: str, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE encounters SET assigned_to = ? WHERE id = ?",
            (staff_name, encounter_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_encounter(encounter_id: str, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.*, p.name as patient_name, p.birth_date, p.gender
               FROM encounters e
               JOIN patients p ON e.patient_id = p.id
               WHERE e.id = ?""",
            (encounter_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_latest_encounter_for_patient(patient_id: str, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.*, p.name as patient_name, p.birth_date, p.gender
               FROM encounters e
               JOIN patients p ON e.patient_id = p.id
               WHERE e.patient_id = ? AND e.status = 'active'
               ORDER BY e.created_at DESC LIMIT 1""",
            (patient_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_recent_history(patient_id: str, limit: int = 3, db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        
        # Conditions
        cursor.execute("SELECT * FROM conditions WHERE patient_id = ? ORDER BY recorded_date DESC", (patient_id,))
        conditions = [dict(r) for r in cursor.fetchall()]
        
        # Allergies
        cursor.execute("SELECT * FROM allergies WHERE patient_id = ?", (patient_id,))
        allergies = [dict(r) for r in cursor.fetchall()]
        
        # Prior Encounters
        cursor.execute(
            """SELECT * FROM encounters 
               WHERE patient_id = ? AND status = 'completed'
               ORDER BY created_at DESC LIMIT ?""",
            (patient_id, limit)
        )
        prior_encounters = [dict(r) for r in cursor.fetchall()]
        
        return {
            "conditions": conditions,
            "allergies": allergies,
            "prior_encounters": prior_encounters
        }
    finally:
        conn.close()

def get_active_queue(db_path: str = None):
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.id as encounter_id, e.esi_score, p.id as patient_id, p.name as patient_name,
                      p.birth_date, p.gender, e.structured_mist, e.raw_transcript, e.image_tag,
                      e.assigned_to, e.created_at
               FROM encounters e
               JOIN patients p ON e.patient_id = p.id
               WHERE e.status = 'active'
               ORDER BY CASE WHEN e.esi_score IS NULL THEN 99 ELSE e.esi_score END ASC, e.created_at ASC"""
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
