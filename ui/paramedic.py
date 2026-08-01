"""T5 skeleton for the Paramedic tab. Full layout added in T9 (see design.md §3.2)."""
import gradio as gr


def paramedic_tab():
    with gr.Column() as tab:
        gr.Markdown("## Paramedic Intake")
        gr.Markdown("_Coming in T9: patient select, audio capture, photo upload, MIST synthesis._")
    return tab
