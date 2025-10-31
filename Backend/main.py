from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gpx_parser import GPXParser
from route_storage import RouteStorage
from overpass_client import OverpassClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
route_storage = RouteStorage()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/gpx/upload")
async def upload_gpx(file: UploadFile = File(...)):
    """
    Endpoint to upload a GPX file and parse route data.
    Returns: Parsed route data including coordinates.
    """
    if not file.filename.endswith('.gpx'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a GPX file.")
    
    try:
        gpx_data = await file.read()
        parser = GPXParser(gpx_data)
        route_points = parser.parse()

        route_id = route_storage.store(route_points)

        coordinates = [{"lat": point.lat, "lon": point.lon} for point in route_points]
        return {
            "route_id": route_id,
            "filename": file.filename, 
            "coordinates": coordinates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process GPX file: {str(e)}")

@app.get("/pois/{route_id}")
async def get_pois(route_id: str, max_distance_km: float = 1.0):
    """

    """
    route = route_storage.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")
    
    try:
        overpass_client = OverpassClient(route)
        bbox = overpass_client.get_route_bounding_box(buffer_km=max_distance_km)
        overpass_data = overpass_client.query_gas_station(bbox)

        filtered_pois = overpass_client.filter_pois(overpass_data, max_distance_to_route_km=max_distance_km)

        return{
            "markers": [
                {
                    "lat": poi.lat,
                    "lon": poi.lon,
                    "name": poi.name
                }
                for poi in filtered_pois
            ],
            "table": [
                {
                    "distance": f"{poi.distance_on_route:.1f} km",
                    "deviation": f"{poi.distance_to_route * 1000:.0f}m",
                    "name": poi.name
                }
                for poi in filtered_pois
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve POIs: {str(e)}")

