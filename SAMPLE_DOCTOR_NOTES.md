# Sample Doctor Assessment Notes & ICD-10 Coding for ER Triage Demo

Use these 5 clinical doctor assessment notes during judging or live testing in the **Doctor Execution Tab**. Each scenario corresponds to the matching paramedic handover scenario in [`SAMPLE_HANDOVER_NOTES.md`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/SAMPLE_HANDOVER_NOTES.md).

---

### 🚨 1. High Acuity — Acute STEMI / Cardiac Event (ESI Level 1)
**Patient:** 74-year-old male with acute chest pain

**Copy-Pasteable Doctor Dictation Note:**
```text
Patient evaluated in resuscitation bay. 74-year-old male presenting with acute anterior ST-elevation myocardial infarction. 12-lead ECG confirms 3mm ST elevation in leads V1 through V4. Heparin IV bolus 5000 units and Ticagrelor 180mg administered immediately. Emergency Cardiology team alerted and patient prepared for emergent transfer to Cardiac Cath Lab for primary percutaneous coronary intervention.
```

*   **Expected Clinical Plan:** Acute STEMI activation, Heparin/Ticagrelor administration, Cath Lab transfer.
*   **Expected ICD-10 Code:** `I21.09` (Acute transmural myocardial infarction of anterior wall)

---

### ⚠️ 2. High Risk — Severe Asthma Exacerbation (ESI Level 2)
**Patient:** 42-year-old female with acute severe respiratory distress

**Copy-Pasteable Doctor Dictation Note:**
```text
42-year-old female presenting with acute severe asthma attack in status asthmaticus. Administered IV Methylprednisolone 125mg, continuous duo-neb (Ipratropium-Albuterol) nebulizer therapy, and 2g IV Magnesium Sulfate over 20 minutes. Patient placed on High-Flow Nasal Cannula at 30L/min. ABG shows mild compensated respiratory acidosis. Patient admitted to Step-Down ICU unit.
```

*   **Expected Clinical Plan:** IV Corticosteroids, continuous nebulizers, IV Magnesium, HFNC, ICU step-down admission.
*   **Expected ICD-10 Code:** `J45.901` (Unspecified asthma with acute exacerbation)

---

### 📋 3. Moderate Acuity — Acute Suspected Appendicitis (ESI Level 3)
**Patient:** 26-year-old male with right lower quadrant pain

**Copy-Pasteable Doctor Dictation Note:**
```text
26-year-old male evaluated for progressive right lower quadrant abdominal pain with positive McBurney's point tenderness and rebound rigidity. Placed on strict NPO status. Ordered STAT contrast-enhanced CT of abdomen and pelvis, IV Ondansetron 4mg for emesis, IV Morphine 4mg for pain control, and pre-op IV Cefoxitin 2g. General Surgery consult called for urgent evaluation.
```

*   **Expected Clinical Plan:** Abdominal CT scan, NPO, analgesia, antiemetics, pre-op IV antibiotics, surgical consult.
*   **Expected ICD-10 Code:** `K35.80` (Unspecified acute appendicitis)

---

### 🦴 4. Lower Acuity — Traumatic Wrist Injury (ESI Level 4)
**Patient:** 31-year-old female after fall onto outstretched hand

**Copy-Pasteable Doctor Dictation Note:**
```text
31-year-old female evaluated for left wrist trauma following fall on ice. 2-view X-ray of left wrist confirms no acute fracture or dislocation. Distal neurovascular status intact with normal capillary refill. Fitted with removable volar wrist splint, advised strict RICE protocol (Rest, Ice, Compression, Elevation), and prescribed Ibuprofen 600mg PRN for pain. Discharged with orthopedic follow-up in 7 days if symptoms persist.
```

*   **Expected Clinical Plan:** Left wrist X-ray (negative for fracture), splinting, NSAIDs, discharge with outpatient orthopedics follow-up.
*   **Expected ICD-10 Code:** `S63.502A` (Unspecified sprain of left wrist, initial encounter)

---

### 🟢 5. Non-Urgent — Simple Prescription Refill / Minor Symptoms (ESI Level 5)
**Patient:** 55-year-old male for Metformin renewal

**Copy-Pasteable Doctor Dictation Note:**
```text
55-year-old male presenting for routine renewal of Metformin for Type 2 Diabetes Mellitus after running out of medication. Patient is asymptomatic with stable baseline chronic low back stiffness. Renewed Metformin 1000mg oral tablets twice daily for 90 days. Counselled on diabetic diet compliance and routine blood glucose monitoring. Discharged home with recommendation for primary care physician follow-up for routine HbA1c lab work.
```

*   **Expected Clinical Plan:** Refill Metformin 1000mg BID, routine diabetic counselling, PCP follow-up.
*   **Expected ICD-10 Code:** `Z76.0` (Encounter for issue of repeat prescription) / `E11.9` (Type 2 diabetes mellitus without complications)

---

## 🎬 How to Demo in the Doctor Tab

1. Open the **Doctor Execution Tab**.
2. Select the patient encounter from the dropdown or click **Refresh Live Queue**.
3. (Optional) Assign an attending or resident doctor using the **Assign Healthcare Staff** dropdown.
4. Copy & paste one of the 5 doctor notes above into the **Doctor Note Transcript** box (or dictate using the microphone).
5. Click **⚡ Structure Note & Suggest ICD-10 Code**.
6. Gemma will structure the clinical assessment/plan and highlight the suggested ICD-10 billing code in a green tag.
