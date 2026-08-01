import json
import gradio as gr
from db.db import get_all_patients, create_patient, create_encounter, update_encounter_mist, update_encounter_image_tag
from services.stt import transcribe_speech
from services.gemma_vision import tag_image
from services.gemma_intake import synthesize_mist

def format_mist_html(mist_dict: dict, image_tag: str = "") -> str:
    """Formats MIST dict into a beautiful, color-coded clinical grid HTML card."""
    cc = mist_dict.get("chief_complaint", "N/A")
    mech = mist_dict.get("mechanism", "N/A")
    inj = mist_dict.get("injury", "N/A")
    signs = mist_dict.get("signs", "N/A")
    treat = mist_dict.get("treatment", "N/A")
    vitals = mist_dict.get("vitals", "N/A")
    
    html = f"""
    <div style="background-color: #0f172a; border-radius: 12px; padding: 20px; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
            <h3 style="margin: 0; color: #38bdf8; font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                🚑 Structured MIST Handover Grid
            </h3>
            {"<span style='background: #3b82f6; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>" + image_tag + "</span>" if image_tag else ""}
        </div>
        
        <div style="margin-bottom: 14px; background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #38bdf8;">
            <span style="font-weight: 700; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">Chief Complaint</span>
            <div style="color: #f1f5f9; font-size: 1rem; font-weight: 600; margin-top: 4px;">{cc}</div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #a855f7;">
                <span style="font-weight: 700; color: #c084fc; font-size: 0.85rem; text-transform: uppercase;">Mechanism (M)</span>
                <div style="color: #e2e8f0; font-size: 0.95rem; margin-top: 4px;">{mech}</div>
            </div>
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">
                <span style="font-weight: 700; color: #f87171; font-size: 0.85rem; text-transform: uppercase;">Injury / Findings (I)</span>
                <div style="color: #e2e8f0; font-size: 0.95rem; margin-top: 4px;">{inj}</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #eab308;">
                <span style="font-weight: 700; color: #fde047; font-size: 0.85rem; text-transform: uppercase;">Signs & Symptoms (S)</span>
                <div style="color: #e2e8f0; font-size: 0.95rem; margin-top: 4px;">{signs}</div>
            </div>
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #22c55e;">
                <span style="font-weight: 700; color: #4ade80; font-size: 0.85rem; text-transform: uppercase;">Treatment Given (T)</span>
                <div style="color: #e2e8f0; font-size: 0.95rem; margin-top: 4px;">{treat}</div>
            </div>
        </div>

        <div style="background: #1e293b; padding: 12px; border-radius: 8px; border-left: 4px solid #06b6d4;">
            <span style="font-weight: 700; color: #22d3ee; font-size: 0.85rem; text-transform: uppercase;">Extracted Vitals</span>
            <div style="color: #f1f5f9; font-size: 0.95rem; font-weight: 600; margin-top: 4px;">{vitals}</div>
        </div>
    </div>
    """
    return html

def build_paramedic_tab():
    patients = get_all_patients()
    patient_choices = [f"{p['id']} - {p['name']}" for p in patients] + ["+ New Patient"]
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🚑 Paramedic Intake Capture")
            patient_drop = gr.Dropdown(
                choices=patient_choices,
                label="Select Patient",
                value=patient_choices[0] if patient_choices else "+ New Patient"
            )
            
            with gr.Group(visible=False) as new_patient_box:
                new_name = gr.Textbox(label="Patient Full Name", placeholder="e.g. Jane Doe")
                new_dob = gr.Textbox(label="Birth Date", placeholder="YYYY-MM-DD")
                new_gender = gr.Radio(["Male", "Female", "Other"], label="Gender", value="Female")
                
            audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Dictate Handover Note")
            transcript_box = gr.Textbox(label="Transcript (Auto-filled / Editable)", lines=4, placeholder="Spoken text transcript will appear here...")
            image_in = gr.Image(sources=["upload", "webcam"], type="filepath", label="Attach Injury Photo (Optional)")
            
            btn_generate = gr.Button("⚡ Generate & Save Handover", variant="primary", size="lg")
            
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Gemma Structured Output")
            img_tag_label = gr.Label(label="Visual Image Tag", value="No image attached")
            mist_output_html = gr.HTML(value="<div style='padding:30px; text-align:center; color:#64748b;'>Dictate audio or type notes on the left, then click <b>Generate & Save Handover</b>.</div>")

    # Callbacks
    def on_patient_change(choice):
        return gr.update(visible=(choice == "+ New Patient"))

    patient_drop.change(fn=on_patient_change, inputs=[patient_drop], outputs=[new_patient_box])

    def on_audio_recorded(audio_path):
        if audio_path:
            gr.Info("Transcribing audio...")
            yield "Transcribing audio... please wait. 🎙️"
            result = transcribe_speech(audio_path)
            yield result
        else:
            yield ""

    audio_in.change(fn=on_audio_recorded, inputs=[audio_in], outputs=[transcript_box])

    def on_generate_handover(patient_sel, name, dob, gender, transcript, img_path):
        if not transcript or not transcript.strip():
            return patient_sel, "No text provided", "<div style='color:red;'>Please provide a text transcript or audio recording.</div>"
            
        # Determine patient ID
        if patient_sel == "+ New Patient":
            import uuid
            p_id = f"P-{uuid.uuid4().hex[:4].upper()}"
            p_name = name.strip() if name else "Anonymous Patient"
            p_dob = dob.strip() if dob else "1990-01-01"
            create_patient(p_id, p_name, p_dob, gender)
        else:
            p_id = patient_sel.split(" - ")[0]

        # Process image tag
        img_tag = ""
        if img_path:
            img_tag = tag_image(img_path)
            
        # Create encounter & synthesize MIST
        enc_id = create_encounter(p_id, raw_transcript=transcript, image_tag=img_tag)
        mist_dict = synthesize_mist(transcript, image_tag=img_tag)
        update_encounter_mist(enc_id, mist_dict)
        if img_tag:
            update_encounter_image_tag(enc_id, img_tag)

        # Refresh patient dropdown
        updated_patients = get_all_patients()
        updated_choices = [f"{p['id']} - {p['name']}" for p in updated_patients] + ["+ New Patient"]
        new_sel_val = f"{p_id} - {name}" if patient_sel == "+ New Patient" else patient_sel

        html_result = format_mist_html(mist_dict, image_tag=img_tag)
        tag_val = img_tag if img_tag else "No visual tag generated"

        return gr.update(choices=updated_choices, value=new_sel_val), tag_val, html_result

    btn_generate.click(
        fn=on_generate_handover,
        inputs=[patient_drop, new_name, new_dob, new_gender, transcript_box, image_in],
        outputs=[patient_drop, img_tag_label, mist_output_html]
    )

    return patient_drop
