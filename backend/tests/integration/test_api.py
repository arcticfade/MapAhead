"""
API contract tests for step 1.1.

These tests are the spec for the HTTP layer:
- responses are typed Pydantic models (visible in the OpenAPI schema),
- distances are numbers in fixed units, never formatted strings,
- errors map to specific status codes instead of a blanket 500.

Overpass is mocked with `responses`, so everything here runs offline.
"""
import pytest
import requests
import responses
from fastapi.testclient import TestClient

from mapahead.main import app

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Three points on the equator, 0.01° of longitude apart (~1.112 km each).
ROUTE_GPX = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><trkseg>
    <trkpt lat="0" lon="0"/>
    <trkpt lat="0" lon="0.01"/>
    <trkpt lat="0" lon="0.02"/>
  </trkseg></trk>
</gpx>"""

EMPTY_GPX = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1">
</gpx>"""

# Deliberately unsorted; one POI has no name, one is far outside the corridor.
OVERPASS_ELEMENTS = {
    "elements": [
        {"type": "node", "id": 2, "lat": 0.0005, "lon": 0.02, "tags": {"amenity": "fuel"}},
        {"type": "node", "id": 1, "lat": 0.001, "lon": 0.01, "tags": {"amenity": "fuel", "name": "Aral"}},
        {"type": "node", "id": 3, "lat": 1.0, "lon": 1.0, "tags": {"amenity": "fuel", "name": "Far away"}},
    ]
}

client = TestClient(app)


def upload(content: bytes = ROUTE_GPX, filename: str = "route.gpx"):
    return client.post("/gpx/upload", files={"file": (filename, content, "application/gpx+xml")})


def upload_route_id() -> str:
    response = upload()
    assert response.status_code == 200
    return response.json()["route_id"]


def response_schema_ref(path: str, method: str) -> str:
    """Return the $ref of the 200 JSON response schema of an endpoint."""
    operation = app.openapi()["paths"][path][method]
    return operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]


# --- Upload: success ------------------------------------------------------------

def test_upload_returns_route_with_coordinates():
    response = upload()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["route_id"], str)
    assert data["filename"] == "route.gpx"
    assert data["coordinates"] == [
        {"lat": 0.0, "lon": 0.0},
        {"lat": 0.0, "lon": 0.01},
        {"lat": 0.0, "lon": 0.02},
    ]


def test_upload_declares_response_model():
    """The Angular client (step 2.2) is generated from these schemas."""
    assert response_schema_ref("/gpx/upload", "post") == "#/components/schemas/RouteUploadResponse"


# --- Upload: errors -------------------------------------------------------------

def test_upload_rejects_non_gpx_extension():
    response = upload(filename="route.txt")
    assert response.status_code == 400


def test_upload_rejects_file_over_2mb():
    """Defect 1: used to come back as 500."""
    too_big = b"x" * (2 * 1024 * 1024 + 1)
    response = upload(content=too_big, filename="big.gpx")
    assert response.status_code == 413


def test_upload_rejects_malformed_gpx():
    """The client sent something we cannot parse: their fault, not a server error."""
    response = upload(content=b"this is not xml", filename="broken.gpx")
    assert response.status_code == 422


def test_upload_rejects_gpx_without_points():
    """A route with zero points is useless; say so instead of storing it."""
    response = upload(content=EMPTY_GPX, filename="empty.gpx")
    assert response.status_code == 422


# --- POIs: success --------------------------------------------------------------

@responses.activate
def test_pois_returns_numbers_in_fixed_units():
    """Defect 2: km and m as numbers; the frontend formats them."""
    responses.post(OVERPASS_URL, json=OVERPASS_ELEMENTS, status=200)
    route_id = upload_route_id()

    response = client.get(f"/pois/{route_id}", params={"max_distance_km": 1.0})

    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == route_id
    assert data["max_distance_km"] == 1.0

    pois = data["pois"]
    assert len(pois) == 2, "the POI at (1, 1) is ~157 km away and must be filtered out"

    aral, unnamed = pois  # sorted by distance along the route
    assert aral["name"] == "Aral"
    assert aral["lat"] == 0.001
    assert aral["lon"] == 0.01
    assert aral["distance_on_route_km"] == pytest.approx(1.112, rel=1e-3)
    assert aral["distance_to_route_m"] == pytest.approx(111.2, rel=1e-3)

    assert unnamed["distance_on_route_km"] == pytest.approx(2.224, rel=1e-3)
    assert unnamed["distance_to_route_m"] == pytest.approx(55.6, rel=1e-3)


@responses.activate
def test_pois_without_osm_name_have_null_name():
    """'Unnamed Gas Station' is presentation (and wrong for other categories)."""
    responses.post(OVERPASS_URL, json=OVERPASS_ELEMENTS, status=200)
    route_id = upload_route_id()

    pois = client.get(f"/pois/{route_id}").json()["pois"]

    assert pois[1]["name"] is None


def test_pois_declares_response_model():
    assert response_schema_ref("/pois/{route_id}", "get") == "#/components/schemas/PoiListResponse"


# --- POIs: errors ---------------------------------------------------------------

def test_pois_unknown_route_is_404():
    response = client.get("/pois/does-not-exist")
    assert response.status_code == 404


@responses.activate  # no mock registered: any Overpass call fails instead of hitting the network
@pytest.mark.parametrize("max_distance_km", [0, -1, 5.1])
def test_pois_rejects_out_of_range_distance(max_distance_km):
    """Valid range is 0 < max_distance_km <= 5. FastAPI can enforce this for you."""
    route_id = upload_route_id()
    response = client.get(f"/pois/{route_id}", params={"max_distance_km": max_distance_km})
    assert response.status_code == 422


@responses.activate
@pytest.mark.parametrize("upstream_status", [400, 406, 429, 500, 503])
def test_pois_overpass_http_error_is_502(upstream_status):
    """Overpass failing is not our server crashing: 502 Bad Gateway."""
    responses.post(OVERPASS_URL, status=upstream_status)
    route_id = upload_route_id()

    response = client.get(f"/pois/{route_id}")

    assert response.status_code == 502


@responses.activate
def test_pois_overpass_timeout_is_504():
    responses.post(OVERPASS_URL, body=requests.exceptions.Timeout())
    route_id = upload_route_id()

    response = client.get(f"/pois/{route_id}")

    assert response.status_code == 504
