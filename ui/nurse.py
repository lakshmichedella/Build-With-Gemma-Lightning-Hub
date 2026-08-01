import json
import gradio as gr
from db.db import get_all_patients, get_latest_encounter_for_patient, get_recent_history, update_encounter_esi
from services.gemma_nurse import extract_entities, summarize_lookback, score_esi_cov
from ui.paramedic import format_mist_html

def format_cov_html(cov_dict: dict) -> str:
    """Formats visible 3-step Chain-of-Verification into a high-impact clinical UI card."""
    red_flags = cov_dict.get("red_flags", "None identified")
    prelim = cov_dict.get("prelim_score", "N/A")
    critique = cov_dict.get("critique", "Verified")
    final_score = cov_dict.get("final_score", 3)
    rationale = cov_dict.get("rationale", "")
    
    # ESI color badge mapping
    esi_colors = {
        1: ("#dc2626", "#fef2f2", "LEVEL 1 - RESUSCITATION (IMMEDIATE)"),
        2: ("#ea580c", "#fff7ed", "LEVEL 2 - EMERGENT / HIGH RISK"),
        3: ("#ca8a04", "#fefce8", "LEVEL 3 - URGENT (MULTIPLE RESOURCES)"),
        4: ("#16a34a", "#f0fdf4", "LEVEL 4 - LESS URGENT (1 RESOURCE)"),
        5: ("#2563eb", "#eff6ff", "LEVEL 5 - NON-URGENT (0 RESOURCES)")
    }
    bg_color, text_color, esi_label = esi_colors.get(int(final_score), ("#475569", "#ffffff", f"LEVEL {final_score}"))

    return f"""
    <div style="background-color: #0f172a; border-radius: 12px; padding: 20px; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 14px; margin-bottom: 16px;">
            <h3 style="margin: 0; color: #fbbf24; font-size: 1.2rem; font-weight: 700;">
                🧠 Gemma Chain-of-Verification (CoV) Reasoning Trail
            </h3>
            <div style="background: {bg_color}; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.5px;">
                ESI {final_score}
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div style="background: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid #ef4444;">
                <span style="font-weight: 700; color: #f87171; font-size: 0.8rem; text-transform: uppercase;">Step 1: Red Flag Audit</span>
                <div style="color: #cbd5e1; font-size: 0.9rem; margin-top: 6px;">{red_flags}</div>
            </div>
            
            <div style="background: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid #3b82f6;">
                <span style="font-weight: 700; color: #60a5fa; font-size: 0.8rem; text-transform: uppercase;">Step 2: Prelim Score</span>
                <div style="color: #cbd5e1; font-size: 1.2rem; font-weight: 700; margin-top: 4px;">ESI Level {prelim}</div>
            </div>

            <div style="background: #1e293b; padding: 14px; border-radius: 8px; border-top: 4px solid #a855f7;">
                <span style="font-weight: 700; color: #c084fc; font-size: 0.8rem; text-transform: uppercase;">Step 3: Self Critique</span>
                <div style="color: #cbd5e1; font-size: 0.9rem; margin-top: 6px;">{critique}</div>
            </div>
        </div>

        <div style="background: {bg_color}; padding: 14px 18px; border-radius: 8px; color: #ffffff;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; opacity: 0.9;">Final Verified Recommendation</div>
            <div style="font-size: 1.1rem; font-weight: 800; margin-top: 2px;">{esi_label}</div>
            <div style="font-size: 0.95rem; margin-top: 4px; opacity: 0.95;">{rationale}</div>
        </div>
    </div>
    """

def build_nurse_tab():
    patients = get_all_patients()
    patient_choices = [f"{p['id']} - {p['name']}" for p in patients]
    
    with gr.Row():
        patient_drop = gr.Dropdown(
            choices=patient_choices,
            label="Select Active ER Patient for Nurse Review",
            value=patient_choices[0] if patient_choices else None,
            scale=3
        )
        btn_load = gr.Button("🔍 Load Patient Record", variant="secondary", scale=1)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("#### 📋 Handover Summary")
            mist_html_box = gr.HTML(value="<div style='color:#64748b;'>Select a patient and click <b>Load Patient Record</b></div>")
            
        with gr.Column(scale=1):
            gr.Markdown("#### 🏷️ Extracted Medical Entities")
            entity_table = gr.Dataframe(
                headers=["Category", "Entity"],
                datatype=["str", "str"],
                col_count=(2, "fixed"),
                interactive=False
            )
            
        with gr.Column(scale=1):
            gr.Markdown("#### ⚠️ History Lookback Flags (2-3 Visits)")
            flags_box = gr.Markdown("Select patient to view clinical flags...")

    gr.Markdown("---")
    with gr.Row():
        btn_score_esi = gr.Button("⚡ Calculate ESI Score with Chain-of-Verification (CoV)", variant="primary", size="lg")

    cov_output_html = gr.HTML(value="<div style='padding:20px; text-align:center; color:#64748b;'>Click <b>Calculate ESI Score</b> to generate visible clinical reasoning.</div>")

    # Current loaded encounter state stored implicitly or retrieved fresh from DB
    loaded_enc_state = gr.State()

    def on_load_patient(patient_sel):
        if not patient_sel:
            return "<div style='color:red;'>No patient selected</div>", [], "No selection", None, "<div></div>"
            
        patient_id = patient_sel.split(" - ")[0]
        enc = get_latest_encounter_for_patient(patient_id)
        if not enc:
            return "<div style='color:orange;'>No active encounter record found for patient.</div>", [], "No active encounter.", None, "<div></div>"
            
        # Parse MIST
        mist_data = {}
        if enc.get("structured_mist"):
            try:
                mist_data = json.loads(enc["structured_mist"])
            except Exception:
                mist_data = {"signs": enc["structured_mist"]}
        else:
            mist_data = {"signs": enc.get("raw_transcript", "N/A")}

        mist_html = format_mist_html(mist_data, image_tag=enc.get("image_tag", ""))
        
        # Entities
        raw_entities = extract_entities(mist_data)
        entity_rows = [[item.get("category", "General"), item.get("entity", "")] for item in raw_entities]

        # Lookback Flags
        history_dict = get_recent_history(patient_id, limit=3)
        lookback_flags = summarize_lookback(mist_data, history_dict)
        flags_md = "\n".join([f"- {flag}" for flag in lookback_flags])

        # Pre-existing ESI CoV if present
        cov_html = "<div></div>"
        if enc.get("esi_rationale"):
            try:
                cov_dict = json.loads(enc["esi_rationale"])
                cov_html = format_cov_html(cov_dict)
            except Exception:
                pass

        return mist_html, entity_rows, flags_md, enc["id"], cov_html

    btn_load.click(
        fn=on_load_patient,
        inputs=[patient_drop],
        outputs=[mist_html_box, entity_table, flags_box, loaded_enc_state, cov_output_html]
    )

    def on_score_esi(patient_sel, enc_id):
        if not patient_sel or not enc_id:
            return "<div style='color:red;'>Please load a valid patient record first.</div>"
            
        patient_id = patient_sel.split(" - ")[0]
        enc = get_latest_encounter_for_patient(patient_id)
        
        mist_data = {}
        if enc.get("structured_mist"):
            try:
                mist_data = json.loads(enc["structured_mist"])
            except Exception:
                mist_data = {"signs": enc["structured_mist"]}
        else:
            mist_data = {"signs": enc.get("raw_transcript", "")}

        history_dict = get_recent_history(patient_id, limit=3)
        lookback_flags = summarize_lookback(mist_data, history_dict)

        cov_dict = score_esi_cov(mist_data, history_flags=lookback_flags)
        
        # Save ESI & CoV rationale back to SQLite database
        final_esi = cov_dict.get("final_score", 3)
        update_encounter_esi(enc_id, final_esi, cov_dict)

        return format_cov_html(cov_dict)

    btn_score_esi.click(
        fn=on_score_esi,
        inputs=[patient_drop, loaded_enc_state],
        outputs=[cov_output_html]
    )

    return patient_drop
