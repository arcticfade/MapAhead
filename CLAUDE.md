# MapAhead

Supply planning for ultracycling events: upload a GPX route, find POIs (fuel, water, food, sleep, ...) along it, plan supply points. Python/FastAPI backend, Angular frontend (in progress), OpenStreetMap via Overpass.

## Read first

- `docs/00-vision.md` what we are building and why
- `docs/01-architecture.md` layout, layers, data flow, API contract
- `docs/02-conventions.md` how we work, code rules, who drives a step
- `docs/03-roadmap.md` the living plan; find the next unchecked step there
- `docs/04-domain.md` glossary
- `docs/adr/` decisions; `docs/concepts/` learning notes

## How we work

The owner is learning and writes the core logic. For steps marked **Owner** in the roadmap: scaffold files, tests and config, explain the concept, then review the owner's code. Do not implement the logic for them unless asked. For steps marked **Claude**: implement, explain, and leave a concept note if a new idea is introduced.

Small steps. One roadmap step per session, tick it in `docs/03-roadmap.md` in the same commit. Keep docs in sync with code.

## Run and test

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                                # offline tests; add -m live for real Overpass, -m e2e for browser
fastapi dev mapahead/main.py --port 5000 # http://localhost:5000/docs

# frontend (Phase 2)
cd frontend && npm ci && ng serve
```

## Rules that bite

- Backend computes, frontend presents: API returns numbers and IDs, never formatted strings.
- No `sys.path` hacks; import as `mapahead.<module>`.
- Never wrap an `HTTPException` in a broad `except Exception`.
- Never bind untrusted text with `[innerHTML]` in Angular.
- Commit only when asked; use the step number in the subject (`1.2: ...`).
