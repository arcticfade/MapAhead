import pytest
from mapahead.route_calculator import RouteCalculator
from mapahead.route_storage import RoutePoint, RouteStorage

route_calculator = RouteCalculator()

def test_haversine_distance_1():
    """
    Test Backend Requirement 3a: Distance calculation between coordinates.
    
    Uses real-world distance Berlin-Paris (878.08 km) verified via luftlinie.org.
    """
    point1 = RoutePoint(lat=52.523403, lon=13.4114)  # Berlin
    point2 = RoutePoint(lat=48.856667, lon=2.350987)   # Paris
    distance = route_calculator.haversine_distance(point1, point2)
    assert round(distance, 2) == 878.08 # https://www.luftlinie.org/Berlin/Paris

def test_haversine_distance_2():
    """
    Test Backend Requirement 3a: Distance calculation between coordinates.
    
    Uses real-world distance LA-NYC (3935.75 km) verified via luftlinie.org.
    """
    point1 = RoutePoint(lat=34.052235, lon=-118.243683)  # Los Angeles
    point2 = RoutePoint(lat=40.712776, lon=-74.005974)   # New York
    distance = route_calculator.haversine_distance(point1, point2)
    assert round(distance, 2) == 3935.75 # https://www.luftlinie.org/Los-Angeles/New-York

def test_haversine_distance_same_point():
    """Test edge case: distance between identical points should be 0."""
    point1 = RoutePoint(lat=-5.123456, lon=42)
    point2 = RoutePoint(lat=-5.123456, lon=42)
    distance = route_calculator.haversine_distance(point1, point2)
    assert round(distance, 2) == 0.00


def test_find_nearest_route_point():
    """
    Test Backend Requirement 3b: Find nearest route point to given coordinate.
    """
    route_storage = RouteStorage()
    route_id = route_storage.store([
        RoutePoint(lat=0, lon=0),  
        RoutePoint(lat=1, lon=1), 
        RoutePoint(lat=2, lon=2),
        RoutePoint(lat=3, lon=3)])
    route = route_storage.get(route_id)

    target_point = RoutePoint(lat=1.1, lon=1.1)  
    nearest_index = route_calculator.find_nearest_route_point_index(route, target_point) # type: ignore
    assert nearest_index == 1  

def test_locate_on_vertex():
    """
    Test Backend Requirement 3a: Calculate cumulative distance along route.

    A point exactly on a vertex (Hamburg) sits 255.65 km along the route, 0 km off it.
    """
    route_storage = RouteStorage()
    route_id = route_storage.store([
        RoutePoint(lat=52.523403, lon=13.4114),  # Berlin
        RoutePoint(lat=53.553406, lon=9.992196),  # Hamburg
        RoutePoint(lat=52.37052, lon=9.73322)   # Hannover
    ])
    route = route_storage.get(route_id)

    match = route_calculator.locate(route, route.points[1])  # type: ignore
    assert round(match.distance_on_route_km, 2) == 255.65  #https://www.luftlinie.org/Berlin,DEU/Hamburg,DEU
    assert match.distance_to_route_km == pytest.approx(0.0, abs=1e-9)


# One degree of latitude (and of longitude on the equator) is ~111.195 km.
KM_PER_DEG = 111.195


def _route(points):
    storage = RouteStorage()
    return storage.get(storage.store(points))


def test_locate_mid_segment():
    """
    The defect 1.3 fixes: a POI 50 m beside a 2.2 km segment, halfway along.

    Nearest-vertex would report ~1.1 km deviation; the segment projection gives 50 m.
    """
    route = _route([RoutePoint(lat=0, lon=0), RoutePoint(lat=0, lon=0.02)])
    poi = RoutePoint(lat=0.05 / KM_PER_DEG, lon=0.01)  # 50 m north of the midpoint

    match = route_calculator.locate(route, poi)  # type: ignore
    assert match.distance_to_route_km == pytest.approx(0.050, abs=0.001)
    assert match.distance_on_route_km == pytest.approx(0.01 * KM_PER_DEG, abs=0.001)


def test_locate_before_start_clamps_to_start():
    """A POI behind the start projects outside the segment (t < 0) and is clamped to km 0."""
    route = _route([RoutePoint(lat=0, lon=0), RoutePoint(lat=0, lon=0.02)])
    poi = RoutePoint(lat=0, lon=-0.01)

    match = route_calculator.locate(route, poi)  # type: ignore
    assert match.distance_on_route_km == pytest.approx(0.0, abs=1e-9)
    assert match.distance_to_route_km == pytest.approx(0.01 * KM_PER_DEG, abs=0.001)


def test_locate_past_end_clamps_to_end():
    """A POI beyond the finish (t > 1) is clamped to the route's total length."""
    route = _route([RoutePoint(lat=0, lon=0), RoutePoint(lat=0, lon=0.02)])
    poi = RoutePoint(lat=0, lon=0.03)

    match = route_calculator.locate(route, poi)  # type: ignore
    assert match.distance_on_route_km == pytest.approx(route.cumulative_km[-1])  # type: ignore
    assert match.distance_to_route_km == pytest.approx(0.01 * KM_PER_DEG, abs=0.001)


def test_locate_hairpin_picks_the_closer_leg():
    """
    Out-and-back with legs 111 m apart: a POI 11 m from the return leg must
    match the return leg (later km), not the outbound one.
    """
    route = _route([
        RoutePoint(lat=0, lon=0),
        RoutePoint(lat=0, lon=0.02),
        RoutePoint(lat=0.001, lon=0.02),
        RoutePoint(lat=0.001, lon=0),
    ])
    poi = RoutePoint(lat=0.0009, lon=0.01)

    match = route_calculator.locate(route, poi)  # type: ignore
    assert match.distance_to_route_km == pytest.approx(0.0001 * KM_PER_DEG, abs=0.001)
    # outbound leg + turn + half the return leg
    assert match.distance_on_route_km == pytest.approx(route.cumulative_km[2] + 0.01 * KM_PER_DEG, abs=0.001)  # type: ignore


def test_locate_single_point_route():
    """A one-point route has no segments: deviation is the distance to that point, km 0."""
    route = _route([RoutePoint(lat=0, lon=0)])
    poi = RoutePoint(lat=0, lon=0.01)

    match = route_calculator.locate(route, poi)  # type: ignore
    assert match.distance_on_route_km == 0.0
    assert match.distance_to_route_km == pytest.approx(0.01 * KM_PER_DEG, abs=0.001)

def test_find_nearest_route_point_first():
    """Test edge case: nearest point is the first route point."""
    route_storage = RouteStorage()
    route_id = route_storage.store([
        RoutePoint(lat=0, lon=0),
        RoutePoint(lat=1, lon=1),
        RoutePoint(lat=2, lon=2)])
    route = route_storage.get(route_id)
    target_point = RoutePoint(lat=-0.1, lon=-0.1)  
    nearest_index = route_calculator.find_nearest_route_point_index(route, target_point) # type: ignore
    assert nearest_index == 0
