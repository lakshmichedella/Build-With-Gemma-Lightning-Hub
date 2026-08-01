"""T3: synthetic patient content for the demo seed.

All data is fabricated. Do not replace with real patient records.
Each patient has 2-3 prior encounters (with conditions/observations for
lookback) plus one active/current encounter awaiting paramedic intake.
ICD-10-style codes are illustrative text, not validated codes.
"""

PATIENTS = [
    {
        "name": "Ava Thornton",
        "birth_date": "1985-03-14",
        "gender": "female",
        "allergies": ["Penicillin"],
        "prior_encounters": [
            {
                "period_start": "2025-11-02T09:15:00",
                "period_end": "2025-11-02T13:40:00",
                "chief_complaint": "Recurrent migraine with visual aura",
                "conditions": [("G43.109", "2025-11-02")],
                "observations": [("HR", "78"), ("BP", "118/76"), ("SpO2", "99")],
                "esi_score": 4,
            },
            {
                "period_start": "2024-06-20T18:05:00",
                "period_end": "2024-06-20T21:30:00",
                "chief_complaint": "Asthma exacerbation",
                "conditions": [("J45.901", "2024-06-20")],
                "observations": [("HR", "104"), ("RR", "26"), ("SpO2", "93")],
                "esi_score": 3,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T07:20:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Marcus Bellweather",
        "birth_date": "1958-11-02",
        "gender": "male",
        "allergies": [],
        "prior_encounters": [
            {
                "period_start": "2025-09-10T14:00:00",
                "period_end": "2025-09-10T20:15:00",
                "chief_complaint": "Chest pain, ruled out MI",
                "conditions": [("R07.9", "2025-09-10"), ("I10", "2020-02-01")],
                "observations": [("HR", "92"), ("BP", "152/94"), ("SpO2", "97")],
                "esi_score": 2,
            },
            {
                "period_start": "2024-12-01T08:30:00",
                "period_end": "2024-12-01T10:00:00",
                "chief_complaint": "Routine follow-up, hypertension",
                "conditions": [("I10", "2020-02-01")],
                "observations": [("HR", "80"), ("BP", "148/90"), ("SpO2", "98")],
                "esi_score": 5,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T08:05:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Priya Nakamura",
        "birth_date": "1997-07-22",
        "gender": "female",
        "allergies": ["Latex", "Sulfa drugs"],
        "prior_encounters": [
            {
                "period_start": "2025-05-18T11:45:00",
                "period_end": "2025-05-18T13:10:00",
                "chief_complaint": "Ankle sprain, playing soccer",
                "conditions": [("S93.401A", "2025-05-18")],
                "observations": [("HR", "72"), ("BP", "110/70"), ("SpO2", "99")],
                "esi_score": 4,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T07:50:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Diego Alvarez",
        "birth_date": "1972-01-30",
        "gender": "male",
        "allergies": ["Aspirin"],
        "prior_encounters": [
            {
                "period_start": "2025-10-05T22:10:00",
                "period_end": "2025-10-06T04:00:00",
                "chief_complaint": "Diabetic ketoacidosis",
                "conditions": [("E10.10", "2018-04-11")],
                "observations": [("HR", "118"), ("BP", "100/64"), ("SpO2", "96")],
                "esi_score": 2,
            },
            {
                "period_start": "2025-02-14T16:20:00",
                "period_end": "2025-02-14T19:00:00",
                "chief_complaint": "Hypoglycemic episode",
                "conditions": [("E10.649", "2018-04-11")],
                "observations": [("HR", "96"), ("BP", "108/70"), ("SpO2", "98")],
                "esi_score": 3,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T06:55:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Grace Odhiambo",
        "birth_date": "2001-09-09",
        "gender": "female",
        "allergies": [],
        "prior_encounters": [
            {
                "period_start": "2025-07-30T12:00:00",
                "period_end": "2025-07-30T13:20:00",
                "chief_complaint": "Minor laceration, kitchen knife",
                "conditions": [("S61.409A", "2025-07-30")],
                "observations": [("HR", "74"), ("BP", "116/74"), ("SpO2", "99")],
                "esi_score": 4,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T08:30:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Harold Whitfield",
        "birth_date": "1946-05-17",
        "gender": "male",
        "allergies": ["Codeine"],
        "prior_encounters": [
            {
                "period_start": "2025-12-19T03:10:00",
                "period_end": "2025-12-19T09:45:00",
                "chief_complaint": "Fall with hip pain",
                "conditions": [("S72.001A", "2025-12-19"), ("I48.91", "2019-03-05")],
                "observations": [("HR", "88"), ("BP", "134/82"), ("SpO2", "95")],
                "esi_score": 2,
            },
            {
                "period_start": "2025-08-02T10:00:00",
                "period_end": "2025-08-02T11:15:00",
                "chief_complaint": "Atrial fibrillation follow-up",
                "conditions": [("I48.91", "2019-03-05")],
                "observations": [("HR", "112"), ("BP", "128/80"), ("SpO2", "96")],
                "esi_score": 3,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T07:05:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Yuki Tanaka",
        "birth_date": "1990-12-25",
        "gender": "female",
        "allergies": ["Shellfish"],
        "prior_encounters": [
            {
                "period_start": "2025-04-11T19:30:00",
                "period_end": "2025-04-11T21:00:00",
                "chief_complaint": "Allergic reaction, shrimp exposure",
                "conditions": [("T78.1XXA", "2025-04-11")],
                "observations": [("HR", "110"), ("BP", "100/68"), ("SpO2", "94")],
                "esi_score": 2,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T08:15:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Samuel Okafor",
        "birth_date": "1965-08-08",
        "gender": "male",
        "allergies": [],
        "prior_encounters": [
            {
                "period_start": "2025-03-22T07:40:00",
                "period_end": "2025-03-22T09:00:00",
                "chief_complaint": "Lower back strain",
                "conditions": [("M54.50", "2025-03-22")],
                "observations": [("HR", "76"), ("BP", "124/80"), ("SpO2", "98")],
                "esi_score": 5,
            },
            {
                "period_start": "2024-11-14T15:10:00",
                "period_end": "2024-11-14T17:45:00",
                "chief_complaint": "Kidney stone",
                "conditions": [("N20.0", "2024-11-14")],
                "observations": [("HR", "98"), ("BP", "138/88"), ("SpO2", "97")],
                "esi_score": 3,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T06:40:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Isabelle Moreau",
        "birth_date": "2010-02-19",
        "gender": "female",
        "allergies": ["Peanuts"],
        "prior_encounters": [
            {
                "period_start": "2025-06-01T13:25:00",
                "period_end": "2025-06-01T15:00:00",
                "chief_complaint": "High fever, suspected viral infection",
                "conditions": [("R50.9", "2025-06-01")],
                "observations": [("HR", "120"), ("RR", "28"), ("temp", "39.4")],
                "esi_score": 3,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T08:40:00",
            "raw_transcript": None,
        },
    },
    {
        "name": "Robert Kaczmarek",
        "birth_date": "1980-04-03",
        "gender": "male",
        "allergies": ["Ibuprofen"],
        "prior_encounters": [
            {
                "period_start": "2025-01-09T20:50:00",
                "period_end": "2025-01-10T02:30:00",
                "chief_complaint": "Motorcycle collision, multiple trauma",
                "conditions": [("S06.0X0A", "2025-01-09"), ("S22.000A", "2025-01-09")],
                "observations": [("HR", "128"), ("BP", "90/60"), ("SpO2", "91")],
                "esi_score": 1,
            },
            {
                "period_start": "2024-07-04T22:00:00",
                "period_end": "2024-07-05T01:30:00",
                "chief_complaint": "Post-trauma follow-up",
                "conditions": [("S06.0X0A", "2025-01-09")],
                "observations": [("HR", "84"), ("BP", "122/78"), ("SpO2", "98")],
                "esi_score": 4,
            },
        ],
        "current_encounter": {
            "period_start": "2026-08-01T09:00:00",
            "raw_transcript": None,
        },
    },
]
