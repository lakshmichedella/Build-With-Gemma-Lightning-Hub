"""T5 skeleton for the Nurse tab. Full layout added in T13 (see design.md §3.3)."""
import gradio as gr


def nurse_tab():
    with gr.Column() as tab:
        gr.Markdown("## Nurse Review")
        gr.Markdown("_Coming in T13: MIST summary, entity table, lookback flags, ESI+CoV._")
    return tab
