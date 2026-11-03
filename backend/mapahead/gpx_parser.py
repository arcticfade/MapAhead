import gpxpy
from gpxpy.gpx import GPXException
from mapahead.route_storage import RoutePoint
from typing import List

class GPXParser:
    """
    A class to parse GPX data and extract route points.

    Reads <trk> if present, else <rte>. <wpt>-only files are rejected.

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

            Raises:
                GPXParseError: Invalid GPX, or no track/route points.
        """
        try:
            gpx = gpxpy.parse(self.gpx_data.decode('utf-8'))
        except (GPXException, UnicodeDecodeError) as e:
            raise GPXParseError(f"Not a valid GPX file: {e}") from e

        # Precedence: track, then route. Waypoints have no defined order, so
        # they never form a route.
        if any(seg.points for t in gpx.tracks for seg in t.segments):
            points = (p for t in gpx.tracks for s in t.segments for p in s.points)
        elif any(r.points for r in gpx.routes):
            points = (p for r in gpx.routes for p in r.points)
        else:
            points = ()

        route_points = [RoutePoint(lat=p.latitude, lon=p.longitude) for p in points]
        if not route_points:
            if gpx.waypoints:
                raise GPXParseError(
                    "GPX file contains only waypoints; a track or route is required."
                )
            raise GPXParseError("GPX file contains no track or route points.")
        return route_points


class GPXParseError(ValueError):
    """The uploaded data is not a usable GPX route."""

