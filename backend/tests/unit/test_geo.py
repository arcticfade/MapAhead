import pytest
from mapahead.geo import haversine_km, project_onto_segment


def test_haversine_km_berlin_paris():
    """Known great-circle distance Berlin -> Paris (878.08 km, luftlinie.org)."""
    assert round(haversine_km(52.523403, 13.4114, 48.856667, 2.350987), 2) == 878.08


def test_haversine_km_same_point():
    assert haversine_km(-5.123456, 42, -5.123456, 42) == 0.0


def test_haversine_km_is_symmetric():
    a = haversine_km(34.052235, -118.243683, 40.712776, -74.005974)
    b = haversine_km(40.712776, -74.005974, 34.052235, -118.243683)
    assert a == b


def test_project_onto_segment_midpoint():
    """P beside the middle of A->B: t = 0.5, distance is the perpendicular offset."""
    t, distance_km = project_onto_segment(0.001, 0.5, 0, 0, 0, 1)
    assert t == pytest.approx(0.5)
    assert distance_km == pytest.approx(0.111, abs=0.001)


def test_project_onto_segment_clamps():
    """Projections outside the segment are clamped to its ends."""
    t_before, _ = project_onto_segment(0, -1, 0, 0, 0, 1)
    t_after, _ = project_onto_segment(0, 2, 0, 0, 0, 1)
    assert t_before == 0.0
    assert t_after == 1.0


def test_project_onto_segment_zero_length():
    """A == B degrades to point-to-point distance with t = 0."""
    t, distance_km = project_onto_segment(0, 0.01, 0, 0, 0, 0)
    assert t == 0.0
    assert distance_km == pytest.approx(haversine_km(0, 0.01, 0, 0), rel=1e-3)
