import gpxpy
from route_storage import RoutePoint
from typing import List

class GPXParser:
    """
    A class to parse GPX data and extract route points.

    Attributes: 
        gpx_data (bytes): The GPX data in bytes format.

    Methods:
        parse() -> List[RoutePoint]:
            Parse the GPX data and extract route points.

    """
    def __init__(self, gpx_data: bytes):
        self.gpx_data = gpx_data

    def parse(self) -> List[RoutePoint]:
        """
        Parse the GPX data and extract route points.

            Args: 
                gpx_data (bytes): The GPX data in bytes format.
    
            Returns:
                List[RoutePoint]: A list of RoutePoint objects extracted from the GPX data. 
        """
        try:
            gpx = gpxpy.parse(self.gpx_data.decode('utf-8'))
            route_points = []

            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        route_points.append(RoutePoint(lat=point.latitude, lon=point.longitude))
            return route_points
        
        except Exception as e:
            raise ValueError(f"Failed to parse GPX data: {str(e)}")