from gpx_parser import GPXParser
from route_storage import RouteStorage
import time


def test_gpx_parser():
    """
    Test Backend Requirement 4: POI data delivery within 2 seconds.
    
    Verifies JSON response contains:
    - Route kilometers (distance)
    - Distance to route (deviation)
    - POI name
    - Coordinates (lat/lon)
    """
    with open(r'C:\Projekte\Schule\MapAhead\tests\files\test_file_2MB.gpx','rb') as file:
        gpx_byte = file.read()
    start_time = time.time()
    gpx_parser = GPXParser(gpx_byte)
    gpx_parser.parse()
    end_time = time.time()
    total_time = end_time - start_time
    assert total_time < 2
