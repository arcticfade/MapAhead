import gpxpy
from Backend.route_storage import Route, RoutePoint
from typing import List


class GPXParser:
    def __init__(self, gpx_data: bytes):
        self.gpx_data = gpx_data

    def parse(self) -> List[RoutePoint]:
        """
        Function to parse the GPX data
        Returns: a list of RoutePoint objects"""
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