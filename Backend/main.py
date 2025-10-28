from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gpx_parser import GPXParser
from Backend.route_storage import RouteStorage

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

@app.get("/pois/markers/{route_id}")
async def get_poi_markers(route_id: str):
    route = route_storage.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")
    
    # Mock data for Frontend development
    mock_markers = [
        {"lat": 52.5200, "lon": 13.4050, "name": "Shell Berlin"},
        {"lat": 52.5100, "lon": 13.4150, "name": "Total Berlin"},
        {"lat": 52.5300, "lon": 13.3950, "name": "Aral Station"}
    ]
    
    return mock_markers
        

@app.get("/pois/table/{route_id}")
async def get_poi_table(route_id: str):
    route = route_storage.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")
    
    # Mock data for Frontend development
    mock_table_data = [
        {"distance": "5.2 km", "deviation": "300m", "name": "Shell Berlin"},
        {"distance": "12.8 km", "deviation": "150m", "name": "Total Berlin"},
        {"distance": "25.4 km", "deviation": "450m", "name": "Aral Station"}
    ]
    return mock_table_data