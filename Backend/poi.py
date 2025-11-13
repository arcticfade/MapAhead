from dataclasses import dataclass

@dataclass
class POI:
    """Point of Interest (POI) data class"""
    lat: float
    lon: float
    name: str
    distance_to_route: float
    distance_on_route: float