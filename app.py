"""T5: app skeleton. Assembles the 3 tabs and runs seeding once at launch."""
from dotenv import load_dotenv
import gradio as gr

from db.seed import seed
from ui.paramedic import paramedic_tab
from ui.nurse import nurse_tab
from ui.doctor import doctor_tab

load_dotenv()
seed()

with gr.Blocks(title="ER Handover Triage") as demo:
    gr.Markdown("# ER Handover Triage")
    with gr.Tabs():
        with gr.Tab("Paramedic Intake"):
            paramedic_tab()
        with gr.Tab("Nurse Review"):
            nurse_tab()
        with gr.Tab("Doctor Queue"):
            doctor_tab()

if __name__ == "__main__":
    demo.launch()
