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
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
                <div>
                    <h1 style="margin:0; font-size:1.8rem; color:#38bdf8;">🏥 ER Handover Triage in Light Speed</h1>
                    <p style="margin:4px 0 0 0; color:#94a3b8; font-size:0.95rem;">Continuous Emergency Handover Chain (Paramedic ➔ Nurse ➔ Doctor) Powered by Gemma</p>
                </div>
                <a href="/file=presentation.html" target="_blank" style="text-decoration:none;">
                    <button style="background:linear-gradient(135deg, #0284c7, #4f46e5); color:white; border:none; padding:10px 18px; border-radius:10px; font-weight:700; cursor:pointer; font-size:0.9rem; box-shadow:0 4px 12px rgba(2, 132, 199, 0.4);">
                        📺 Launch Pitch Slide Deck
                    </button>
                </a>
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
                
        gr.Markdown(
            """
            ---
            *Built with Gemma for Kaggle 'Build with Gemma: Triage in Light Speed' Hackathon. Demo data is synthetic.*
            """
        )
        
    return app

if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, allowed_paths=["presentation.html", "sample_images"])

