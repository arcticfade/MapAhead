from dataclasses import dataclass
from typing import Optional
@dataclass
class POI:
    """Represents a Point of Interest (POI) 
    
    Attributes:
        lat (float): Latitude of the POI in decimal degrees.
        lon (float): Longitude of the POI in decimal degrees.
        name (str): Display name of the POI.
        distance_to_route (float): Direct perpendicular distance from POI to nearest route point in kilometers.
        distance_on_route (float): Cumulative distance along the route from start to the nearest point in kilometers.
    """
    lat: float
    lon: float
    name: Optional[str]
    distance_to_route: float
    distance_on_route: float