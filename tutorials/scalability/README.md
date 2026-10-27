# Campus peak · Scale, balance, survive

In-class companion for **Cloud Computing · Week 2** (scalability, elasticity, load balancing, availability, autoscaling). Fits the **15–20 minute** short-apply block. No install.

| File | Audience |
| --- | --- |
| [`index.html`](index.html) | Student / projected exercise |
| [`instructor.html`](instructor.html) | Timing, answer key, takeaway map |

## Run in class

Open the student page in a browser, or serve the folder:

```bash
python3 -m http.server --directory tutorials/scalability
```

Then visit `http://localhost:8000/`. Keep [`instructor.html`](instructor.html) on a second screen.

## Minute plan (~18 min)

1. Scenario — campus registration peak (~2 min)  
2. Vertical vs horizontal (~3 min)  
3. Load balancer + `/health` meaning; fail one instance (~4 min)  
4. Autoscaling sketch: metric, min/desired/max, cooldown (~5 min)  
5. One risk (~2 min)  
6. Reveal vs possible answer (~3 min)  

The AWS live demo stays on the lecture slides; this lab is the conceptual apply step only.
