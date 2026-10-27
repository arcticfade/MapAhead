# Architecture

## System overview

```
┌──────────────┐   HTTP/JSON (OpenAPI)   ┌──────────────────┐   Overpass QL   ┌─────────────┐
│  Angular app │ ──────────────────────▶ │ FastAPI backend  │ ──────────────▶ │ Overpass API│
│  (browser)   │ ◀────────────────────── │ (Python package) │ ◀────────────── │ (OSM data)  │
└──────────────┘                         └──────────────────┘                 └─────────────┘
       │                                          │
       │ tiles                                    │ later: SQLite / Postgres
       ▼                                          ▼
  OSM tile server                            events, routes, supply points
```

Principle: **the backend computes, the frontend presents.** The API returns numbers, IDs and raw tags. Formatting (km, m, links, icons) is the frontend's job.

## Repository layout

```
MapAhead/
├── CLAUDE.md              AI/human entry point, links here
├── docs/                  vision, architecture, conventions, roadmap, ADRs, concept notes
├── backend/               Python package `mapahead` + tests (see below)
├── frontend/              Angular workspace (Phase 2)
├── docker-compose.yml     local full stack (Phase 4)
└── .github/workflows/     CI (Phase 4)
```

## Backend (`backend/`)

Current state after Phase 0: a flat package. The target layout below is reached during Phase 1; modules move when the step that touches them runs.

```
backend/
├── pyproject.toml         package metadata, deps, pytest config
├── mapahead/
│   ├── main.py            FastAPI app, CORS, routes            (Phase 1.8: app factory + routers)
│   ├── gpx_parser.py      GPX bytes -> list[RoutePoint]        (-> services/)
│   ├── geo.py             pure math (haversine_km), no mapahead imports (-> domain/)
│   ├── route_storage.py   RoutePoint, Route (+ cumulative_km), in-memory store   (-> domain/ + services/)
│   ├── route_calculator.py distance and nearest-point helpers  (-> services/)
│   ├── overpass_client.py Overpass HTTP + POI filtering        (-> clients/ + services/)
│   └── poi.py             POI dataclass                        (-> domain/)
└── tests/
    ├── unit/              fast, no network
    ├── integration/       TestClient against the app; some hit the live Overpass API (marker `live`)
    └── files/             GPX fixtures (100 km route, 2 MB route)
```

Target module responsibilities (Phase 1):

| Layer      | Contains                                                | May import      |
|------------|---------------------------------------------------------|-----------------|
| `domain/`  | `RoutePoint`, `Route`, `POI`, `POICategory`. Pure data. | nothing internal |
| `services/`| GPX parsing, route index, distances, POI filtering       | `domain`        |
| `clients/` | Overpass HTTP client. The only place that does network.  | `domain`        |
| `api/`     | Routers + Pydantic request/response schemas              | `services`, `clients`, `domain` |
| `main.py`  | App factory, middleware, router registration             | `api`, `config` |

## Data flow for "show POIs along a route"

1. `POST /gpx/upload`: bytes -> `GPXParser.parse()` -> `RouteStorage.store()` builds an R-tree over the points and returns a `route_id`.
2. `GET /pois/{route_id}?max_distance_km=`: load route -> bounding box (Phase 1.6: corridor) -> Overpass query -> for each element: nearest route point via R-tree, haversine deviation, cumulative km (precomputed prefix sum on `Route.cumulative_km`, a lookup) -> filter by deviation -> sort by km.
3. Frontend draws the polyline and the markers, renders the table.

## API contract

FastAPI generates the OpenAPI document at `/openapi.json` (interactive docs at `/docs`). In Phase 2.2 the Angular client is generated from it. Breaking changes to responses require regenerating the client in the same commit.

Current endpoints:

- `POST /gpx/upload` (multipart, max 2 MB) -> `RouteUploadResponse {route_id, filename, coordinates[{lat, lon}]}`
- `GET /pois/{route_id}?max_distance_km=1.0` (`0 < max_distance_km <= 5`) -> `PoiListResponse {route_id, max_distance_km, pois[]}`; each POI is `{name | null, lat, lon, distance_on_route_km, distance_to_route_m}`, sorted by `distance_on_route_km`. Numbers only, units in the field names.

Error mapping (the HTTP boundary in `main.py` translates; parser and client raise plain Python exceptions, see [concepts/api-contracts-and-errors.md](concepts/api-contracts-and-errors.md)):

| Status | Endpoint | Cause | Raised as |
|---|---|---|---|
| 400 | upload | file name does not end in `.gpx` | `HTTPException` in handler |
| 413 | upload | file larger than 2 MB | `HTTPException` in handler |
| 422 | upload | not parseable as GPX, or no track points | `GPXParseError` |
| 422 | pois | `max_distance_km` out of range | FastAPI `Query` validation |
| 404 | pois | unknown `route_id` | `HTTPException` in handler |
| 502 | pois | Overpass returned an HTTP error or invalid JSON | `OverpassError` |
| 504 | pois | Overpass request timed out | `OverpassTimeoutError` |
| 500 | any | bug in our code | unhandled, FastAPI default |

## Frontend (Phase 2)

Angular 21, standalone components, signals for state, `HttpClient` through a generated API client. Leaflet for the map. Layout:

```
frontend/src/app/
├── core/        generated api client, config, error interceptor
├── features/route/  upload, map, poi-table, category-filter, route store
└── shared/      models, pipes (km, m), small ui pieces
```

## Decisions

See [adr/](adr/). Every decision that is hard to reverse (language, database, hosting, map library) gets one file.
