# Elicitation techniques (Software Architecture · University of Stuttgart)

In-class pack after the missed-exams lab. Recap, two check questions, group techniques board. Specification is a separate tutorial: [`../specification/`](../specification/).

| File | Use |
| --- | --- |
| [`index.html`](index.html) | Projected student flow: recap + two MCQs |
| [`board.html`](board.html) | Techniques board — collect pros / cons / contexts |
| [`instructor.html`](instructor.html) | Timing, MCQ keys, group technique assignments |
| [`LecturePlan_90min_Elicitation.pdf`](LecturePlan_90min_Elicitation.pdf) | One-pager 90-minute lecture plan |
| [`build_onepager.py`](build_onepager.py) | Regenerates the PDF (`reportlab`) |

## Run

```bash
python3 -m http.server --directory tutorials/eliciation2
```

Order: `index.html` → `board.html` (groups report).

## Session shape

1. Recap (introspection, hard data, conflict of objectives, problem space)  
2. MCQ · introspection  
3. MCQ · ground-truth / hard-data analysis  
4. Groups: one elicitation technique each → fill board · debrief  
