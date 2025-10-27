from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from mockdata import MOCK_ROUTE_COORDINATES, MOCK_POIS
from gpx_parser import GPXParser

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        coordinates = [{"lat": point.lat, "lon": point.lon} for point in route_points]
        return {"filename": file.filename, "coordinates": coordinates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process GPX file: {str(e)}")
