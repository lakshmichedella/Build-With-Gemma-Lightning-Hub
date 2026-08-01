"""Shared MIST card-grid renderer, used by both the Paramedic tab (where a
handover is first generated) and the Nurse tab (where it's reviewed) — a
single source of truth so the two views can't silently drift apart, which
is exactly what happened before this module existed (Nurse rendered a
plain table while Paramedic had the card grid)."""

FIELD_COLORS = {
    "chief_complaint": "#fde68a",
    "mechanism": "#bfdbfe",
    "injury": "#fecaca",
    "signs": "#fed7aa",
    "treatment": "#bbf7d0",
    "vitals": "#e9d5ff",
    "interventions_given": "#a5f3fc",
    "allergies": "#fca5a5",
}

FIELD_LABELS = {
    "chief_complaint": "Chief Complaint",
    "mechanism": "Mechanism (M)",
    "injury": "Injury / Findings (I)",
    "signs": "Signs & Symptoms (S)",
    "treatment": "Treatment Given (T)",
    "vitals": "Extracted Vitals",
    "interventions_given": "Interventions Given",
    "allergies": "Allergies",
}

# Fields rendered full-width in the card grid; the rest pair up two-per-row
# in the order FIELD_LABELS lists them, which already produces the intended
# layout (chief complaint full-width, mechanism+injury paired, signs+
# treatment paired, then vitals/interventions/allergies full-width) without
# needing manual row math — CSS grid auto-flows around the "full" spans.
FULL_WIDTH_FIELDS = {"chief_complaint", "vitals", "interventions_given", "allergies"}


def mist_card_html(mist, image_tag=None, header="🚑 Structured MIST Handover Grid"):
    cards = "".join(
        f'<div class="mist-card{" full" if field in FULL_WIDTH_FIELDS else ""}" '
        f'style="border-left-color:{FIELD_COLORS.get(field, "#888")};">'
        f'<div class="mist-label">{FIELD_LABELS.get(field, field.replace("_", " ").title())}</div>'
        f'<div class="mist-value">{mist.get(field, "Not reported")}</div>'
        f"</div>"
        for field in FIELD_LABELS
        if field in mist
    )
    tag_badge = f'<span class="mist-tag-badge">{image_tag}</span>' if image_tag else ""
    header_html = (
        '<div class="mist-header-row">'
        f'<span class="section-header">{header}</span>'
        f"{tag_badge}</div>"
    )
    return f'{header_html}<div class="mist-grid">{cards}</div>'
