#!/usr/bin/env python3
"""Build a one-page PDF lecture plan for the 90-minute elicitation techniques session."""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent / "LecturePlan_90min_Elicitation.pdf"

INK = HexColor("#1c1915")
MUTED = HexColor("#5e574e")
TEAL = HexColor("#0f766e")
LINE = HexColor("#ddd4c6")
PAPER = HexColor("#f3efe6")
CARD = HexColor("#fffdf8")
RUST = HexColor("#9a3412")
BLUE = HexColor("#1e40af")


def draw_wrapped(c, text, x, y, width, font="Helvetica", size=8.5, leading=11, color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    for w in words:
        trial = (line + " " + w).strip()
        if c.stringWidth(trial, font, size) <= width:
            line = trial
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def section_rule(c, y, left, right):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(left, y, right, y)
    return y - 3 * mm


def main():
    width, height = A4
    margin = 12 * mm
    left = margin
    right = width - margin
    usable = right - left

    c = canvas.Canvas(str(OUT), pagesize=A4)

    c.setFillColor(PAPER)
    c.rect(0, height - 28 * mm, width, 28 * mm, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, height - 28 * mm, 3.2 * mm, 28 * mm, fill=1, stroke=0)

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(left, height - 8 * mm, "Software Architecture  ·  University of Stuttgart")

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left, height - 14.5 * mm, "90-minute lecture plan  ·  Elicitation techniques")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(left, height - 20 * mm, "Follow-up to the missed-exams lab  ·  Artifacts: tutorials/eliciation2/")
    c.drawRightString(right, height - 20 * mm, "One pager")

    y = height - 33 * mm

    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, y, "LEARNING OUTCOMES")
    y -= 4.5 * mm
    outcomes = [
        "Explain introspection vs hard-data analysis without confusing either with a finished requirement.",
        "Compare elicitation techniques (pros, cons, suited context) using the lecture technique table.",
        "Argue when to pick interviews, workshops, observation, surveys, documents, or prototyping.",
    ]
    for o in outcomes:
        c.setFillColor(TEAL)
        c.circle(left + 1.2 * mm, y + 1.2 * mm, 1.0 * mm, fill=1, stroke=0)
        y = draw_wrapped(c, o, left + 4.5 * mm, y, usable - 4.5 * mm, size=8.2, leading=10.5)
        y -= 0.8 * mm

    y = section_rule(c, y - 1 * mm, left, right)

    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, y, "AGENDA (90 MIN)")
    y -= 5 * mm

    agenda = [
        ("0–8", "Recap", "Four terms: introspection, hard data / ground truth, conflict of objectives, problem space. Do not re-run the full lab."),
        ("8–22", "Two checks", "Project index.html. Room votes. Q1 introspection → C. Q2 ground truth → C. Discuss distractors briefly."),
        ("22–40", "Group work", "Assign G1–G6 one technique each. Draft pros / cons / suited context (~15–18 min)."),
        ("40–75", "Board debrief", "Scribe into board.html; project the summary table. Compare contexts. Sample answers only after their round."),
        ("75–90", "Close", "Two takeaways + export board JSON if useful. Point to the filled technique table as the session artifact."),
    ]

    row_h = 12.2 * mm
    for i, (t, title, body) in enumerate(agenda):
        top = y
        c.setFillColor(CARD if i % 2 == 0 else PAPER)
        c.roundRect(left, top - row_h + 2 * mm, usable, row_h - 0.5 * mm, 2 * mm, fill=1, stroke=0)
        c.setFillColor(RUST)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(left + 2.5 * mm, top - 3.2 * mm, t)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(left + 16 * mm, top - 3.2 * mm, title)
        draw_wrapped(
            c, body, left + 16 * mm, top - 7.2 * mm, usable - 19 * mm,
            size=7.6, leading=9.5, color=MUTED,
        )
        y -= row_h

    y -= 1.5 * mm
    y = section_rule(c, y, left, right)

    col_w = (usable - 5 * mm) / 2
    col2 = left + col_w + 5 * mm
    block_top = y

    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, y, "MCQ KEYS (DO NOT PROJECT)")
    y -= 4.2 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left, y, "Q1 Introspection → C")
    y -= 3.5 * mm
    y = draw_wrapped(
        c,
        "Reminder is a solution. Introspection collected beliefs; it did not validate a need. Press anyone defending “we agreed.”",
        left, y, col_w, size=7.6, leading=9.5, color=MUTED,
    )
    y -= 1.5 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left, y, "Q2 Ground truth → C")
    y -= 3.5 * mm
    y = draw_wrapped(
        c,
        "Counts locate problem-space conditions. Jumping to scheduler conflict-detection skips whose objective is served. A/D absolute & false; B is a sample-size red herring.",
        left, y, col_w, size=7.6, leading=9.5, color=MUTED,
    )
    y_left = y

    y = block_top
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(col2, y, "GROUP → TECHNIQUE")
    y -= 4 * mm
    assignments = [
        ("G1", "Interviews"),
        ("G2", "Workshops"),
        ("G3", "Observation / site visit"),
        ("G4", "Surveys / questionnaires"),
        ("G5", "Document analysis"),
        ("G6", "Prototyping"),
    ]
    for g, tech in assignments:
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(col2, y, g)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8)
        c.drawString(col2 + 10 * mm, y, tech)
        y -= 3.8 * mm
    y -= 0.5 * mm
    y = draw_wrapped(
        c,
        "Introspection + hard data = last week (optional 1-min refresh). Stuck prompts on instructor.html.",
        col2, y, col_w, size=7.4, leading=9.2, color=MUTED,
    )
    y_right = y

    y = min(y_left, y_right) - 2.5 * mm
    y = section_rule(c, y, left, right)

    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, y, "CLOSE · TWO LINES (+ PREVIEW)")
    y -= 4 * mm
    closes = [
        "Elicitation chooses sources and techniques — no single technique is enough.",
        "Hard data and introspection both mislead when they skip the problem space.",
        "The filled technique table (pros / cons / context) is the session artifact.",
    ]
    for line in closes:
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(left, y, "→")
        c.setFillColor(INK)
        c.setFont("Helvetica", 8)
        c.drawString(left + 5 * mm, y, line)
        y -= 3.8 * mm

    y -= 1.5 * mm
    y = section_rule(c, y, left, right)

    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left, y, "OPEN IN CLASS")
    y -= 4 * mm
    files = [
        "index.html — recap + MCQs",
        "board.html — pros / cons / contexts",
        "instructor.html — private keys",
    ]
    x = left
    c.setFont("Helvetica", 7.8)
    for f in files:
        c.setFillColor(CARD)
        tw = c.stringWidth(f, "Helvetica", 7.8) + 6 * mm
        c.roundRect(x, y - 1.2 * mm, tw, 5.2 * mm, 2 * mm, fill=1, stroke=0)
        c.setFillColor(INK)
        c.drawString(x + 2.5 * mm, y + 0.6 * mm, f)
        x += tw + 2.5 * mm

    y -= 8 * mm
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.2)
    c.drawString(left, y, "Serve:  python3 -m http.server --directory tutorials/eliciation2")
    c.drawRightString(right, y, "Dr. Floriment Klinaku")

    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
