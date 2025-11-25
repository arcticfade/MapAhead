from fastapi.testclient import TestClient
import time
from main import app 

client = TestClient(app)

def test_gpx_upload_performance():
    with open(r'C:\Projekte\Schule\MapAhead\tests\files\test_file_2MB.gpx','rb') as file:
        gpx_byte = file.read()
    start_time = time.time()
    response = client.post(
        "/gpx/upload",
        files={"file": ("test.gpx", gpx_byte, "application/gpx+xml")}                   
        )
    end_time = time.time()
 
    total_time = end_time - start_time
    print(total_time)
    assert total_time < 2
    assert response.status_code == 200

    data = response.json()
    assert "route_id" in data
    assert "filename" in data
    assert len(data["coordinates"]) > 0
    assert type(data["coordinates"][0]["lat"]) == float 