import requests 
from dataclasses import dataclass
from typing import List, Dict

class OverpassClient:
    def __init__(self):
        self.api_url = "idk"
    def find_pois(self, route_points: List[Dict], poi_type: str = "amenity=fuel") -> List[Dict]:
        pass
