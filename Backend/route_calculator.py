from route_storage import RoutePoint, Route
from haversine import haversine
from typing import List

class RouteCalculator:
    def haversine_distance(self, point1: RoutePoint, point2: RoutePoint) -> float:
        """
        Calculate the Haversine distance between two RoutePoints.
        Returns: Distance in kilometers.
        """
        return haversine((point1.lat, point1.lon), (point2.lat, point2.lon))

    def find_nearest_route_point_index(self, route: Route, poi_point: RoutePoint) -> int:
        """
        Find the nearest point on the route to the poi point.
        Returns: The nearest RoutePoint on the route.
        """
        nearest_index = -1
        min_distance = float('inf')
        for index, route_point in enumerate(route.points):
            distance = self.haversine_distance(route_point, poi_point)
            if distance < min_distance:
                min_distance = distance
                nearest_index = index
        return nearest_index
    
    def calculate_distance_on_route(self, route: Route, point: RoutePoint) -> float:
        """
        Calculate the distance along the route to the specified point.
        Returns: Distance in kilometers.
        """
        index = self.find_nearest_route_point_index(route, point)
        distance = 0.0
        for i in range(index):
            distance += self.haversine_distance(route.points[i], route.points[i + 1])
        return distance
    
