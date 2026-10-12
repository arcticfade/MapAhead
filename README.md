# 🗺️ MapAhead

Supply planning for ultracycling events. Upload a GPX route, see it on a map, and find points of interest (fuel, water, food, sleep, ...) along it, sorted by route kilometre with their deviation from the route.

Started as a school project (gas stations only, vanilla JS). Now being rebuilt step by step: Python/FastAPI backend, Angular frontend, more POI categories, saved event plans, Docker deployment. The plan and the reasoning live in [docs/](docs/); start with [docs/00-vision.md](docs/00-vision.md) and [docs/03-roadmap.md](docs/03-roadmap.md).

## Status

- ✅ Phase 0: docs, `CLAUDE.md`, backend as an installable package
- ⏳ Phase 1: backend refactor and bug fixes
- ⏳ Phase 2: Angular frontend (the current `Frontend/` folder is the old vanilla JS app and will be replaced)

## Quick start

### Backend

Requires Python 3.12+.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
fastapi dev mapahead/main.py --port 5000
```

Interactive API docs: http://localhost:5000/docs

### Frontend (old vanilla JS app, until Phase 2 lands)

```bash
cd Frontend
python3 -m http.server 4000
```

Open http://localhost:4000.

## Tests

```bash
cd backend
pytest              # offline tests (default)
pytest -m live      # tests that hit the real Overpass API
pytest -m e2e       # Selenium browser tests; needs Chrome and both servers running
```

## Project structure

```
MapAhead/
├── CLAUDE.md               entry point for AI-assisted work, links to docs/
├── docs/                   vision, architecture, conventions, roadmap, ADRs, concept notes
├── backend/
│   ├── pyproject.toml      package metadata, dependencies, pytest config
│   ├── mapahead/           the Python package (FastAPI app, GPX parsing, routing, Overpass client)
│   └── tests/              unit and integration tests, GPX fixtures
└── Frontend/               old vanilla JS app (replaced by Angular in Phase 2)
```

Architecture, layers and data flow: [docs/01-architecture.md](docs/01-architecture.md).

## API (current)

- `POST /gpx/upload` multipart GPX file (max 2 MB) → `{ route_id, filename, coordinates[] }`
- `GET /pois/{route_id}?max_distance_km=1.0` → `{ markers[], table[] }`

Full schema at `/openapi.json` when the backend runs. Response shapes change in Phase 1.1 (numbers instead of formatted strings).

## Tech

Backend: FastAPI, gpxpy, rtree, haversine, requests. Tests: pytest, responses, FastAPI TestClient. Map data: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) (ODbL), queried via the Overpass API. Map rendering: Leaflet.

## License

MIT. Author: [arcticfade](https://github.com/arcticfade).
