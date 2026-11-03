# Concept: projecting a point onto a route segment

## What is it

A route is a polyline: vertices joined by straight segments. To know where a POI sits relative to the route you want the **closest point on a segment**, not the closest vertex. Snapping to a vertex is wrong by up to half the segment length.

For a segment A->B and a point P, treat them as vectors:

```
t = (AP · AB) / (AB · AB)        # how far along A->B P's "shadow" falls
t = clamp(t, 0, 1)               # stay on the segment, not the infinite line
closest = A + t · AB
deviation = |P - closest|
```

`t = 0` is A, `t = 1` is B, `t = 0.5` is halfway. Without the clamp, a POI behind the start would land on the line's extension, off the route.

## Why here

`geo.project_onto_segment` does the maths. `RouteCalculator.locate` uses it in three steps:

1. **Candidates.** The R-tree returns the 5 nearest vertices (`CANDIDATE_VERTICES`). Each vertex `i` touches segments `i-1` and `i`. Taking several vertices, not one, handles hairpins where the nearest vertex belongs to the wrong leg.
2. **Project** P onto each candidate segment and keep the closest. That distance is the deviation.
3. **Position on route** = `cumulative_km[s] + t · (cumulative_km[s+1] - cumulative_km[s])`. It reuses the haversine prefix sum from 1.2, so along-route km stays haversine.

### Haversine vs a local flat frame

The vector formula needs flat x/y in one unit, but lat/lon are angles on a sphere. A degree of longitude shrinks with latitude (`111 km · cos(lat)`). So the projection works in a **local flat frame centred on P**: longitude is multiplied by `cos(lat)` and both axes are converted to km (an equirectangular projection).

That is only accurate locally, but the deviation is local: a few km at most (`max_distance_km <= 5`). At that scale the error is well under a metre. Long distances (km along the route) never go through the flat frame; they stay haversine.

We did not use shapely or pyproj. Measured on the test routes (median vertex gap 21 to 24 m), the vertex error was tens of metres, which does not justify two dependencies. If 1.6 needs real geometry (buffering the route into a corridor), shapely comes in then.

## What to check when reviewing

- The clamp is there. Without it, POIs before the start or after the finish get impossible km values.
- Units: the flat frame is in km, as are `cumulative_km` and `max_distance_to_route_km`. The deviation is converted to metres only when `main.py` builds the response.
- Candidates come from more than one vertex.
- Known limits: the flat frame breaks at the antimeridian (±180° longitude) and near the poles. Neither matters for cycling routes so far.
