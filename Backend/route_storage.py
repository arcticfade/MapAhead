from rtree import index
from dataclasses import dataclass
import uuid
from typing import List, Dict, Optional
from threading import Lock

@dataclass
class RoutePoint:
    lat: float
    lon: float

class Route:
    points: List[RoutePoint]
    id: str
    rtree: index.Index
    def __init__(self, points: List[RoutePoint], id: str, rtree: index.Index):
        self.points = points
        self.id = id
        self.rtree = rtree


class RouteStorage:
    def __init__(self):
        self._routes: Dict[str, Route] = {}
        self._lock = Lock()

    def store(self, points: List[RoutePoint]) -> str:
        route_id = str(uuid.uuid4())

        idx = index.Index()
        for i, point in enumerate(points):
            idx.insert(i,(point.lon,point.lat,point.lon,point.lat))
        
        with self._lock:
            self._routes[route_id] = Route(points=points, id=route_id, rtree = idx)
        print (f"Stored route with ID: {route_id}, Number of points: {len(points)}")
        return route_id
    
    def get(self, route_id: str) -> Optional[Route]:
        with self._lock:
            return self._routes.get(route_id)
