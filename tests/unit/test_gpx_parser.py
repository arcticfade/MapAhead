from gpx_parser import GPXParser
from route_storage import RouteStorage
import time


def test_gpx_parser():
    with open(r'C:\Projekte\Schule\MapAhead\tests\files\test_file_2MB.gpx','rb') as file:
        gpx_byte = file.read()
    start_time = time.time()
    gpx_parser = GPXParser(gpx_byte)
    gpx_parser.parse()
    end_time = time.time()
    total_time = end_time - start_time
    assert total_time < 2
