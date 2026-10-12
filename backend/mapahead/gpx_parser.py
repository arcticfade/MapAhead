import gpxpy
from gpxpy.gpx import GPXException
from mapahead.route_storage import RoutePoint
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
        except (GPXException, UnicodeDecodeError)as e: 
            raise GPXParseError(f"Not a valid GPX file: {e}") from e

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    route_points.append(RoutePoint(lat=point.latitude, lon=point.longitude))
        if not route_points:
            raise GPXParseError("GPX file contains no track points.")
        return route_points


class GPXParseError(ValueError):
    """The uploaded data is not a usable GPX route."""

