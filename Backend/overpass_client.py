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
        response = requests.post(self.overpass_url, data={"data": overpass_query})
        data = response.json()
        return data 

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


if __name__ == "__main__":
    
    bbox = {
    'north': 52.65,
    'south': 52.33,
    'east': 13.76,
    'west': 13.09
    }
    
    o = OverpassClient(None)
    o.route = Route([
        RoutePoint(lat=52.52, lon=13.405),  # Berlin
        RoutePoint(lat=52.5205, lon=13.409),  # Slightly northeast
        RoutePoint(lat=52.521, lon=13.414)   # Further northeast
    ], "sample_route")

    result = o.query_gas_station(bbox)
    filtered = o.filter_pois(result)
    
    print(filtered)
    print(len(result.get("elements", [])))
    print(len(filtered))

