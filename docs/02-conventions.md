# Conventions

## How we work (human + AI)

The owner is learning; the AI is a pair, not an autopilot.

- **Who drives.** Each roadmap step names a driver. "Owner" means the owner writes the code and the AI scaffolds (files, tests, config), explains, and reviews. "Claude" means the AI writes it and the owner reviews. Plumbing tends to be Claude; domain and Angular logic tends to be Owner.
- **Test first where it teaches.** For owner-driven steps the AI may write failing tests first; the owner makes them pass.
- **One step, one commit.** A step starts by reading `03-roadmap.md` and ends by ticking its box in the same commit.
- **Concept notes.** Every step that introduces a new idea adds a short note to `docs/concepts/` answering: what is it, why here, what to check when reviewing code that uses it.
- **Docs follow code.** If a change makes a doc wrong, fix the doc in the same commit.
- **Review checklist for the owner** when the AI wrote code: does it match the layer rules in `01-architecture.md`, are errors handled at the boundary not swallowed, is there a test, would I be able to explain this line in a code review at work?

## Python (backend)

- Python 3.12. One installable package `mapahead` under `backend/`. Never `sys.path` hacks.
- Dependencies in `pyproject.toml`; runtime and `[dev]` extras separated. Pin exact versions for now.
- Type hints on every public function. Docstrings: short summary line, then Args/Returns when non-obvious.
- Errors: raise specific exceptions in services/clients; translate to HTTP status codes only in `api/`. Never wrap an `HTTPException` in another `except Exception`.
- Logging via `logging`, never `print`.
- Tests: `pytest`, unit tests offline. Markers: `live` (needs network / real Overpass), `e2e` (needs a browser and running servers). Both are excluded by default (`pyproject.toml`).
- Format/lint: `ruff` (added in Phase 1.7).

## Angular (frontend)

- Angular 21, standalone components only, `inject()` instead of constructor injection, signals for component/store state, RxJS only at the HTTP boundary.
- One feature folder per feature, `core/` for singletons, `shared/` for reusable presentation.
- Never bind untrusted text with `[innerHTML]`. Interpolation only.
- API types come from the generated client; do not hand-write DTOs.
- Tests: unit tests for stores and pipes; component tests for anything with logic.

## Git

- `main` is always green (tests pass).
- Commit messages: imperative subject, optional body explaining *why*. Prefix with the step when applicable, e.g. `1.2: precompute cumulative route distance`.
- Feature branches are optional while the owner works alone; required once CI exists (Phase 4).
