# Domain glossary

| Term | Meaning in MapAhead |
|------|---------------------|
| **Route** | The ordered list of geographic points a rider will follow, imported from a GPX file. Immutable once stored. |
| **Route point** | One `(lat, lon)` pair on the route. GPX tracks from bike computers have a point every few metres; planning tools export sparser routes. |
| **Track vs route (GPX)** | GPX `<trk>` is a recorded or exported line; `<rte>` is a planned line with fewer points; `<wpt>` are standalone waypoints. We read tracks now, routes and waypoints from Phase 1.4. |
| **Route km / distance on route** | Cumulative distance from the start of the route to the point nearest a POI, in kilometres. The primary sort key for planning ("what is at km 340?"). |
| **Deviation / distance to route** | Shortest distance from a POI to the route, in metres. Riders care about this because every metre off route is ridden twice. |
| **Corridor** | The area within `max_distance` of the route. POIs outside the corridor are ignored. Currently approximated by one bounding box around the whole route (Phase 1.6 replaces it). |
| **POI** | Point of interest from OpenStreetMap: a node (or later way centroid) with tags, e.g. `amenity=fuel`. |
| **POI category** | A named group of OSM tag filters the user can toggle, e.g. *Fuel* (`amenity=fuel`), *Supermarket* (`shop=supermarket`), *Water* (`amenity=drinking_water`). Defined in code, served by `GET /api/categories` from Phase 1.5. |
| **Supply point** | A POI the planner has *chosen* for an event, with notes and a planned arrival km. Introduced in Phase 3.3. |
| **Event** | A named ride with one route and a set of supply points. Introduced in Phase 3.3. |
| **Overpass API** | The read-only query service for OpenStreetMap data. Public instances are rate limited; large bounding boxes time out. |
| **Haversine distance** | Great-circle distance between two lat/lon pairs on a sphere. Accurate to about 0.5 % and cheap. Used for all distances today. |
| **R-tree** | Spatial index over the route points; makes "nearest route point to this POI" a log-time lookup instead of a scan. |
