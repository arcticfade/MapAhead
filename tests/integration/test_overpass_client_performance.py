from overpass_client import OverpassClient
from gpx_parser import GPXParser
from route_storage import RouteStorage
import time
from fastapi.testclient import TestClient
from main import app 

def test_performance():
    """ Test the performance of OverpassClient """
    with open(r'C:\Projekte\Schule\MapAhead\tests\files\test_file_100km.gpx','rb') as file:
        gpx_byte = file.read()
    
    gpx_parser = GPXParser(gpx_byte)
    route_points = gpx_parser.parse()

    route_storage = RouteStorage()
    route_id = route_storage.store(route_points)
    route = route_storage.get(route_id)

    start_time = time.time()
    overpass_client = OverpassClient(route) # type: ignore
    bbox = overpass_client.get_route_bounding_box()
    end_time = time.time()
    end_time = end_time-start_time
    assert end_time < 1 # BBox creation time should be unter 1 sec 
    
    start_time = time.time()
    results = overpass_client.query_gas_station(bbox)
    end_time = time.time()
    end_time = end_time-start_time
    assert end_time < 5 # Overpass query time should be unter 5 sec 

    start_time = time.time()
    filtered_pois = overpass_client.filter_pois(results, max_distance_to_route_km=2.0)
    end_time = time.time()
    end_time = end_time-start_time
    assert len(filtered_pois) > 0
    assert end_time < 3 # POI filtering time should be unter 3 sec 
    # complete performence under 9 sec

client = TestClient(app)

def test_poi_data_response_time():
    """
    Test Anforderung 4: Daten für Ergebnistabelle innerhalb von 2 Sekunden bereitstellen
    JSON sollte enthalten: Routenkilometer, Distanz zur Route, Bezeichnung, Breitengrad, Längengrad
    """
    with open(r'C:\Projekte\Schule\MapAhead\tests\files\test_file_100km.gpx','rb') as file:
        gpx_byte = file.read()
    
    upload_response = client.post(
        "/gpx/upload",
        files={"file": ("test.gpx", gpx_byte, "application/gpx+xml")}
    )
    assert upload_response.status_code == 200
    route_id = upload_response.json()["route_id"]
    
    start_time = time.time()
    response = client.get(f"/pois/{route_id}?max_distance_km=2.0")
    end_time = time.time()
    
    total_time = end_time - start_time
    
    assert total_time < 2.0, f"POI endpoint took {total_time}s, should be under 2s"
    
    assert response.status_code == 200
    data = response.json()
    
    assert "markers" in data
    assert len(data["markers"]) > 0
    
    marker = data["markers"][0]
    assert "lat" in marker  
    assert "lon" in marker  
    assert "name" in marker  
    
    assert "table" in data
    assert len(data["table"]) > 0
    
    table_entry = data["table"][0]
    assert "distance" in table_entry  
    assert "deviation" in table_entry  
    assert "name" in table_entry  
    
    assert isinstance(marker["lat"], float)
    assert isinstance(marker["lon"], float)
    assert isinstance(marker["name"], str)
    assert isinstance(table_entry["distance"], str)  
    assert isinstance(table_entry["deviation"], str)  
    assert isinstance(table_entry["name"], str)