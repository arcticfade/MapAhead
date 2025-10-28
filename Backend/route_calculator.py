from typing import List, Tuple
from route_storage import RoutePoint
from math import radians, sin, cos, sqrt, atan2
from haversine import haversine

class RouteCalculator:
    @staticmethod
    def haversine_distance(point1: RoutePoint, point2: RoutePoint) -> float:
        """
        Calculate the Haversine distance between two RoutePoints.
        Returns: Distance in kilometers.
        """
        return haversine((point1.lat, point1.lon), (point2.lat, point2.lon))

