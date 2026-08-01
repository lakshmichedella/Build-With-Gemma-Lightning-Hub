"""T5: app skeleton. Assembles the 3 tabs and runs seeding once at launch."""
from dotenv import load_dotenv
import gradio as gr

from db.seed import seed
from ui.paramedic import paramedic_tab, refresh_patient_dropdown as refresh_paramedic_dropdown
from ui.nurse import nurse_tab, refresh_patient_dropdown as refresh_nurse_dropdown
from ui.doctor import doctor_tab

load_dotenv()
seed()

with gr.Blocks(title="ER Handover Triage") as demo:
    gr.Markdown("# ER Handover Triage")
    with gr.Tabs():
        with gr.Tab("Paramedic Intake") as paramedic_tab_item:
            _, paramedic_patient_dropdown = paramedic_tab()
        with gr.Tab("Nurse Review") as nurse_tab_item:
            _, nurse_patient_dropdown = nurse_tab()
        with gr.Tab("Doctor Queue"):
            doctor_tab()

    # Dropdown `choices=` only evaluate once, at build time above — re-query
    # the DB whenever a tab is opened so patients created in one tab show up
    # in the others without an app restart (AGENTS.md §5).
    paramedic_tab_item.select(refresh_paramedic_dropdown, outputs=paramedic_patient_dropdown)
    nurse_tab_item.select(refresh_nurse_dropdown, outputs=nurse_patient_dropdown)

if __name__ == "__main__":
    demo.launch()
