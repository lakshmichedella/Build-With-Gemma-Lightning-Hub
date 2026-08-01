import sys
import os

def test_system():
    print("Testing DB and seeding...")
    from db.seed import seed_database
    from db.db import get_all_patients, get_active_queue, get_recent_history
    
    seeded = seed_database()
    print(f"Seed result: {seeded}")
    
    patients = get_all_patients()
    print(f"Total patients in DB: {len(patients)}")
    assert len(patients) >= 10, "Expected at least 10 synthetic patients"
    
    queue = get_active_queue()
    print(f"Active queue count: {len(queue)}")
    assert len(queue) > 0, "Expected active encounters in queue"
    
    print("\nTesting Nurse Reasoning Services...")
    from services.gemma_nurse import extract_entities, summarize_lookback, score_esi_cov
    sample_mist = {
        "chief_complaint": "Crushing chest pain",
        "mechanism": "Acute onset at rest",
        "signs": "Diaphoresis, BP 90/60, HR 115",
        "treatment": "Aspirin 325mg PO"
    }
    
    entities = extract_entities(sample_mist)
    print(f"Extracted entities: {entities}")
    
    history = get_recent_history(patients[0]["id"])
    flags = summarize_lookback(sample_mist, history)
    print(f"Lookback flags: {flags}")
    
    esi_res = score_esi_cov(sample_mist, flags)
    print(f"ESI CoV Result: {esi_res}")
    
    print("\nTesting Doctor Services...")
    from services.gemma_doctor import structure_dictation
    doc_res = structure_dictation("Patient presenting with suspected STEMI. Transfer immediately to cath lab.")
    print(f"Doctor dictation result: {doc_res}")
    
    print("\nTesting App Import...")
    from app import build_app
    app = build_app()
    print("App successfully initialized!")
    print("\n✅ ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_system()
