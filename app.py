import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import gradio as gr
import spaces

from db.seed import seed_database
from ui.paramedic import build_paramedic_tab
from ui.nurse import build_nurse_tab
from ui.doctor import build_doctor_tab

# Ensure database is initialized & seeded on startup
seed_database()

# Dummy function to satisfy HF ZeroGPU initialization requirements
@spaces.GPU
def initialize_gpu():
    pass

initialize_gpu()

def build_app():
    custom_css = """
    .gradio-container {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    """
    
    with gr.Blocks(title="ER Handover Triage — Gemma Lightning", css=custom_css, theme=gr.themes.Soft(primary_hue="sky")) as app_blocks:
        gr.Markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
                <div>
                    <h1 style="margin:0; font-size:1.8rem; color:#38bdf8;">🏥 ER Handover Triage in Light Speed</h1>
                    <p style="margin:4px 0 0 0; color:#94a3b8; font-size:0.95rem;">Continuous Emergency Handover Chain (Paramedic ➔ Nurse ➔ Doctor) Powered by Gemma</p>
                </div>
            </div>
            """
        )
        
        with gr.Tabs():
            with gr.TabItem("🚑 Paramedic Intake", id="paramedic_tab"):
                build_paramedic_tab()
                
            with gr.TabItem("👩‍⚕️ Nurse Review & ESI Triage", id="nurse_tab"):
                build_nurse_tab()
                
            with gr.TabItem("🩺 Doctor Queue & Execution", id="doctor_tab"):
                build_doctor_tab()
                
            with gr.TabItem("📺 Pitch Deck Presentation", id="presentation_tab"):
                with open("presentation.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                # Safely escape double quotes for the srcdoc attribute
                html_content_escaped = html_content.replace('"', '&quot;')
                gr.HTML(f'<iframe srcdoc="{html_content_escaped}" width="100%" height="800px" style="border:none; border-radius: 12px; overflow: hidden; background: #090d16;"></iframe>')
                
        gr.Markdown(
            """
            ---
            *Built with Gemma for Kaggle 'Build with Gemma: Triage in Light Speed' Hackathon. Demo data is synthetic.*
            """
        )
        
    return app_blocks

app = build_app()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
