import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import gradio as gr
from db.seed import seed_database
from ui.paramedic import build_paramedic_tab
from ui.nurse import build_nurse_tab
from ui.doctor import build_doctor_tab

# Ensure database is initialized & seeded on startup
seed_database()

def build_app():
    custom_css = """
    .gradio-container {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    """
    
    with gr.Blocks(title="ER Handover Triage — Gemma Lightning", css=custom_css, theme=gr.themes.Soft(primary_hue="sky")) as app:
        gr.Markdown(
            """
            # 🏥 ER Handover Triage in Light Speed
            **Continuous Emergency Handover Chain (Paramedic ➔ Nurse ➔ Doctor) Powered by Gemma Models**
            """
        )
        
        with gr.Tabs():
            with gr.TabItem("🚑 Paramedic Intake", id="paramedic_tab"):
                build_paramedic_tab()
                
            with gr.TabItem("👩‍⚕️ Nurse Review & ESI Triage", id="nurse_tab"):
                build_nurse_tab()
                
            with gr.TabItem("🩺 Doctor Queue & Execution", id="doctor_tab"):
                build_doctor_tab()
                
        gr.Markdown(
            """
            ---
            *Built with Gemma for Kaggle 'Build with Gemma: Triage in Light Speed' Hackathon. Demo data is synthetic.*
            """
        )
        
    return app

if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
