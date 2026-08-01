import json
import sqlite3
from db.db import get_connection, init_db

SYNTHETIC_PATIENTS = [
    {
        "id": "P001",
        "name": "Arthur Pendelton",
        "birth_date": "1954-03-12",
        "gender": "Male",
        "conditions": [
            {"id": "COND-101", "code": "I25.10 - Coronary artery disease", "recorded_date": "2023-05-10"},
            {"id": "COND-102", "code": "I10 - Essential hypertension", "recorded_date": "2021-11-04"}
        ],
        "allergies": [
            {"id": "ALG-101", "substance": "Penicillin", "reaction": "Anaphylaxis"}
        ],
        "prior_encounters": [
            {
                "id": "ENC-001-A",
                "status": "completed",
                "period": "2024-01-15",
                "raw_transcript": "Patient presented with mild exertional dyspnea. ECG showed sinus rhythm.",
                "structured_mist": json.dumps({
                    "mechanism": "Exertion while walking stairs",
                    "injury": "None",
                    "signs": "Mild SOB, BP 145/90, HR 82",
                    "treatment": "Sublingual Nitroglycerin given with relief"
                }),
                "esi_score": 3,
                "esi_rationale": "Stable chest pain workup"
            },
            {
                "id": "ENC-001-B",
                "status": "completed",
                "period": "2024-06-20",
                "raw_transcript": "Follow up cardiology consultation for blood pressure adjustment.",
                "structured_mist": json.dumps({
                    "mechanism": "Routine follow up",
                    "injury": "None",
                    "signs": "BP 138/85, HR 74",
                    "treatment": "Adjusted Lisinopril dose"
                }),
                "esi_score": 4,
                "esi_rationale": "Routine hypertension management"
            }
        ],
        "active_encounter": {
            "id": "ENC-001-CURR",
            "raw_transcript": "72-year-old male with sudden onset severe crushing substernal chest pain radiating to left arm and jaw. Profuse diaphoresis, nausea. BP 90/60, HR 115 irregular, SpO2 91% on room air. Aspirin 325mg administered.",
            "structured_mist": {
                "chief_complaint": "Crushing chest pain radiating to left arm and jaw",
                "mechanism": "Sudden onset at rest 30 mins ago",
                "injury": "None acute physical trauma",
                "signs": "Severe diaphoresis, hypotension BP 90/60, HR 115, SpO2 91%",
                "treatment": "Aspirin 325mg PO, Oxygen 2L NC applied",
                "vitals": "BP: 90/60 mmHg | HR: 115 bpm | RR: 24 bpm | SpO2: 91%"
            },
            "image_tag": "diaphoretic, pale, distress",
            "esi_score": 1,
            "esi_rationale": {
                "red_flags": "Hemodynamic instability (BP 90/60), suspected acute STEMI/AMI, hypoxia (SpO2 91%).",
                "prelim_score": 1,
                "critique": "Meets ESI Level 1 immediate life-saving intervention criteria (unstable vitals + acute coronary syndrome).",
                "final_score": 1,
                "rationale": "Requires immediate resuscitation bay entry and cath lab activation."
            }
        }
    },
    {
        "id": "P002",
        "name": "Maria Rodriguez",
        "birth_date": "1981-08-24",
        "gender": "Female",
        "conditions": [
            {"id": "COND-201", "code": "J45.909 - Severe persistent asthma", "recorded_date": "2019-02-14"}
        ],
        "allergies": [
            {"id": "ALG-201", "substance": "Latex", "reaction": "Contact dermatitis"}
        ],
        "prior_encounters": [
            {
                "id": "ENC-002-A",
                "status": "completed",
                "period": "2024-03-10",
                "raw_transcript": "Asthma flare up secondary to upper respiratory tract infection.",
                "structured_mist": json.dumps({
                    "mechanism": "URI trigger",
                    "injury": "None",
                    "signs": "Bilateral wheezing, SpO2 93%",
                    "treatment": "Albuterol nebulizer x2, Oral Prednisone"
                }),
                "esi_score": 2,
                "esi_rationale": "High risk respiratory exacerbation"
            }
        ],
        "active_encounter": {
            "id": "ENC-002-CURR",
            "raw_transcript": "45-year-old female experiencing severe respiratory distress. Unable to speak full sentences. Tachypneic RR 32, SpO2 88% on room air, diffuse inspiratory and expiratory wheezing. Continuous albuterol nebulizer started.",
            "structured_mist": {
                "chief_complaint": "Severe acute asthma exacerbation",
                "mechanism": "Acute onset following allergen exposure",
                "injury": "None",
                "signs": "Tachypnea RR 32, accessory muscle use, SpO2 88%, diffuse wheezing",
                "treatment": "Albuterol/Ipratropium neb in progress, O2 4L NC",
                "vitals": "BP: 135/88 mmHg | HR: 110 bpm | RR: 32 bpm | SpO2: 88%"
            },
            "image_tag": "respiratory distress, tripod position",
            "esi_score": 2,
            "esi_rationale": {
                "red_flags": "SpO2 88%, severe work of breathing, accessory muscle use.",
                "prelim_score": 2,
                "critique": "High risk patient who could deteriorate to respiratory failure rapidly.",
                "final_score": 2,
                "rationale": "High-risk status requiring urgent room placement and continuous monitoring."
            }
        }
    },
    {
        "id": "P003",
        "name": "James Chen",
        "birth_date": "1998-11-03",
        "gender": "Male",
        "conditions": [
            {"id": "COND-301", "code": "K21.9 - Gastro-esophageal reflux disease", "recorded_date": "2022-09-18"}
        ],
        "allergies": [],
        "prior_encounters": [
            {
                "id": "ENC-003-A",
                "status": "completed",
                "period": "2023-11-12",
                "raw_transcript": "Presented with epigastric burning pain relieved by antacids.",
                "structured_mist": json.dumps({
                    "mechanism": "Postprandial pain",
                    "injury": "None",
                    "signs": "Normal vitals",
                    "treatment": "Omeprazole prescribed"
                }),
                "esi_score": 4,
                "esi_rationale": "Non-urgent GERD"
            }
        ],
        "active_encounter": {
            "id": "ENC-003-CURR",
            "raw_transcript": "28-year-old male with 12 hours of progressive right lower quadrant abdominal pain, sharp, migrating from umbilical region. Anorexia, low-grade fever 101.4F. Positive McBurney point tenderness. HR 98, BP 124/78.",
            "structured_mist": {
                "chief_complaint": "Acute right lower quadrant abdominal pain",
                "mechanism": "Migrated from umbilicus over 12h",
                "injury": "None",
                "signs": "McBurney tenderness, Fever 101.4F, Nausea",
                "treatment": "IV line established, NPO status",
                "vitals": "BP: 124/78 mmHg | HR: 98 bpm | RR: 18 bpm | Temp: 101.4 F"
            },
            "image_tag": "abnormally guarded abdominal posture",
            "esi_score": 3,
            "esi_rationale": {
                "red_flags": "Localized RLQ peritonitis signs, fever.",
                "prelim_score": 3,
                "critique": "Requires multiple resources (labs, IV, abdominal CT/US, surgical consult). Vitals are currently stable.",
                "final_score": 3,
                "rationale": "Requires multiple resources for acute appendicitis workup."
            }
        }
    },
    {
        "id": "P004",
        "name": "Sarah Jenkins",
        "birth_date": "1992-04-17",
        "gender": "Female",
        "conditions": [
            {"id": "COND-401", "code": "G43.909 - Migraine without aura", "recorded_date": "2021-07-01"}
        ],
        "allergies": [
            {"id": "ALG-401", "substance": "Ibuprofen", "reaction": "Urticaria / Hives"}
        ],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-004-CURR",
            "raw_transcript": "34-year-old female tripped over dog at home, landed on outstretched left hand. Left wrist swelling and focal anatomical snuffbox tenderness. No skin breakdown, sensation intact, radial pulse 2+. Vitals stable.",
            "structured_mist": {
                "chief_complaint": "Left wrist pain following fall",
                "mechanism": "Mechanical fall onto outstretched hand (FOOSH)",
                "injury": "Left wrist swelling, suspected scaphoid fracture",
                "signs": "Focal tenderness, intact sensation & distal pulses",
                "treatment": "Splint applied, ice pack",
                "vitals": "BP: 118/74 mmHg | HR: 72 bpm | RR: 16 bpm | SpO2: 99%"
            },
            "image_tag": "swollen wrist, localized edema",
            "esi_score": 4,
            "esi_rationale": {
                "red_flags": "None. Neurovascularly intact.",
                "prelim_score": 4,
                "critique": "Needs 1 resource: X-ray of wrist.",
                "final_score": 4,
                "rationale": "Single resource required (X-ray). Vitals completely stable."
            }
        }
    },
    {
        "id": "P005",
        "name": "Robert Taylor",
        "birth_date": "1968-01-30",
        "gender": "Male",
        "conditions": [
            {"id": "COND-501", "code": "E11.9 - Type 2 diabetes mellitus", "recorded_date": "2018-10-15"},
            {"id": "COND-502", "code": "M19.90 - Osteoarthritis, unspecified", "recorded_date": "2020-03-22"}
        ],
        "allergies": [],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-005-CURR",
            "raw_transcript": "58-year-old male ran out of Metformin script 3 days ago. Here requesting prescription refill. Reports mild chronic lumbar stiffness unchanged from baseline. Vitals completely normal.",
            "structured_mist": {
                "chief_complaint": "Medication refill request & chronic back ache",
                "mechanism": "Out of routine prescription",
                "injury": "None acute",
                "signs": "No focal neurological deficits, normal mobility",
                "treatment": "None prior to intake",
                "vitals": "BP: 122/80 mmHg | HR: 68 bpm | RR: 14 bpm | SpO2: 98%"
            },
            "image_tag": "no acute distress",
            "esi_score": 5,
            "esi_rationale": {
                "red_flags": "None.",
                "prelim_score": 5,
                "critique": "Requires zero complex emergency diagnostic resources.",
                "final_score": 5,
                "rationale": "Non-urgent prescription refill."
            }
        }
    },
    {
        "id": "P006",
        "name": "Elena Rostova",
        "birth_date": "1963-09-05",
        "gender": "Female",
        "conditions": [
            {"id": "COND-601", "code": "I48.91 - Unspecified atrial fibrillation", "recorded_date": "2020-08-11"}
        ],
        "allergies": [
            {"id": "ALG-601", "substance": "Sulfa drugs", "reaction": "Severe rash"}
        ],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-006-CURR",
            "raw_transcript": "63-year-old female brought in by EMS with acute neurological deficits starting 45 minutes ago. Left facial droop, left arm motor weakness 2/5, slurred speech (dysarthria). BP 172/96, HR 88 AFib rhythm. Stroke code activated.",
            "structured_mist": {
                "chief_complaint": "Acute stroke symptoms (facial droop, left hemiparesis)",
                "mechanism": "Sudden onset 45m ago while watching TV",
                "injury": "None",
                "signs": "Left facial droop, left arm weakness 2/5, dysarthria, BP 172/96",
                "treatment": "Stroke alert called, IV access established",
                "vitals": "BP: 172/96 mmHg | HR: 88 bpm (irregular) | RR: 18 bpm | SpO2: 97%"
            },
            "image_tag": "facial asymmetry, acute stroke presentation",
            "esi_score": 2,
            "esi_rationale": {
                "red_flags": "Acute stroke within tPA window (<4.5h), severe neurological deficits.",
                "prelim_score": 2,
                "critique": "High-risk time-sensitive emergency requiring immediate CT head & neurology code.",
                "final_score": 2,
                "rationale": "High risk acute ischemic stroke candidate within treatment window."
            }
        }
    },
    {
        "id": "P007",
        "name": "Marcus Vance",
        "birth_date": "2007-06-19",
        "gender": "Male",
        "conditions": [],
        "allergies": [],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-007-CURR",
            "raw_transcript": "19-year-old male driver unrestrained in high-speed rollover MVC. GCS 9 (E2V3M4). Unstable pelvic ring on palpation, active internal bleeding suspected. BP 78/42, HR 142 weak, SpO2 90%. Trauma code green declared.",
            "structured_mist": {
                "chief_complaint": "Major polytrauma post rollover MVC",
                "mechanism": "High-speed unrestrained rollover motor vehicle collision",
                "injury": "Suspected pelvic fracture, internal hemorrhage, head trauma",
                "signs": "Hypotension BP 78/42, Tachycardia 142, GCS 9, pelvic instability",
                "treatment": "Pelvic binder placed, 2 large bore IVs, O-neg blood uncrossed hung",
                "vitals": "BP: 78/42 mmHg | HR: 142 bpm | RR: 28 bpm | SpO2: 90%"
            },
            "image_tag": "pelvic binder, severe trauma, pallor",
            "esi_score": 1,
            "esi_rationale": {
                "red_flags": "Profound hemorrhagic shock (BP 78/42), altered mental status GCS 9, severe trauma.",
                "prelim_score": 1,
                "critique": "Immediate life-saving intervention required (massive transfusion, airway management, trauma surgeon).",
                "final_score": 1,
                "rationale": "ESI Level 1: Hemodynamically unstable polytrauma requiring immediate resuscitation bay."
            }
        }
    },
    {
        "id": "P008",
        "name": "Linda Sterling",
        "birth_date": "1975-02-28",
        "gender": "Female",
        "conditions": [
            {"id": "COND-801", "code": "J44.9 - Chronic obstructive pulmonary disease", "recorded_date": "2017-04-10"}
        ],
        "allergies": [
            {"id": "ALG-801", "substance": "Ciprofloxacin", "reaction": "Tendon pain"}
        ],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-008-CURR",
            "raw_transcript": "51-year-old female with 3 days of worsening fever up to 102.5F, productive cough with rust-colored sputum, right pleuritic chest pain. Crackles heard over right lung base. BP 115/72, HR 102, SpO2 93% on room air.",
            "structured_mist": {
                "chief_complaint": "Fever, productive cough, right pleuritic chest pain",
                "mechanism": "Gradual onset infectious illness over 3 days",
                "injury": "None",
                "signs": "Right base crackles, Fever 102.5F, SpO2 93%",
                "treatment": "Supplemental O2 2L NC",
                "vitals": "BP: 115/72 mmHg | HR: 102 bpm | RR: 22 bpm | Temp: 102.5 F"
            },
            "image_tag": "flushed, febrile distress",
            "esi_score": 3,
            "esi_rationale": {
                "red_flags": "Moderate hypoxemia SpO2 93%, elevated temperature.",
                "prelim_score": 3,
                "critique": "Needs multiple resources (Chest X-ray, blood cultures, IV antibiotics, CBC/BMP). Vitals stable enough for ESI 3.",
                "final_score": 3,
                "rationale": "Community-acquired pneumonia candidate requiring multiple diagnostic and therapeutic resources."
            }
        }
    },
    {
        "id": "P009",
        "name": "David Miller",
        "birth_date": "1986-12-14",
        "gender": "Male",
        "conditions": [],
        "allergies": [],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-009-CURR",
            "raw_transcript": "40-year-old male cut right volar forearm on broken window glass 1 hour ago. 4cm linear laceration, superficial, moderate bleeding now controlled with pressure dressing. Sensation and motor function to hand fully intact.",
            "structured_mist": {
                "chief_complaint": "Laceration right forearm",
                "mechanism": "Accidental cut on broken glass",
                "injury": "4cm linear forearm laceration",
                "signs": "Bleeding controlled with pressure, intact neurovascular exam",
                "treatment": "Pressure dressing applied",
                "vitals": "BP: 126/82 mmHg | HR: 76 bpm | RR: 16 bpm | SpO2: 99%"
            },
            "image_tag": "forearm laceration, pressure bandage",
            "esi_score": 4,
            "esi_rationale": {
                "red_flags": "None. Bleeding controlled, neurovascularly intact.",
                "prelim_score": 4,
                "critique": "Requires 1 resource (suturing / wound repair).",
                "final_score": 4,
                "rationale": "Single resource required (suturing & wound care)."
            }
        }
    },
    {
        "id": "P010",
        "name": "Chloe Bennett",
        "birth_date": "2003-07-22",
        "gender": "Female",
        "conditions": [],
        "allergies": [],
        "prior_encounters": [],
        "active_encounter": {
            "id": "ENC-010-CURR",
            "raw_transcript": "23-year-old female presents with 2 days of dysuria, urinary frequency and urgency. Denies flank pain, chills, or fever. Afebrile, vitals entirely normal.",
            "structured_mist": {
                "chief_complaint": "Dysuria and urinary frequency",
                "mechanism": "2 day onset lower UTI symptoms",
                "injury": "None",
                "signs": "No CVA tenderness, afebrile",
                "treatment": "None prior to intake",
                "vitals": "BP: 112/70 mmHg | HR: 68 bpm | RR: 14 bpm | Temp: 98.4 F"
            },
            "image_tag": "no acute distress",
            "esi_score": 5,
            "esi_rationale": {
                "red_flags": "None. No fever, no systemic symptoms.",
                "prelim_score": 5,
                "critique": "Needs point-of-care urinalysis / simple prescription.",
                "final_score": 5,
                "rationale": "Uncomplicated dysuria suitable for rapid clinic/discharge track."
            }
        }
    }
]

def seed_database(db_path: str = None) -> bool:
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        count = cursor.fetchone()["count"]
        if count > 0:
            return False  # Already seeded
        
        for p in SYNTHETIC_PATIENTS:
            cursor.execute(
                "INSERT INTO patients (id, name, birth_date, gender) VALUES (?, ?, ?, ?)",
                (p["id"], p["name"], p["birth_date"], p["gender"])
            )
            
            for cond in p.get("conditions", []):
                cursor.execute(
                    "INSERT INTO conditions (id, patient_id, code, recorded_date) VALUES (?, ?, ?, ?)",
                    (cond["id"], p["id"], cond["code"], cond["recorded_date"])
                )
                
            for alg in p.get("allergies", []):
                cursor.execute(
                    "INSERT INTO allergies (id, patient_id, substance, reaction) VALUES (?, ?, ?, ?)",
                    (alg["id"], p["id"], alg["substance"], alg.get("reaction", ""))
                )
                
            for pe in p.get("prior_encounters", []):
                cursor.execute(
                    """INSERT INTO encounters (id, patient_id, status, period, raw_transcript, structured_mist, esi_score, esi_rationale)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (pe["id"], p["id"], pe["status"], pe.get("period"), pe.get("raw_transcript"),
                     pe.get("structured_mist"), pe.get("esi_score"), pe.get("esi_rationale"))
                )
                
            active = p.get("active_encounter")
            if active:
                mist_str = json.dumps(active["structured_mist"]) if isinstance(active["structured_mist"], dict) else active["structured_mist"]
                rationale_str = json.dumps(active["esi_rationale"]) if isinstance(active["esi_rationale"], dict) else active["esi_rationale"]
                cursor.execute(
                    """INSERT INTO encounters (id, patient_id, status, raw_transcript, structured_mist, image_tag, esi_score, esi_rationale)
                       VALUES (?, ?, 'active', ?, ?, ?, ?, ?)""",
                    (active["id"], p["id"], active.get("raw_transcript"), mist_str,
                     active.get("image_tag"), active.get("esi_score"), rationale_str)
                )
                
        conn.commit()
        return True
    finally:
        conn.close()

if __name__ == "__main__":
    seeded = seed_database()
    print(f"Database seeding complete! Newly seeded: {seeded}")
