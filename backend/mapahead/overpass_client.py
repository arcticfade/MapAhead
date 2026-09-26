import requests 
from typing import List 
from mapahead.route_storage import RoutePoint, Route
from mapahead.route_calculator import RouteCalculator    
from mapahead.poi import POI

class OverpassClient:
    """ 
    Client to interact with the Overpass API for querying POIs along a route. 
    
        Attributes:
            overpass_url (str): The URL of the Overpass API endpoint.  
            route (Route): The route for which to query POIs.
            route_calculator (Route Calculator): Utility for route calculations.
 
        Methods:
            get_route_bounding_box(buffer_km: float) -> dict:
                Calculate a bounding box around the route with optional buffer.    
            query_gas_station(bbox: dict) -> dict:
                Query the Overpass API for gas stations within the given bounding box.
            filter_pois(overpass_poi_data: dict, max_distance_to_route_km: float) -> List[POI]:
                Filter POIs based on their distance to the route. 
    """

    def __init__(self, route: Route):
        self.overpass_url = "http://overpass-api.de/api/interpreter"
        self.route = route
        self.route_calculator = RouteCalculator()

    def get_route_bounding_box(self, buffer_km: float = 1.0) -> dict:
        """ 
        Calculate a bounding box around the route with optional buffer. 

            Args:
                buffer_km (float): Buffer distance in kilometers to expand the bounding box. Default is 1.0 km. 
            Returns:
                dict: A dictionary representing the bounding box with keys 'south', 'north', 'west', 'east'.
        """
        min_lat = min(point.lat for point in self.route.points)
        max_lat = max(point.lat for point in self.route.points)
        min_lon = min(point.lon for point in self.route.points)
        max_lon = max(point.lon for point in self.route.points)
        conversion_factor = 111.0  # Approximate conversion from km to degrees
        buffer_deg = buffer_km / conversion_factor
        return {
            "south": min_lat - buffer_deg,
            "north": max_lat + buffer_deg,
            "west": min_lon - buffer_deg,
            "east": max_lon + buffer_deg
        }

    def query_gas_station(self, bbox: dict):
        """
        Query the Overpass API for gas stations within the given bounding box.
            Args:
                bbox (dict): A dictionary representing the bounding box with keys 'south', 'north', 'west', 'east'.
            Returns:
                dict: The JSON response from the Overpass API containing POI data.            
         """
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
            response = requests.post(
                self.overpass_url, 
                headers={"User-Agent": "MapAhead/0.1 (github.com/arcticfade/MapAhead)"},
                data={"data": overpass_query}, 
                timeout=30,
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise TimeoutError("Overpass API request timed out.")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 429:
                raise ConnectionError("Overpass API rate limit exceeded.")
            elif status_code == 400: 
                raise ValueError(f"Bad request to Overpass API: {str(e)}")
            elif status_code >= 500 and status_code < 600:
                raise ConnectionError(f"Overpass API server error: {str(e)}")
            else: 
                raise ConnectionError(f"Overpass API HTTP error {status_code}: {str(e)}")
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Overpass API: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Overpass API connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Overpass API request failed: {str(e)}")

    def filter_pois(self, overpass_poi_data: dict, max_distance_to_route_km: float = 1.0) -> List[POI]:
        """
        Filter POIs based on their distance to the route. 
            
            Args:
                overpass_poi_data (dict): The JSON response from the Overpass API containing POI data.
                max_distance_to_route_km (float): Maximum distance in kilometers from the route to include a POI. Default is 1.0 km.
            Returns:
                List[POI]: A list of filtered POIs with their details and distances.
        """    
        filtered_pois = []
        for element in overpass_poi_data.get("elements", []):
            poi_point = RoutePoint(lat=element['lat'], lon=element['lon'])
            # find the nearest point on route relative to the poi
            nearest_point_on_route_index = self.route_calculator.find_nearest_route_point_index(self.route, poi_point)
            nearest_route_point = self.route.points[nearest_point_on_route_index]
            # calculate direct distance to route
            distance_to_route_km = self.route_calculator.haversine_distance(poi_point, nearest_route_point)
            # only include poi if within max distance
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
        # sort the pois by distance along the route
        filtered_pois.sort(key=lambda poi: poi.distance_on_route)
        return filtered_pois
    
    