import pytest
from fastapi.testclient import TestClient
import sys 
import os
import time
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Backend'))

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
    assert total_time < 4
    assert response.status_code == 200

    data = response.json()
    assert "route_id" in data
    assert "filename" in data
    assert len(data["coordinates"]) > 0
    assert type(data["coordinates"][0]["lat"]) == float 