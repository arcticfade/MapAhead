import pytest
from mapahead.geo import haversine_km
from mapahead.route_storage import RouteStorage, Route, RoutePoint

def test_multiple_route_storage():
    """ Test storing multiple routes and retrieving them correctly."""
    storage = RouteStorage()
    points1 = [RoutePoint(lat=10.0, lon=20.0)]
    points2 = [RoutePoint(lat=15.0, lon=25.0)]
    
    route_id1 = storage.store(points1)
    route_id2 = storage.store(points2)
    
    assert route_id1 != route_id2

    route1 = storage.get(route_id1)
    route2 = storage.get(route_id2)
    
    assert route1.points[0].lat == 10.0 # type: ignore
    assert route2.points[0].lat == 15.0 # type: ignore

def test_store():
    """ Test storing a route and verifying its contents."""
    storage = RouteStorage()
    points = [RoutePoint(lat=42, lon=-42) for _ in range(100)]

    route_id = storage.store(points)
    
    assert route_id is not None
    assert storage._routes[route_id].points == points
    assert len(storage._routes[route_id].points) == 100
    assert len(storage._routes) == 1
    assert storage._routes[route_id].id == route_id
    assert isinstance(storage._routes[route_id], Route)

def test_get():
    """ Test retrieving a stored route by its ID."""
    storage = RouteStorage()
    points = [RoutePoint(lat=1, lon=1), RoutePoint(lat=2, lon=2)]
    route_id = storage.store(points)
    
    retrieved_route = storage.get(route_id)

    assert isinstance(retrieved_route, Route)
    assert retrieved_route.id == route_id
    assert retrieved_route.points == points

def test_cumulative_km_one_entry_per_point_starting_at_zero():
    """Prefix sum: same length as points, first entry is the route start."""
    storage = RouteStorage()
    points = [RoutePoint(lat=0, lon=0), RoutePoint(lat=1, lon=1), RoutePoint(lat=2, lon=2)]
    route = storage.get(storage.store(points))

    assert len(route.cumulative_km) == len(points)  # type: ignore
    assert route.cumulative_km[0] == 0.0  # type: ignore


def test_cumulative_km_is_monotonic_and_sums_segments():
    """Last entry equals the sum of all segment lengths."""
    storage = RouteStorage()
    points = [RoutePoint(lat=0, lon=0), RoutePoint(lat=1, lon=1), RoutePoint(lat=2, lon=3), RoutePoint(lat=2, lon=4)]
    route = storage.get(storage.store(points))
    cumulative = route.cumulative_km  # type: ignore

    assert all(a <= b for a, b in zip(cumulative, cumulative[1:]))
    segments = sum(
        haversine_km(a.lat, a.lon, b.lat, b.lon) for a, b in zip(points, points[1:])
    )
    assert cumulative[-1] == pytest.approx(segments)


def test_cumulative_km_single_point_route():
    storage = RouteStorage()
    route = storage.get(storage.store([RoutePoint(lat=1, lon=1)]))

    assert route.cumulative_km == [0.0]  # type: ignore
