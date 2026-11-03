from dataclasses import dataclass
from mapahead.route_storage import RoutePoint, Route
from mapahead.geo import haversine_km, project_onto_segment

# How many nearest vertices to take as candidates. More than one, so a hairpin
# where the closest vertex belongs to the wrong leg still finds the right segment.
CANDIDATE_VERTICES = 5


@dataclass
class RouteMatch:
    """
    Where a point sits relative to a route.

    Attributes:
        distance_to_route_km (float): Shortest distance from the point to the route (deviation).
        distance_on_route_km (float): Distance from the route start to the closest point on the route.
    """
    distance_to_route_km: float
    distance_on_route_km: float


class RouteCalculator:
    """
    Helpers for route calculations such as distance an nearest point. 
    """
    def haversine_distance(self, point1: RoutePoint, point2: RoutePoint) -> float:
        """
        Calculate the Haversine distance between two RoutePoints via `geo.haversine_km`.
        Args: 
            point1 (RoutePoint): The first route point.
            point2 (RoutePoint): The second route point. 
        Returns: 
            float: Distance in kilometers.
        """
        return haversine_km(point1.lat, point1.lon, point2.lat, point2.lon)

    def find_nearest_route_point_index(self, route: Route, poi_point: RoutePoint) -> int:
        """
        Find the nearest point on the route to the poi point.
        Args:
            route (Route): Route object containing route points.
            poi_point (RoutePoint): The target point.
        Returns:
            int: Index of the nearest route point
        """
        nearest_index = route.rtree.nearest((poi_point.lon, poi_point.lat, poi_point.lon, poi_point.lat), 1)
        return next(nearest_index)

    def locate(self, route: Route, point: RoutePoint) -> RouteMatch:
        """
        Find the closest point on the route's segments, not just its vertices.

        The R-tree gives the nearest vertices as candidates; the point is then
        projected onto every segment touching one of them, and the closest wins.
        Args:
            route (Route): Route object containing route points.
            point (RoutePoint): The target point, e.g. a POI.
        Returns:
            RouteMatch: Deviation and distance on route, both in kilometers.
        """
        n = len(route.points)
        if n == 1:
            return RouteMatch(self.haversine_distance(point, route.points[0]), 0.0)

        nearest = route.rtree.nearest((point.lon, point.lat, point.lon, point.lat), CANDIDATE_VERTICES)
        # A segment is named by its start index s (points[s] -> points[s + 1]).
        # Vertex i touches segment i - 1 (arriving) and segment i (leaving).
        segments = set()
        for i in nearest:
            if i > 0:
                segments.add(i - 1)
            if i < n - 1:
                segments.add(i)

        best_km, best_s, best_t = float("inf"), 0, 0.0
        for s in sorted(segments):
            a, b = route.points[s], route.points[s + 1]
            t, distance_km = project_onto_segment(point.lat, point.lon, a.lat, a.lon, b.lat, b.lon)
            if distance_km < best_km:
                best_km, best_s, best_t = distance_km, s, t

        # Along-route km stays haversine: start of the segment plus t of its length.
        segment_km = route.cumulative_km[best_s + 1] - route.cumulative_km[best_s]
        return RouteMatch(best_km, route.cumulative_km[best_s] + best_t * segment_km)

