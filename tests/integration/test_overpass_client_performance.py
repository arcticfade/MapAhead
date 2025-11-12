from overpass_client import OverpassClient
from gpx_parser import GPXParser
from route_storage import Route
import time

def test_performance():
    """ Test the performance of OverpassClient unit defined in 2.5.2 
    """
    with open(r'C:\Projekte\Schule\MapAhead\tests\files\test_file_100km.gpx','rb') as file:
        gpx_byte = file.read()
    
    gpx_parser = GPXParser(gpx_byte)
    route_points = gpx_parser.parse()

    start_time = time.time()
    overpass_client = OverpassClient(Route(route_points, "test-100km"))
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
    assert end_time < 3 # POI filtering time should be unter 3 sec 
    # complete performence under 9 sec
