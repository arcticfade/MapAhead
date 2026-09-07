# ADR 0001: Keep Python + FastAPI for the backend

- **Status:** accepted
- **Date:** 2026-09-07

## Context

The school-project backend is Python 3.12 with FastAPI. The frontend is being rewritten in Angular, which is new to the owner. The owner knows Python and C#, has some C++, and asked whether a different backend would be a "better" fit for the rebuilt app.

## Decision

Keep Python and FastAPI. Refactor the existing modules into an installable package rather than rewriting them.

## Reasons

1. **Learning budget.** Angular is the new thing. Changing the backend language at the same time doubles what is new and slows the frontend learning down.
2. **Geo tooling.** Python has the strongest open geo stack for this job: `gpxpy`, `shapely` (segment projection, buffering a polyline), `rtree`, `pyproj`. C# has NetTopologySuite, which is comparable; Node has `turf.js`, which is thinner.
3. **FastAPI is modern.** Async, Pydantic v2 validation, an automatically generated OpenAPI spec. That spec generates the Angular API client (Phase 2.2), which is a real-world skill and removes hand-written DTO drift.
4. **Existing tests.** 17 fast unit tests with real-world distance assertions and mocked HTTP carry over unchanged.

## Alternatives considered

- **ASP.NET Core (C#).** The strongest alternative given the owner's C# knowledge and the common Angular + .NET pairing in enterprise. Rejected for now because it discards the existing tests and geo libraries and adds a second new framework on top of Angular. Worth revisiting only if the owner's workplace uses exactly this pairing and wants to practise it.
- **Node / NestJS.** One language across the stack, but the geo ecosystem is thinner and the owner has no TypeScript backend experience to build on.
- **Java / Spring Boot.** Heaviest rebuild, most new tooling. Not considered further.

## Consequences

- The OpenAPI document is the contract between frontend and backend. Any backend swap later only has to reproduce that contract.
- Deployment uses a Python container (uvicorn) behind a reverse proxy (Phase 4).
- The owner practises Python packaging, Pydantic and pytest rather than a second framework.
