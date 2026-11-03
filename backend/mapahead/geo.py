"""
Pure geographic math helpers.

This module imports nothing from `mapahead`, so any other module can use it
without risking a circular import. It works on plain floats rather than
`RoutePoint` for the same reason.
"""
import math

from haversine import haversine

# Mean Earth radius, the same value the `haversine` package uses.
EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points in decimal degrees.

    Returns:
        float: Distance in kilometers.
    """
    return haversine((lat1, lon1), (lat2, lon2))


def project_onto_segment(
    lat: float, lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float,
) -> tuple[float, float]:
    """
    Find the point on segment A->B closest to P(lat, lon).

    Works in a local flat frame centred on P: longitude is scaled by cos(lat)
    so one km east and one km north have the same length. Over the few km of a
    POI's deviation this is accurate to well under a metre.
    See docs/concepts/point-to-segment-projection.md.

    Returns:
        tuple[float, float]: (t, distance_km). t in [0, 1] is the fraction along
        A->B where the closest point lies; distance_km is the distance from P to it.
    """
    km_per_rad_x = EARTH_RADIUS_KM * math.cos(math.radians(lat))

    def to_xy(p_lat: float, p_lon: float) -> tuple[float, float]:
        return (math.radians(p_lon - lon) * km_per_rad_x,
                math.radians(p_lat - lat) * EARTH_RADIUS_KM)

    # P is the origin, so the vector A->P is simply -A.
    ax, ay = to_xy(a_lat, a_lon)
    bx, by = to_xy(b_lat, b_lon)
    abx, aby = bx - ax, by - ay
    length_sq = abx * abx + aby * aby

    if length_sq == 0.0:  # A == B, a zero-length segment
        t = 0.0
    else:
        t = (-ax * abx - ay * aby) / length_sq   # (AP . AB) / (AB . AB)
        t = max(0.0, min(1.0, t))                # clamp onto the segment

    closest_x, closest_y = ax + t * abx, ay + t * aby
    return t, math.hypot(closest_x, closest_y)
