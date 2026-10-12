from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from mapahead.gpx_parser import GPXParser, GPXParseError
from mapahead.route_storage import RouteStorage
from mapahead.overpass_client import OverpassClient, OverpassError, OverpassTimeoutError
from mapahead.schemas import PoiListResponse, PoiResponse, RouteUploadResponse

MAX_FILE_SIZE_MB = 2
MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
route_storage = RouteStorage()


@app.post("/gpx/upload", response_model=RouteUploadResponse)
async def upload_gpx(file: UploadFile = File(...)):
    """
    Endpoint to upload a GPX file and parse route data.
        Args:
            file (UploadFile): The uploaded GPX file.
        Returns:
            RouteUploadResponse: route_id, filename and coordinates list.
    """
    if not file.filename.endswith('.gpx'): # type: ignore
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a GPX file.")
    
    gpx_data = await file.read(MAX_FILE_SIZE_BYTES + 1)
    if len(gpx_data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB} MB")
        
    try:
        parser = GPXParser(gpx_data)
        route_points = parser.parse()
    except GPXParseError as e: 
        raise HTTPException(status_code=422, detail=str(e))
    
    route_id = route_storage.store(route_points)
    coordinates = [{"lat": point.lat, "lon": point.lon} for point in route_points]
    return RouteUploadResponse(
        route_id=route_id,
        filename=file.filename,  # type: ignore
        coordinates=coordinates,
    )

@app.get("/pois/{route_id}", response_model=PoiListResponse)
async def get_pois(route_id: str, max_distance_km: Annotated[float, Query(gt=0, le=5)] = 1.0):
    """
    Endpoint to get point of interests (POI) along a route.
        Args:
            route_id (str): The ID of the route.
            max_distance_km (float): Maximum distance from the route to consider POIs (in kilometers), 0 < value <= 5. Default is 1 km.
        Returns:
            PoiListResponse: route_id, max_distance_km and POIs sorted by distance along the route.
    """
    
    route = route_storage.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")
    
    overpass_client = OverpassClient(route)
    bbox = overpass_client.get_route_bounding_box(buffer_km=max_distance_km)
    try:
        overpass_data = overpass_client.query_gas_station(bbox)
    except OverpassTimeoutError:
        raise HTTPException(status_code=504, detail="Overpass API timed out. Please try again later.")
    except OverpassError:
        raise HTTPException(status_code=502, detail="Overpass API is unavailable or returned an error.")

    filtered_pois = overpass_client.filter_pois(overpass_data, max_distance_to_route_km=max_distance_km)

    return PoiListResponse(
        route_id=route_id,
        max_distance_km=max_distance_km,
        pois=[
            PoiResponse(
                name=poi.name,
                lat=poi.lat,
                lon=poi.lon,
                distance_on_route_km=poi.distance_on_route,
                distance_to_route_m=poi.distance_to_route * 1000,
            )
            for poi in filtered_pois
        ],
    )
