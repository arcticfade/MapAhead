from rtree import index
from dataclasses import dataclass
import uuid
from typing import List, Dict, Optional
from threading import Lock
from mapahead.geo import haversine_km


@dataclass
class RoutePoint:
    """
    Represents a single geographical point on a route.
    
    Attributes:
        lat (float): Latitude in decimal degrees.
        lon (float): Longitude in decimal degrees.
    """
    lat: float
    lon: float

class Route:
    """
    Represents a complete route with spatial indexing capabilities.
    
    Attributes:
        points (List[RoutePoint]): Ordered list of route points.
        id (str): Unique identifier for the route.
        rtree (index.Index): R-tree spatial index for efficient nearest-neighbor queries.
    """    
    points: List[RoutePoint]
    id: str
    rtree: index.Index
    cumulative_km: List[float]
    def __init__(self, points: List[RoutePoint], id: str, rtree: index.Index):
        self.points = points
        self.id = id
        self.rtree = rtree
        self.cumulative_km = self._build_cumulative_km(points)

    @staticmethod
    def _build_cumulative_km(route: List[RoutePoint]) -> List[float]:
        com_dist = 0.0
        out = [0.0]
        for a, b in zip(route, route[1:]):
            com_dist += haversine_km(a.lat, a.lon, b.lat, b.lon)
            out.append(com_dist)
        return out



class RouteStorage:
    """
    Thread-safe storage for managing multiple routes.
    
    Routes are stored in memory with UUID identifiers. The storage uses
    a lock to ensure thread-safe access in concurrent environments.
    
    Attributes:
        _routes (Dict[str, Route]): Internal dictionary mapping route IDs to Route objects.
        _lock (Lock): Thread lock for concurrent access protection.
    """
    def __init__(self):
        self._routes: Dict[str, Route] = {}
        self._lock = Lock()

    def store(self, points: List[RoutePoint]) -> str:
        """
        Store a new route with automatic spatial indexing.
        
        Creates an R-tree index for efficient spatial queries and generates
        a unique UUID for the route.
        
        Args:
            points (List[RoutePoint]): Ordered list of route points to store.
            
        Returns:
            str: UUID of the stored route.
        """
        route_id = str(uuid.uuid4())

        idx = index.Index()
        for i, point in enumerate(points):
            idx.insert(i,(point.lon,point.lat,point.lon,point.lat))
        
        with self._lock:
            self._routes[route_id] = Route(points=points, id=route_id, rtree = idx)
        print (f"Stored route with ID: {route_id}, Number of points: {len(points)}")
        return route_id
    
    def get(self, route_id: str) -> Optional[Route]:
        """
        Retrieve a stored route by its ID.
        
        Args:
            route_id (str): UUID of the route to retrieve.
            
        Returns:
            Optional[Route]: The Route object if found, None otherwise.
            
        Note:
            This method is thread-safe and can be called concurrently.
        """
        with self._lock:
            return self._routes.get(route_id)
