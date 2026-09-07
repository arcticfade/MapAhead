# Vision

## What MapAhead is for

MapAhead helps organisers and riders plan the **supply side of ultracycling events**: routes of several hundred to a few thousand kilometres, ridden with minimal support, where knowing *where the next water, food, fuel or bed is* matters more than the map itself.

A user uploads a GPX route, chooses which kinds of places they care about, and gets:

- the places along the route, sorted by route kilometre,
- how far each one is off the route (deviation),
- enough detail to decide (opening hours, brand, link to Google Maps / OSM),
- later: a saved plan per event with chosen supply points, notes and exports for the crew.

## Who it is for

- Riders preparing an unsupported or self-supported ultra event.
- Organisers publishing a "resupply guide" alongside a route.
- Support crews who need a list of stops with coordinates.

## Non-goals (for now)

- Route *creation* or turn-by-turn navigation. Komoot, RideWithGPS and Garmin do that; we consume their GPX.
- Live tracking or dot-watching.
- Being a general map app. The map is a viewer for the route and its POIs, nothing more.

## Why this project exists beyond the product

It is also a learning vehicle for the owner:

- Angular (used at work, wants depth): standalone components, signals, HttpClient, testing.
- Backend structure in Python: packaging, Pydantic, clean boundaries, tests.
- Docker, CI and a real deployment.
- Working with AI as a pair: the owner writes the core logic, the AI scaffolds and reviews. See [02-conventions.md](02-conventions.md).

## Origin

Started as a school project (gas stations along a GPX track, FastAPI + vanilla JS). The evaluation of that codebase and the reasons for the rebuild are in [03-roadmap.md](03-roadmap.md) and [adr/0001-keep-fastapi.md](adr/0001-keep-fastapi.md).
