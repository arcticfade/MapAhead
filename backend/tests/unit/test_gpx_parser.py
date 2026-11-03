import pytest
from mapahead.gpx_parser import GPXParseError, GPXParser
import time
import os


def test_gpx_parser():
    """
    Test Backend Requirement 1: GPX parsing within 2 seconds.
    
    Parses a 2MB GPX file with 20,000+ points.
    """
    test_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(test_dir, 'tests', 'files', 'test_file_2MB.gpx')
    with open(file_path,'rb') as file:
        gpx_byte = file.read()
    start_time = time.time()
    gpx_parser = GPXParser(gpx_byte)
    gpx_parser.parse()
    end_time = time.time()
    total_time = end_time - start_time
    assert total_time < 2


def _gpx(body: str) -> bytes:
    return f'<gpx version="1.1" creator="test">{body}</gpx>'.encode()


TRK = (
    '<trk><trkseg>'
    '<trkpt lat="1" lon="2"/><trkpt lat="1.1" lon="2.1"/>'
    '</trkseg></trk>'
)
RTE = '<rte><rtept lat="3" lon="4"/><rtept lat="3.1" lon="4.1"/></rte>'
WPT = '<wpt lat="5" lon="6"><name>shop</name></wpt>'


def _coords(points):
    return [(p.lat, p.lon) for p in points]


def test_parses_track():
    points = GPXParser(_gpx(TRK)).parse()
    assert _coords(points) == [(1, 2), (1.1, 2.1)]


def test_parses_route_only_file():
    points = GPXParser(_gpx(RTE)).parse()
    assert _coords(points) == [(3, 4), (3.1, 4.1)]


def test_track_wins_over_route():
    points = GPXParser(_gpx(RTE + TRK)).parse()
    assert _coords(points) == [(1, 2), (1.1, 2.1)]


def test_waypoints_ignored_when_track_present():
    points = GPXParser(_gpx(WPT + TRK)).parse()
    assert _coords(points) == [(1, 2), (1.1, 2.1)]


def test_waypoint_only_file_is_rejected():
    with pytest.raises(GPXParseError, match="waypoint"):
        GPXParser(_gpx(WPT)).parse()


def test_empty_track_and_route_are_rejected():
    with pytest.raises(GPXParseError):
        GPXParser(_gpx("<trk><trkseg/></trk><rte/>")).parse()


def test_gpx_without_geometry_is_rejected():
    with pytest.raises(GPXParseError):
        GPXParser(_gpx("")).parse()


def test_non_gpx_is_rejected():
    with pytest.raises(GPXParseError, match="Not a valid GPX"):
        GPXParser(b"not xml").parse()
