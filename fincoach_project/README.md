# FinCoach — Life Simulator (Django + Three.js)

## What's built so far

- **Django project** (`fincoach_project/`) — settings, URL routing, admin
- **`simulator` app** — the Life Simulator feature:
  - `models.py` — Scenario, Choice, SimulationRun, DecisionLog
  - `views.py` — page view + JSON API for the 3D frontend to talk to
  - `admin.py` — lets your team add scenarios/choices at `/admin/` with no code
  - `templates/simulator/simulator.html` — the 3D scene page
  - `templates/simulator/results.html` — text summary + chart after finishing
  - `static/simulator/js/scene.js` — Three.js scene + API calls
  - `static/simulator/css/base.css` — brand colors as CSS variables

Right now the "avatar" is a plain green box and the ground is a flat
plane — that's intentional. This proves the whole pipeline (3D render
-> Django API -> database -> results) works before we spend time on
real art. Once Kenney/Mixamo/Sketchfab assets are ready, we swap the
box for a loaded 3D model in `scene.js` — nothing else needs to change.

## How to run it (on your own machine, once ready)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # so you can log into /admin/
python manage.py runserver
```

Then visit:
- `http://127.0.0.1:8000/admin/` — log in and add a few Scenarios +
  Choices so there's something to play through
- `http://127.0.0.1:8000/simulator/` — try the simulator
- `http://127.0.0.1:8000/simulator/results/` — see it after finishing

## Adding your first scenario (no code needed)

1. Go to `/admin/` and log in.
2. Click **Scenarios -> Add**.
3. Fill in: title, description, order (1, 2, 3...), and a location_tag
   (just a short label like `mechanic_shop` for now).
4. Underneath, add 2-3 **Choices** right on the same page — label,
   any costs, and feedback text.
5. Save, then visit `/simulator/` to try it.

## What's next

- Swap the placeholder box for a real avatar model
- Add more scenario locations/scenes
- Design the choice-popup UI to match final brand look
- Turn the results chart into a month-by-month trend, not just a snapshot
