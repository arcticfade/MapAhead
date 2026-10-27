"""
Pure geographic math helpers.

This module imports nothing from `mapahead`, so any other module can use it
without risking a circular import. It works on plain floats rather than
`RoutePoint` for the same reason.
"""
from haversine import haversine


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points in decimal degrees.

    Returns:
        float: Distance in kilometers.
    """
    return haversine((lat1, lon1), (lat2, lon2))
