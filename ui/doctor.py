import json
import gradio as gr
from db.db import get_active_queue, assign_staff, update_encounter_doctor_note, get_encounter
from services.stt import transcribe_speech
from services.gemma_doctor import structure_dictation

def build_queue_table_rows():
    queue_data = get_active_queue()
    rows = []
    for item in queue_data:
        esi = item.get("esi_score")
        esi_str = f"ESI {esi}" if esi else "Pending Nurse Review"
        
        mist = {}
        if item.get("structured_mist"):
            try:
                mist = json.loads(item["structured_mist"])
            except Exception:
                pass
                
        cc = mist.get("chief_complaint", item.get("raw_transcript", "Unspecified"))
        assigned = item.get("assigned_to") or "Unassigned"
        created = item.get("created_at") or "Just now"
        
        rows.append([
            esi_str,
            f"{item['patient_id']} - {item['patient_name']}",
            cc,
            assigned,
            created,
            item["encounter_id"]
        ])
    return rows

def build_doctor_tab():
    with gr.Row():
        gr.Markdown("### 🩺 Doctor Emergency Department Queue & Execution")
        btn_refresh = gr.Button("🔄 Refresh Live Queue", variant="primary", size="sm")

    queue_df = gr.Dataframe(
        headers=["ESI Score", "Patient", "Chief Complaint", "Assigned Staff", "Intake Time", "Encounter ID"],
        datatype=["str", "str", "str", "str", "str", "str"],
        col_count=(6, "fixed"),
        value=build_queue_table_rows(),
        interactive=False,
        label="Prioritized Patient Queue (Ranked by ESI Acuity)"
    )

    gr.Markdown("---")
    gr.Markdown("### 👨‍⚕️ Patient Bedside Action & Dictation")

    with gr.Row():
        with gr.Column(scale=1):
            enc_select = gr.Dropdown(
                label="Select Encounter ID",
                choices=[row[5] for row in build_queue_table_rows()],
                value=build_queue_table_rows()[0][5] if build_queue_table_rows() else None
            )
            staff_drop = gr.Dropdown(
                choices=["Unassigned", "Dr. Smith (Attending)", "Dr. Patel (Resident)", "RN Taylor (Primary)", "RN Davis"],
                label="Assign Healthcare Staff",
                value="Unassigned"
            )
            btn_assign = gr.Button("Assign Staff Member", variant="secondary")
            assign_msg = gr.Label(value="", label="Assignment Status")

        with gr.Column(scale=2):
            doc_audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Dictate Doctor Note")
            doc_transcript = gr.Textbox(label="Doctor Note Transcript", lines=3, placeholder="Doctor dictation text...")
            btn_structure_note = gr.Button("⚡ Structure Note & Suggest ICD-10 Code", variant="primary")
            
            note_output_html = gr.HTML(value="<div style='color:#64748b; padding:15px;'>Dictate or type clinical notes above to structure and code.</div>")

    # Callbacks
    def on_refresh():
        rows = build_queue_table_rows()
        enc_choices = [row[5] for row in rows]
        val = enc_choices[0] if enc_choices else None
        return rows, gr.update(choices=enc_choices, value=val)

    btn_refresh.click(fn=on_refresh, outputs=[queue_df, enc_select])

    def on_assign(enc_id, staff):
        if not enc_id:
            return "No encounter selected."
        assign_staff(enc_id, staff)
        return f"Successfully assigned {staff} to {enc_id}"

    btn_assign.click(fn=on_assign, inputs=[enc_select, staff_drop], outputs=[assign_msg])

    def on_audio_recorded(audio_path):
        if audio_path:
            import time
            gr.Info("Transcribing audio...")
            yield "Transcribing audio... please wait. 🎙️"
            time.sleep(0.2)
            result = transcribe_speech(audio_path)
            yield result
        else:
            yield ""

    doc_audio.stop_recording(fn=on_audio_recorded, inputs=[doc_audio], outputs=[doc_transcript])
    doc_audio.upload(fn=on_audio_recorded, inputs=[doc_audio], outputs=[doc_transcript])
    doc_audio.clear(fn=lambda: "", inputs=None, outputs=[doc_transcript])

    def on_structure_note(enc_id, transcript):
        if not enc_id or not transcript or not transcript.strip():
            return "<div style='color:red;'>Please select an encounter and provide dictation text.</div>"
            
        doc_result = structure_dictation(transcript)
        plan = doc_result.get("assessment_plan", transcript)
        code = doc_result.get("suggested_code", "Unspecified")

        update_encounter_doctor_note(enc_id, plan, code)

        return f"""
        <div style="background-color: #0f172a; border-radius: 10px; padding: 18px; color: #f8fafc; font-family: system-ui, sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-bottom: 12px;">
                <h4 style="margin: 0; color: #38bdf8;">Structured Clinical Assessment & Coding</h4>
                <span style="background: #22c55e; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.85rem;">{code}</span>
            </div>
            <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5; white-space: pre-wrap;">{plan}</div>
        </div>
        """

    btn_structure_note.click(
        fn=on_structure_note,
        inputs=[enc_select, doc_transcript],
        outputs=[note_output_html]
    )
