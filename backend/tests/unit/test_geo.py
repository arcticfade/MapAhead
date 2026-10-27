from mapahead.geo import haversine_km


def test_haversine_km_berlin_paris():
    """Known great-circle distance Berlin -> Paris (878.08 km, luftlinie.org)."""
    assert round(haversine_km(52.523403, 13.4114, 48.856667, 2.350987), 2) == 878.08


def test_haversine_km_same_point():
    assert haversine_km(-5.123456, 42, -5.123456, 42) == 0.0


def test_haversine_km_is_symmetric():
    a = haversine_km(34.052235, -118.243683, 40.712776, -74.005974)
    b = haversine_km(40.712776, -74.005974, 34.052235, -118.243683)
    assert a == b
