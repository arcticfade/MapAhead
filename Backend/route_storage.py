from dataclasses import dataclass
import uuid
from typing import List, Dict
from threading import Lock

@dataclass
class RoutePoint:
    lat: float
    lon: float

@dataclass
class Route:
    points: List[RoutePoint]
    id: str

class RouteStorage:
    def __init__(self):
        self._routes: Dict[str, Route] = {}
        self._lock = Lock()

    def store(self, points: List[RoutePoint]) -> str:
        route_id = str(uuid.uuid4())
        with self._lock:
            self._routes[route_id] = Route(points=points, id=route_id)
        print (f"Stored route with ID: {route_id}, Number of points: {len(points)}")
        return route_id
    
    def get(self, route_id: str) -> Route:
        with self._lock:
            return self._routes.get(route_id)
