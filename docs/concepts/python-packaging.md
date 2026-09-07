# Concept: Python packaging with `pyproject.toml`

*Introduced in step 0.4 / 0.5.*

## What it is

A Python **package** is a directory with an `__init__.py` whose modules are imported by a dotted name (`mapahead.gpx_parser`). `pyproject.toml` is the standard file (PEP 621) that tells `pip` what the package is called, what it depends on, and how to build it.

`pip install -e .` installs the package in **editable** mode: Python records a link to the source directory instead of copying it, so edits are visible immediately without reinstalling.

## Why we use it here

The school project made modules importable with a `sys.path.insert(...)` in `tests/conftest.py`. That works on the author's machine and breaks as soon as:

- a test file is run from another directory,
- the code is imported from a second place (a CLI, a worker, a Docker image),
- two modules have the same name as something on the path.

It also mixed test-only dependencies (`pytest`, `selenium`) into the runtime requirements, so a production image would ship a browser driver.

With the package:

- `from mapahead.route_storage import RouteStorage` works everywhere: tests, app, Docker, REPL.
- Runtime deps live in `[project.dependencies]`, dev deps in `[project.optional-dependencies].dev`. Docker installs only the first.
- `pytest` config (`testpaths`, markers, default `-m` filter) lives in the same file, so `pytest` with no arguments does the right thing.

## What to check when reviewing

- No `sys.path` manipulation anywhere.
- Imports use the package name (`mapahead.`), never bare module names.
- A new runtime dependency goes to `dependencies`, a test/lint tool to `dev`.
- After adding a dependency, `pip install -e ".[dev]"` again; the version is pinned.
- `pytest -q` from `backend/` passes offline. Tests needing network carry `@pytest.mark.live`; browser tests carry `@pytest.mark.e2e`.

## Try it

```bash
cd backend
source .venv/bin/activate
python -c "import mapahead, inspect; print(inspect.getfile(mapahead))"   # points into your source tree (editable)
pytest -q            # default: offline tests only
pytest -q -m live    # only the tests that hit the real Overpass API
```
