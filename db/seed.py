"""T4: idempotent startup seeding.

Creates tables (if needed) and inserts the T3 synthetic dataset only if
the patients table is empty. Safe to call on every app startup/restart.
"""
from db import db
from db.seed_data import PATIENTS


def seed():
    db.init_db()
    if not db.is_empty():
        return

    for patient in PATIENTS:
        patient_id = db.create_patient(
            name=patient["name"],
            birth_date=patient["birth_date"],
            gender=patient["gender"],
        )

        for substance in patient["allergies"]:
            db.create_allergy(patient_id, substance)

        for enc in patient["prior_encounters"]:
            encounter_id = db.create_encounter(
                patient_id=patient_id,
                status="finished",
                class_="emergency",
                period_start=enc["period_start"],
                period_end=enc["period_end"],
                raw_transcript=enc["chief_complaint"],
            )
            db.update_encounter_esi(encounter_id, enc["esi_score"], None)
            for code, recorded_date in enc["conditions"]:
                db.create_condition(patient_id, code, recorded_date)
            for obs_type, value in enc["observations"]:
                db.create_observation(encounter_id, obs_type, value)

        current = patient["current_encounter"]
        db.create_encounter(
            patient_id=patient_id,
            status="active",
            class_="emergency",
            period_start=current["period_start"],
            raw_transcript=current["raw_transcript"],
        )


if __name__ == "__main__":
    seed()
    print("Seed complete.")
