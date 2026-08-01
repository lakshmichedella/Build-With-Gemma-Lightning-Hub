# Sample Paramedic Handover Notes & Aligned Photos for ER Triage Demo

Use these 5 clinical handover scenarios during judging or live testing. Each scenario includes a copy-pasteable text dictation note paired 1-to-1 with a matching sample photo from [`sample_images/`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images).

---

### 🚨 1. High Acuity — Acute STEMI / Cardiac Event (ESI Level 1)
*📷 Paired Image: [`sample_images/note1_cardiac_diaphoretic.jpg`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images/note1_cardiac_diaphoretic.jpg)*

```text
74-year-old male with sudden onset crushing substernal chest pain radiating to his left shoulder and jaw, started 25 minutes ago while mowing the lawn. Patient is diaphoretic and nauseated. Vitals on scene: Blood Pressure 88 over 54, Heart Rate 118 irregular, Respiratory Rate 24, SpO2 90% on room air. Administered 325mg chewable Aspirin and 2 Liters nasal cannula Oxygen en route. History of hypertension and coronary artery disease.
```

---

### ⚠️ 2. High Risk — Severe Asthma Exacerbation (ESI Level 2)
*📷 Paired Image: [`sample_images/note2_asthma_nebulizer.jpg`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images/note2_asthma_nebulizer.jpg)*

```text
42-year-old female experiencing severe acute shortness of breath and respiratory distress. Patient is sitting in tripod position, speaking in 1 to 2 word sentences. Inspiratory and expiratory wheezing heard throughout both lung fields. SpO2 is 87% on room air, Heart Rate 122, Respiratory Rate 34. Continuous Albuterol nebulizer with 4 Liters Oxygen started 10 minutes ago with minimal improvement. History of severe asthma.
```

---

### 📋 3. Moderate Acuity — Acute Suspected Appendicitis (ESI Level 3)
*📷 Paired Image: [`sample_images/note3_appendicitis_abdomen.jpg`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images/note3_appendicitis_abdomen.jpg)*

```text
26-year-old male presenting with 10 hours of progressive abdominal pain. Pain started around the belly button and migrated to the right lower quadrant, sharp and constant. Patient reports nausea and one episode of non-bilious emesis. Temperature 101.6 Fahrenheit, Blood Pressure 124 over 78, Heart Rate 94, SpO2 99%. Positive McBurney's point tenderness on palpation. Established 18-gauge IV peripheral access.
```

---

### 🦴 4. Lower Acuity — Traumatic Wrist Injury (ESI Level 4)
*📷 Paired Image: [`sample_images/note4_wrist_splint.jpg`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images/note4_wrist_splint.jpg)*

```text
31-year-old female injured her left wrist after slipping on ice and falling onto an outstretched hand 45 minutes ago. Reports moderate localized pain and swelling over the anatomical snuffbox. No open skin breaks or gross deformity. Sensation and motor function in fingers fully intact, radial pulse 2+. Vitals completely stable: BP 118 over 72, HR 68, SpO2 100%. Left wrist immobilizing splint and ice pack applied.
```

---

### 🟢 5. Non-Urgent — Simple Prescription Refill / Minor Symptoms (ESI Level 5)
*📷 Paired Image: [`sample_images/note5_prescription_refill.jpg`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images/note5_prescription_refill.jpg)*

```text
55-year-old male requesting routine prescription renewal for Metformin after running out 2 days ago. Also mentions mild, chronic low back stiffness unchanged from his normal baseline. No neurological deficits, negative straight leg raise. Vitals completely normal: BP 120 over 76, HR 70, SpO2 98%, afebrile.
```

---

## 🎬 How to Demo

1. **Paramedic Intake Tab**:
   - Select patient **+ New Patient** or an existing synthetic patient.
   - Copy & paste one of the text notes above into the transcript box.
   - Drag & drop the corresponding paired image from [`sample_images/`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/sample_images).
   - Click **Generate & Save Handover** to generate the visual tag and color-coded MIST grid.

2. **Nurse Review Tab**:
   - Select the patient and click **Load Patient Record**.
   - Click **Calculate ESI Score with Chain-of-Verification (CoV)** to show Gemma's visible 3-step reasoning.

3. **Doctor Queue Tab**:
   - Click **Refresh Live Queue** to see the patient ranked by ESI level.
   - For bedside dictation and ICD-10 coding, use the corresponding sample doctor's notes in [`SAMPLE_DOCTOR_NOTES.md`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/SAMPLE_DOCTOR_NOTES.md).

