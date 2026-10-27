# Roadmap

The living plan. Find the first unchecked step, do it, tick it in the same commit. "Drives" = who writes the code; the other reviews (see [02-conventions.md](02-conventions.md)).

## Evaluation of the school project (2026-09-07)

Verdict: the domain logic (parse, index, query, filter, sort) is a sound seed. The HTTP layer, the vanilla-JS frontend and the repo layout get rebuilt. Defects found, each mapped to the step that fixes it:

| # | Where (pre-refactor path) | Problem | Fixed in |
|---|---|---|---|
| 1 | `main.py` upload/pois handlers | `except Exception` swallows the `HTTPException(413)`, so oversized files return 500. | 1.1 |
| 2 | `main.py` pois response | API returns display strings (`"5.2 km"`, `"120m"`) instead of numbers. | 1.1 |
| 3 | `route_calculator.calculate_distance_on_route` | Walks the route from index 0 per POI: O(n·m). | 1.2 |
| 4 | `route_calculator.find_nearest_route_point_index` | Nearest *vertex*, not nearest point on the *segment*; overestimates deviation on sparse routes. | 1.3 |
| 5 | `overpass_client.get_route_bounding_box` | One bbox around the whole route; a 1000 km route queries a whole country. | 1.6 |
| 6 | `overpass_client` | Hard-coded `http://` URL and `amenity=fuel`; no category abstraction. | 1.5, 1.6, 1.7 |
| 7 | `gpx_parser` | Only `<trk>` read; `<rte>` files yield an empty route silently. | 1.4 |
| 8 | `route_storage` | In-memory only; restart loses everything. | 3.3 |
| 9 | `script.js` | Old markers never removed on a second upload. | 2.5 |
| 10 | `script.js` | POI names into `innerHTML` unescaped (XSS from OSM data). | 2.6 |
| 11 | `script.js` | API URL hard-coded; non-200 responses unhandled. | 2.1, 2.8 |
| 12 | `tests/conftest.py`, `requirements.txt` | `sys.path` hack; test deps mixed with runtime deps. | 0.4 |
| 13 | `route_storage` | `print` instead of logging; no config. | 1.7 |
| 14 | `README.md`, `index.html` credits | Library versions out of date. | 2.10 |

## Phase 0: Foundations

- [x] 0.1 Create `docs/` (vision, architecture, conventions, domain, roadmap). *Claude*
- [x] 0.2 Root `CLAUDE.md`. *Claude*
- [x] 0.3 ADR 0001: keep Python + FastAPI. *Claude*
- [x] 0.4 Backend as installable package `backend/mapahead` with `pyproject.toml`; tests moved to `backend/tests`; `sys.path` hack removed; runtime/dev deps split; `live`/`e2e` markers; all offline tests green. *Claude*
- [x] 0.5 Concept note: [concepts/python-packaging.md](concepts/python-packaging.md). *Claude*

## Phase 1: Backend refactor and bug fixes

- [x] 1.1 Pydantic response schemas returning numbers; fix 413-becomes-500. Claude writes failing tests, owner makes them pass. *Owner*
  - Spec: `backend/tests/integration/test_api.py`. Work in `mapahead/schemas.py`, `main.py`, and where needed `overpass_client.py` / `gpx_parser.py`. Concept: [concepts/api-contracts-and-errors.md](concepts/api-contracts-and-errors.md).
  - [x] Schemas in `mapahead/schemas.py` (owner draft, finished by Claude after review: `BaseModel`, unit-suffixed field names, `PoiResponse` kept apart from domain `POI`).
  - [x] Wire `response_model` into `main.py`, return numbers.
  - [x] `name: None` for unnamed POIs (fix the "Unnamed" fallback at its source in `overpass_client.py`).
  - [x] 413 out of the broad `except`.
  - [x] Malformed or empty GPX → 422 via `GPXParseError` in `gpx_parser.py`, mapped in `main.py`.
  - [x] `max_distance_km` range via `Query` (0 < x <= 5); Overpass HTTP error → 502, timeout → 504 (`OverpassError`, `OverpassTimeoutError`).
  - [x] API contract section of `01-architecture.md` updated.
  - [x] Adapt the old `Frontend/static/script.js` to the new response (Claude).
  - Done when: `pytest -q` is green; the API contract section of `01-architecture.md` is updated; the old `Frontend/script.js` is adapted to the new response (Claude, it is throwaway).
- [x] 1.2 Precompute cumulative distance on store; `distance_on_route` becomes a lookup. *Owner*
  - [x] `mapahead/geo.py` leaf module for `haversine_km`, so `route_storage` and `route_calculator` share it without a circular import (Claude).
  - [x] `Route.cumulative_km` prefix sum, `calculate_distance_on_route` as lookup (owner). Tests: `tests/unit/test_route_storage.py`, `test_geo.py`.
- [ ] 1.3 Nearest point on segment (shapely projection). Concept note: haversine vs local metric projection. *Owner*
- [ ] 1.4 Parse `<rte>` and `<wpt>` in addition to `<trk>`. *Owner*
- [ ] 1.5 `POICategory` registry (fuel, supermarket, drinking_water, bakery, bicycle shop, restaurant, pharmacy, ATM, hotel, toilets); `GET /api/categories`. *Owner*
- [ ] 1.6 Overpass query from selected categories; corridor query instead of whole-route bbox. Concept note: Overpass QL, rate limits, caching. *Owner*
- [ ] 1.7 `config.py` with pydantic-settings; `logging`; `ruff`. *Claude*
- [ ] 1.8 `/api` prefix, `GET /api/health`, OpenAPI tags. Split into `domain/ services/ clients/ api/`. Concept note: OpenAPI. *Claude*

## Phase 2: Angular frontend MVP

- [ ] 2.1 `ng new frontend` (standalone, routing, SCSS, strict); environments for API base URL. Concept note: workspace anatomy, standalone, signals vs RxJS. *Claude*
- [ ] 2.2 Generate API client from OpenAPI into `core/api/`. Concept note: contract-first. *Claude*
- [ ] 2.3 `RouteStore` (signals): route, POIs, selected categories, loading, error. *Owner*
- [ ] 2.4 `UploadComponent` with validation. *Owner*
- [ ] 2.5 `MapComponent`: Leaflet lifecycle, `effect()` redraw, clears old layers. *Owner*
- [ ] 2.6 `PoiTableComponent`, `KmPipe`, `MetersPipe`, row click pans map. *Owner*
- [ ] 2.7 `CategoryFilterComponent`. *Owner*
- [ ] 2.8 HTTP error interceptor + toast. *Owner*
- [ ] 2.9 Unit tests: store, pipes, table component. Concept note: testing with signals. *Claude scaffolds, owner fills*
- [ ] 2.10 Delete `Frontend/`, update README. *Claude*

## Phase 3: Planning features

- [ ] 3.1 Google Maps / OSM links per POI. *Owner*
- [ ] 3.2 POI details from tags (opening hours, brand, website, phone). *Owner*
- [ ] 3.3 Persistence: SQLite + SQLModel + Alembic; `Event`, `Route`, `SupplyPoint`. Concept note: ORM, migrations, repositories. *Claude scaffolds, owner writes repo + endpoints*
- [ ] 3.4 Angular: event list/detail, mark supply points, notes; lazy-loaded route. *Owner*
- [ ] 3.5 Export supply points as GPX waypoints and CSV. *Owner*
- [ ] 3.6 Elevation profile and km markers (nice to have). *Owner*

## Phase 4: Docker, CI, deployment

- [ ] 4.1 Install Docker; `backend/Dockerfile` (multi-stage, non-root). Concept note: images, layers, multi-stage. *Claude writes, owner rebuilds by hand*
- [ ] 4.2 `frontend/Dockerfile` (Node build, nginx serve, proxy `/api`). *Owner with template*
- [ ] 4.3 `docker-compose.yml`. *Owner*
- [ ] 4.4 GitHub Actions: pytest, ng test, ng build, docker build. *Claude*
- [ ] 4.5 Deploy (Fly.io or Hetzner VPS + Caddy); Postgres. Concept note: env, secrets, reverse proxy, TLS. *Owner with guide*
- [ ] 4.6 Overpass result cache + rate limiting. *Owner*

## Phase 5: Hardening (once public)

- [ ] Auth if events are per user.
- [ ] Self-hosted Overpass or POI mirror if usage grows.
- [ ] Monitoring and error reporting.
