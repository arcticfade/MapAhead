from route_calculator import RouteCalculator
from route_storage import RoutePoint, Route

route_calculator = RouteCalculator()

def test_haversine_distance_1():
    point1 = RoutePoint(lat=52.523403, lon=13.4114)  # Berlin
    point2 = RoutePoint(lat=48.856667, lon=2.350987)   # Paris
    distance = route_calculator.haversine_distance(point1, point2)
    assert round(distance, 2) == 878.08 # https://www.luftlinie.org/Berlin/Paris

def test_haversine_distance_2():
    point1 = RoutePoint(lat=34.052235, lon=-118.243683)  # Los Angeles
    point2 = RoutePoint(lat=40.712776, lon=-74.005974)   # New York
    distance = route_calculator.haversine_distance(point1, point2)
    assert round(distance, 2) == 3935.75 # https://www.luftlinie.org/Los-Angeles/New-York

def test_haversine_distance_same_point():
    point1 = RoutePoint(lat=-5.123456, lon=42)
    point2 = RoutePoint(lat=-5.123456, lon=42)
    distance = route_calculator.haversine_distance(point1, point2)
    assert round(distance, 2) == 0.00


def test_find_nearest_route_point():
    route = Route([
        RoutePoint(lat=0, lon=0),  
        RoutePoint(lat=1, lon=1), 
        RoutePoint(lat=2, lon=2),
        RoutePoint(lat=3, lon=3)],
    "test_route")

    target_point = RoutePoint(lat=1.1, lon=1.1)  
    nearest_index = route_calculator.find_nearest_route_point_index(route, target_point)
    assert nearest_index == 1  

def test_calculate_distance_on_route():
    route = Route([
        RoutePoint(lat=52.523403, lon=13.4114),  # Berlin
        RoutePoint(lat=53.553406, lon=9.992196),  # Hamburg
        RoutePoint(lat=52.37052, lon=9.73322)   # Hannover
    ],"test_route_2")

    distance = route_calculator.calculate_distance_on_route(route, route.points[1])  
    assert round(distance, 2) == 255.65  #https://www.luftlinie.org/Berlin,DEU/Hamburg,DEU