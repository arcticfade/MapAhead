# Map_Ahead
A website where a route can be uploaded in the form of a GPX file and displayed using the JS library Leaflet and OpenStreetMap. Along the route, the OverpassAPI provided by OpenStreetMap can be used to search for relevant locations (such as supermarkets, gas stations, or water points). These locations are indicated by a marker on the map.

## Manual app start: 
Backend: 
fastapi dev main.py --port 5000

Frontend: 
python -m http.server 4000
