"""Registry tests for step 1.5: every category id has exactly one well-formed entry."""
import dataclasses

import pytest

from mapahead.poi_category import CATEGORIES, CategoryId, POICategory


def test_every_category_id_is_registered():
    assert set(CATEGORIES) == set(CategoryId)


def test_registry_has_the_ten_roadmap_categories():
    assert {c.value for c in CategoryId} == {
        "fuel", "supermarket", "drinking_water", "bakery", "bicycle_shop",
        "restaurant", "pharmacy", "atm", "hotel", "toilets",
    }


def test_registry_keys_match_entry_ids():
    for category_id, category in CATEGORIES.items():
        assert category.id == category_id


def test_entries_have_osm_tag():
    for category in CATEGORIES.values():
        assert category.osm_key.strip()
        assert category.osm_value.strip()


def test_overpass_filter():
    assert CATEGORIES[CategoryId.FUEL].overpass_filter == '["amenity"="fuel"]'
    assert CATEGORIES[CategoryId.BICYCLE_SHOP].overpass_filter == '["shop"="bicycle"]'
    assert CATEGORIES[CategoryId.HOTEL].overpass_filter == '["tourism"="hotel"]'


def test_category_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        CATEGORIES[CategoryId.FUEL].osm_value = "changed"  # type: ignore[misc]


def test_category_id_serializes_as_plain_string():
    assert CategoryId.FUEL == "fuel"
    assert f"{CategoryId.DRINKING_WATER}" == "drinking_water"
    assert isinstance(CATEGORIES[CategoryId.ATM], POICategory)
