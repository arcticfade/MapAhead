"""
HTTP request/response schemas (Pydantic models) for the MapAhead API.

These describe what goes over the wire, not the internal domain objects in
`route_storage.py` and `poi.py`. Keeping the two apart means the domain can
change without breaking the API, and the API contract stays explicit.

Units are part of the field name (`_km`, `_m`) so no client has to guess.
The spec is `tests/integration/test_api.py`; background is in
`docs/concepts/api-contracts-and-errors.md`.

Step 1.8 moves this module to `mapahead/api/`.
"""
from pydantic import BaseModel


class Coordinate(BaseModel):
    """A point in decimal degrees (WGS84)."""
    lat: float
    lon: float


class RouteUploadResponse(BaseModel):
    """Result of `POST /gpx/upload`."""
    route_id: str
    filename: str
    coordinates: list[Coordinate]


class PoiResponse(BaseModel):
    """A single POI along a route.

    Attributes:
        name: OSM name, or None if the node has no `name` tag.
        lat, lon: Position in decimal degrees.
        distance_on_route_km: Distance along the route from the start to the
            route point nearest the POI.
        distance_to_route_m: Direct distance from the POI to the route.
    """
    name: str | None
    lat: float
    lon: float
    distance_on_route_km: float
    distance_to_route_m: float


class PoiListResponse(BaseModel):
    """Result of `GET /pois/{route_id}`, sorted by `distance_on_route_km`."""
    route_id: str
    max_distance_km: float
    pois: list[PoiResponse]
