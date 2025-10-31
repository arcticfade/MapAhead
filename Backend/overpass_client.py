import requests 
from typing import List, Dict
from route_storage import RoutePoint, Route
from route_calculator import RouteCalculator    
from poi import POI

class OverpassClient:
    def __init__(self, route: Route):
        self.overpass_url = "http://overpass-api.de/api/interpreter"
        self.route = route
        self.route_calculator = RouteCalculator()

    def get_route_bounding_box(self, buffer_km: float = 1.0) -> dict:
        min_lat = min(point.lat for point in self.route.points)
        max_lat = max(point.lat for point in self.route.points)
        min_lon = min(point.lon for point in self.route.points)
        max_lon = max(point.lon for point in self.route.points)
        buffer_deg = buffer_km / 111.0
        return {
            "south": min_lat - buffer_deg,
            "north": max_lat + buffer_deg,
            "west": min_lon - buffer_deg,
            "east": max_lon + buffer_deg
        }

    def query_gas_station(self, bbox: dict):
        overpass_query = f"""
        [out:json];
        (
        node["amenity"="fuel"]({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        );
        out body;
        >;
        out skel qt;
        """
        try:    
            response = requests.post(self.overpass_url, data={"data": overpass_query}, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise TimeoutError("Overpass API request timed out.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Overpass API request failed: {str(e)}")

    def filter_pois(self, overpass_poi_data: dict, max_distance_to_route_km: float = 1.0) -> List[Dict]:
        filtered_pois = []
        for element in overpass_poi_data.get("elements", []):
            poi_point = RoutePoint(lat=element['lat'], lon=element['lon'])
            # find nearest point on route
            nearest_point_on_route_index = self.route_calculator.find_nearest_route_point_index(self.route, poi_point)
            nearest_route_point = self.route.points[nearest_point_on_route_index]
            
            distance_to_route_km = self.route_calculator.haversine_distance(poi_point, nearest_route_point)
            if distance_to_route_km <= max_distance_to_route_km:
                distance_along_route = self.route_calculator.calculate_distance_on_route(self.route, nearest_route_point)
            
                name = element.get("tags", {}).get("name")


                poi = POI(
                    lat=element['lat'],
                    lon=element['lon'],
                    name=name if name else "Unnamed Gas Station",
                    distance_to_route=distance_to_route_km,
                    distance_on_route=distance_along_route
                )
                filtered_pois.append(poi)
        filtered_pois.sort(key=lambda poi: poi.distance_on_route)

        return filtered_pois