# 🎬 Gemma Lightning Hub — Pitch Video Script (2 Minutes)

**Target length:** ~2 Minutes  
**Tool recommended:** Loom, Zoom, or OBS Studio (Record screen + camera in the corner)  
**Preparation:** Open the live Hugging Face Space demo (`localhost:7860` or HF link). Have the "Paramedic Intake" tab ready on Scenario 1 (Acute STEMI).

---

## ⏱️ 0:00 - 0:15 | The Hook & Problem (Visual: Slide 2 - The Clinical Crisis)
**Visual:** Show the Presentation Slide 2 detailing traditional ER handover friction.
**Speaker (Camera On):** 
"Hi everyone, we built the **Gemma Lightning Hub** for the *Build with Gemma: Triage in Light Speed* hackathon. 
Right now, emergency room handovers are chaotic. Paramedics shout out vitals under high stress, nurses scramble to manually type notes, and critical patient history is often lost in translation. This friction delays life-saving care."

## ⏱️ 0:15 - 0:45 | The Paramedic View (Visual: App Tab 1 - Paramedic Intake)
**Visual:** Switch to the live App. Click Tab 1 (Paramedic Intake). Click "Load Scenario 1". Play the audio dictation and point to the uploaded photo.
**Speaker (Screen Recording):** 
"To solve this, we created a single, continuous patient record powered by Gemma that spans across three clinical roles. 
It starts here in the ambulance. A paramedic dictates their handover hands-free and snaps a quick photo of an injury or an EKG. 
*(Click 'Synthesize')*
Within seconds, **Gemini Multimodal Audio** and **Gemma Vision** work together to structure this chaotic raw data into a standardized MIST grid, extracting exactly what the hospital needs before the ambulance even arrives."

## ⏱️ 0:45 - 1:15 | The Nurse View & ESI CoV (Visual: App Tab 2 - Nurse Review)
**Visual:** Switch to Tab 2 (Nurse Review). Click "Run Lookback & Triager". Highlight the extracted entities and the 3-Step CoV reasoning.
**Speaker:** 
"Once the patient arrives, the Triage Nurse inherits the exact same digital record. But we don't just stop at data entry. 
Gemma automatically cross-references the patient's last three visits from our FHIR-lite database to flag critical history—like a severe penicillin allergy.
Then, Gemma acts as a clinical reasoning engine. Instead of a black-box AI score, it uses a **3-step Chain of Verification**. It extracts red flags, proposes a preliminary ESI score, actively self-critiques against clinical traps like over-triage, and then outputs a highly verified final Acuity Score."

## ⏱️ 1:15 - 1:45 | The Doctor Queue (Visual: App Tab 3 - Doctor Queue)
**Visual:** Switch to Tab 3 (Doctor Queue). Show the live sorted table. Click "Assess Bedside".
**Speaker:** 
"Finally, the ER Doctor views a live queue, automatically prioritized by Gemma's verified acuity scores.
The doctor can securely assign staffing roles using our simulated RBAC system, dictate their bedside assessment, and instantly have Gemma suggest the correct **ICD-10 billing codes**—closing the loop on the entire patient journey without ever breaking continuity."

## ⏱️ 1:45 - 2:00 | Conclusion & Impact (Visual: Slide 6 - Core Value Proposition)
**Visual:** Switch to Presentation Tab / Slide 6 (Value Prop & Hackathon Alignment).
**Speaker (Camera On):** 
"By keeping data locally isolated on the edge and reducing a 5-minute charting task to 10 seconds, the Gemma Lightning Hub removes the administrative burden from clinicians so they can focus on what matters most: saving patient lives.
Thank you!"

---

### 💡 Video Recording Tips:
- **Pacing:** Speak confidently but don't rush. The script is timed for a relaxed, professional pace.
- **Mouse Clicks:** Make your mouse movements deliberate. Don't wave the cursor around. Point exactly to what you are talking about (e.g., the ESI score).
- **Demo Data:** Pre-load the demo scenarios (using the buttons we built) so you don't have to wait for typing or slow uploads during the video.
