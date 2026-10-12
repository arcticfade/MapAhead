# Concept: API contracts with Pydantic, and mapping errors to status codes

*Introduced in step 1.1.*

## 1. Response models are the contract

A FastAPI endpoint can return a plain `dict`. It works, but nobody can tell what the dict contains without reading the function. A **response model** is a Pydantic class that describes the shape:

```python
from pydantic import BaseModel

class Bike(BaseModel):
    id: str
    weight_kg: float
    nickname: str | None      # may be missing

@app.get("/bikes/{bike_id}", response_model=Bike)   # or: -> Bike as return annotation
def get_bike(bike_id: str) -> Bike:
    return Bike(id=bike_id, weight_kg=8.4, nickname=None)
```

What you get for declaring it:

- **Validation on the way out.** If the function returns something that does not match (a string where a float belongs), FastAPI fails loudly in development instead of sending garbage.
- **Filtering.** Fields not in the model are not sent, so internal data cannot leak by accident.
- **Documentation.** The model appears in `/openapi.json` under `components/schemas/Bike` and in `/docs`. In step 2.2 the Angular client and its TypeScript interfaces are **generated** from this. The name of the class becomes the name of the TypeScript type, so pick names you want to read in Angular.

Where they live: `mapahead/schemas.py`. These are *API* shapes. The dataclasses in `poi.py` and `route_storage.py` are *domain* shapes. Converting one into the other in the endpoint is normal and intended.

Nested models just work: a field of type `list[Coordinate]` becomes a JSON array of objects.

## 2. Numbers, not strings; `None`, not "Unnamed"

The school API returned `"distance": "5.2 km"`. Problems:

- The frontend cannot sort, filter or sum `"5.2 km"` without parsing it back.
- Units and rounding are a display decision (km or mi? one decimal or none?). The frontend owns display.

Rule: **put the unit in the field name and send a number**: `distance_on_route_km: float`, `distance_to_route_m: float`. No rounding in the backend.

Same for names: `"Unnamed Gas Station"` is a display text, and it is wrong the moment a POI is a supermarket (step 1.5). The honest value is "OSM has no name", which is `None` in Python and `null` in JSON. The frontend decides what to show.

## 3. Errors: say *whose* fault it is

A status code tells the client what went wrong and whether retrying helps.

| Situation | Status | Why |
|---|---|---|
| Not a `.gpx` file | 400 Bad Request | client sent the wrong thing |
| File larger than 2 MB | 413 Content Too Large | specific code exists, use it |
| GPX cannot be parsed, or has no points | 422 Unprocessable Content | well-formed request, unusable content |
| Query parameter out of range | 422 | FastAPI does this for you (see below) |
| Unknown `route_id` | 404 Not Found | |
| Overpass returned an error | 502 Bad Gateway | *we* are fine, the service behind us is not |
| Overpass timed out | 504 Gateway Timeout | same, but "try again later" |
| Bug in our code | 500 Internal Server Error | the only case that should be 500 |

The school code wrapped everything in `except Exception` and returned 500. That tells the client nothing, hides bugs, and has a nasty side effect: `HTTPException` *is* an `Exception`, so an intentional `HTTPException(413)` raised inside the `try` gets caught and replaced by a 500.

**The layer rule:** services and clients raise *specific* Python exceptions (`ValueError`, `TimeoutError`, `ConnectionError`, or later our own). Only the endpoint (the HTTP boundary) translates them into status codes. `gpx_parser.py` should never know what a 422 is.

Two ways to do the translation in FastAPI:

1. **Specific `except` clauses in the endpoint.** Catch exactly what you expect, re-raise as `HTTPException(status_code=..., detail=...)`. Let anything else propagate: FastAPI turns an unhandled exception into a 500 by itself.
2. **Exception handlers** registered once on the app (`@app.exception_handler(TimeoutError)`). Less repetition when many endpoints share the mapping.

For two endpoints, option 1 is clearer. Keep option 2 in mind for step 1.8.

Watch out:

- `TimeoutError` and `ConnectionError` are both subclasses of `OSError`. Catching `OSError` would lump a timeout (504) together with an unreachable server (502). Name the exact classes.
- Look at what `overpass_client.py` raises for an upstream 400 or broken JSON: `ValueError`, the same class the GPX parser raises for a broken file. One built-in exception now means two very different things. A small custom exception (e.g. `class OverpassError(Exception)`) in the client makes the endpoint code unambiguous. Your call; the tests only check status codes.

## 4. Validating query parameters declaratively

Instead of `if max_distance_km <= 0: raise ...`, let FastAPI do it:

```python
from fastapi import Query

def get_bikes(max_weight_kg: float = Query(default=10.0, gt=0, le=20)): ...
```

Out-of-range values get a 422 with a precise message, and the limits show up in the OpenAPI schema (and later in the generated Angular client). `Annotated[float, Query(gt=0, le=20)] = 10.0` is the newer spelling of the same thing.

## 5. A hint for the 413 bug

Read what `UploadFile.read(size)` returns when the file is bigger than `size`. Then look at the `if` right after it. How could `len(gpx_data)` ever be larger than `MAX_FILE_SIZE_BYTES`?

## What to check when reviewing

- Every endpoint has a `response_model` (or return annotation) with a meaningful class name.
- Field names carry units; values are numbers; missing data is `None`, not a placeholder string.
- No `except Exception` around code that raises `HTTPException`.
- Every `except` names a specific exception and maps it to a status code that says whose fault it is.
- Parsing and network code raise Python exceptions, never `HTTPException`.
- `detail` messages help the client but do not leak stack traces or internal paths.
