from overpass_client import OverpassClient, RoutePoint, Route, POI
import pytest
import responses

def test_overpass_client_creation():
    o = OverpassClient(Route(points=[RoutePoint(-2,-2), RoutePoint(-1,3), RoutePoint(2,2)], id="test"))
    assert isinstance(o, OverpassClient)
    assert o.overpass_url == "http://overpass-api.de/api/interpreter"

def test_get_route_bounding_box():
    o = OverpassClient(Route(points=[RoutePoint(-2.0,-2.0), RoutePoint(-1.0,3.0), RoutePoint(2.0,2.0)], id="test"))
    bbox = o.get_route_bounding_box(buffer_km=0.0)
    assert bbox == {            
            "south": -2.0,
            "north": 2.0,
            "west": -2.0,
            "east": 3.0}
    
def test_filter_pois():
    route = Route(points=[RoutePoint(0,0), RoutePoint(0,1), RoutePoint(1,1)], id="test")
    
    o = OverpassClient(route)
    
    overpass_data = {
        "elements": [
            {"type": "node", "id": 1, "lat": 0.001, "lon": 0.001, "tags": {"amenity": "fuel", "name": "Gas Station 1"}},
            {"type": "node", "id": 2, "lat": 5.0, "lon": 5.0, "tags": {"amenity": "fuel", "name": "Gas Station 2"}},
        ]
    }
    
    filtered_pois = o.filter_pois(overpass_data, max_distance_to_route_km=2.0)
    
    assert len(filtered_pois) == 1
    assert filtered_pois[0].lat == 0.001
    assert filtered_pois[0].lon == 0.001
    assert filtered_pois[0].name == "Gas Station 1"

@pytest.fixture
def overpass_client():
    return OverpassClient(route=None)
@pytest.fixture
def bbox():
    return {
        "south": 47.3700,
        "north": 47.3850,
        "west": 8.5300,
        "east": 8.5600
    }

@responses.activate
def test_sucessfull(overpass_client , bbox):
    # Mock Overpass API endpoint
    responses.post("http://overpass-api.de/api/interpreter",
                   json={
                       "elements" : [
                            {
                                "type": "node",
                                "id": 123456,
                                "lat": 47.3769,
                                "lon": 8.5417,
                                "tags": {
                                    "amenity": "fuel",
                                    "name": "Shell",
                                    "operator": "Shell"
                                }
                            },
                            {
                                "type": "node",
                                "id": 789012,
                                "lat": 47.3800,
                                "lon": 8.5450,
                                "tags": {
                                    "amenity": "fuel",
                                    "name": "BP"
                                }
                            }
                       ]
                       },
                    status = 200
                    )

    results = overpass_client.query_gas_station(bbox)
    assert "elements" in results
    assert responses.calls[0].response.status_code == 200
    assert len(results["elements"]) == 2


@responses.activate
def test_rate_limiting_error(overpass_client, bbox):
    responses.post(
        "http://overpass-api.de/api/interpreter",
        json = {"error" : "Rate limit exceed"},
        status = 429
    )
    with pytest.raises(ConnectionError, match="Overpass API rate limit exceeded."):
        overpass_client.query_gas_station(bbox)
        
@responses.activate
def test_empty_results(overpass_client, bbox):
    responses.post(
        "http://overpass-api.de/api/interpreter",
        json={"elements" : []},
        status=200        
    )
    results = overpass_client.query_gas_station(bbox)
    assert results["elements"] == []

@responses.activate 
def test_invalid_json(overpass_client, bbox):
    responses.post(
        "http://overpass-api.de/api/interpreter",
        body='{"invalid":',
        status = 200)
    with pytest.raises(ValueError):
        overpass_client.query_gas_station(bbox)