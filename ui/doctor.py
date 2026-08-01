"""T5 skeleton for the Doctor tab. Full layout added in T15 (see design.md §3.4)."""
import gradio as gr


def doctor_tab():
    with gr.Column() as tab:
        gr.Markdown("## Doctor Queue")
        gr.Markdown("_Coming in T15: ranked patient queue by ESI score._")
    return tab
