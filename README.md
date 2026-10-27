# Software Architecture · Tutorials

In-class teaching materials (University of Stuttgart). Most labs are static HTML — open in a browser.

**Student site (GitHub Pages):** https://klinakuf.github.io/swarch-tutorials/

| Tutorial | Folder | How to run |
| --- | --- | --- |
| One sentence, three causes | [`tutorials/elicitation/`](tutorials/elicitation/) | HTML in browser / Pages |
| Elicitation techniques | [`tutorials/eliciation2/`](tutorials/eliciation2/) | HTML in browser / Pages |
| Requirement specification | [`tutorials/specification/`](tutorials/specification/) | HTML in browser / Pages |
| Campus peak · Scale, balance, survive | [`tutorials/scalability/`](tutorials/scalability/) | HTML in browser / Pages |
| Monte Carlo, from one picture | [`tutorials/montecarlo/`](tutorials/montecarlo/) | Streamlit (local Python) |

## Local serve (optional)

```bash
python3 -m http.server --directory .
```

Then open `http://localhost:8000/`.

## Monte Carlo (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd tutorials/montecarlo && streamlit run app.py
```
