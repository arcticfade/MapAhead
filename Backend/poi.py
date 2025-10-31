from dataclasses import dataclass

@dataclass
class POI:
    lat: float
    lon: float
    name: str
    distance_to_route: float
    distance_on_route: float