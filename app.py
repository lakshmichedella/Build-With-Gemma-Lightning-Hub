"""T5: app skeleton. Assembles the 3 tabs and runs seeding once at launch."""
from dotenv import load_dotenv
import gradio as gr

from db.seed import seed
from ui.paramedic import paramedic_tab, refresh_patient_dropdown as refresh_paramedic_dropdown
from ui.nurse import nurse_tab, refresh_patient_dropdown as refresh_nurse_dropdown
from ui.doctor import doctor_tab, refresh_queue as refresh_doctor_queue

load_dotenv()
seed()

CUSTOM_CSS = """
.section-box {
    border: 1px solid #2a3142 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    margin-bottom: 14px !important;
    background: #161b28 !important;
}
.section-header { font-weight: 600; color: #e5e7eb; font-size: 15px; }
.mist-header-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.mist-tag-badge {
    background: #2563eb; color: white; padding: 2px 10px;
    border-radius: 999px; font-size: 12px; font-weight: 600;
}
.mist-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.mist-card {
    grid-column: span 1;
    background: #1a2030;
    border-left: 4px solid #888;
    border-radius: 6px;
    padding: 10px 14px;
}
.mist-card.full { grid-column: 1 / -1; }
.mist-label {
    font-size: 11px; text-transform: uppercase; letter-spacing: .05em;
    color: #9ca3af; margin-bottom: 4px;
}
.mist-value { font-weight: 600; color: #f3f4f6; }
.transparent-wrapper {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
"""

with gr.Blocks(title="Lighting Hub Triage", theme=gr.themes.Default(), css=CUSTOM_CSS) as demo:
    # Force Gradio's native dark theme rather than hand-overriding component
    # backgrounds one-by-one — overriding only .gradio-container's background
    # (an earlier attempt) leaves every inner widget (Audio recorder, Image
    # dropzone, Textbox) on Gradio's default *light* palette, which is
    # exactly the light-box-on-dark-page mismatch this fixes. Gradio's own
    # dark CSS variables apply consistently to every component once `.dark`
    # is on <body> — that's the supported way to get a dark UI, not custom
    # background overrides fighting the theme.
    demo.load(None, None, None, js="() => { document.body.classList.add('dark'); }")

    gr.Markdown("# 🏥 Lighting Hub Triage")
    gr.Markdown("Continuous Emergency Handover Chain (Paramedic → Nurse → Doctor) — Powered by Gemma Models")
    with gr.Tabs():
        with gr.Tab("🚑 Paramedic Intake") as paramedic_tab_item:
            _, paramedic_patient_dropdown = paramedic_tab()
        with gr.Tab("👩‍⚕️ Nurse Review & ESI Triage") as nurse_tab_item:
            _, nurse_patient_dropdown = nurse_tab()
        with gr.Tab("👨‍⚕️ Doctor Queue & Execution") as doctor_tab_item:
            (
                _,
                doctor_queue_df,
                doctor_queue_state,
                doctor_action_group,
                doctor_selection_header,
                doctor_selected_encounter_state,
                doctor_override_info,
            ) = doctor_tab()
    gr.Markdown("_Built with Gemma for Kaggle 'Build with Gemma: Triage in Light Speed' Hackathon. Demo data is synthetic._")

    # Dropdown/table values only evaluate once, at build time above —
    # re-query the DB whenever a tab is opened so a change made in one tab
    # (new patient, fresh triage) shows up in the others without an app
    # restart (AGENTS.md §5).
    paramedic_tab_item.select(refresh_paramedic_dropdown, outputs=paramedic_patient_dropdown)
    nurse_tab_item.select(refresh_nurse_dropdown, outputs=nurse_patient_dropdown)
    doctor_tab_item.select(
        refresh_doctor_queue,
        outputs=[
            doctor_queue_df,
            doctor_queue_state,
            doctor_action_group,
            doctor_selection_header,
            doctor_selected_encounter_state,
            doctor_override_info,
        ],
    )

if __name__ == "__main__":
    demo.launch()
