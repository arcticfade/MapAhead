"""
POI categories and the OpenStreetMap tags that select them in Overpass.

Pure data, no internal imports (like `geo.py`). Step 1.8 moves this module to
`mapahead/domain/`.

The registry is the single source of truth: the `/categories` endpoint lists
it, and the Overpass query (step 1.6) is built from the selected entries.
"""
from dataclasses import dataclass
from enum import StrEnum


class CategoryId(StrEnum):
    """Stable identifiers used in the API and by the frontend."""
    FUEL = "fuel"
    SUPERMARKET = "supermarket"
    DRINKING_WATER = "drinking_water"
    BAKERY = "bakery"
    BICYCLE_SHOP = "bicycle_shop"
    RESTAURANT = "restaurant"
    PHARMACY = "pharmacy"
    ATM = "atm"
    HOTEL = "hotel"
    TOILETS = "toilets"


@dataclass(frozen=True)
class POICategory:
    """A kind of place the user can search for along a route.

    Attributes:
        id (CategoryId): Stable identifier.
        osm_key (str): OSM tag key, e.g. "amenity".
        osm_value (str): OSM tag value, e.g. "fuel".
    """
    id: CategoryId
    osm_key: str
    osm_value: str

    @property
    def overpass_filter(self) -> str:
        """The Overpass QL tag filter, e.g. `["amenity"="fuel"]`."""
        return f'["{self.osm_key}"="{self.osm_value}"]'


CATEGORIES: dict[CategoryId, POICategory] = {
    c.id: c
    for c in (
        POICategory(CategoryId.FUEL, "amenity", "fuel"),
        POICategory(CategoryId.SUPERMARKET, "shop", "supermarket"),
        POICategory(CategoryId.DRINKING_WATER, "amenity", "drinking_water"),
        POICategory(CategoryId.BAKERY, "shop", "bakery"),
        POICategory(CategoryId.BICYCLE_SHOP, "shop", "bicycle"),
        POICategory(CategoryId.RESTAURANT, "amenity", "restaurant"),
        POICategory(CategoryId.PHARMACY, "amenity", "pharmacy"),
        POICategory(CategoryId.ATM, "amenity", "atm"),
        POICategory(CategoryId.HOTEL, "tourism", "hotel"),
        POICategory(CategoryId.TOILETS, "amenity", "toilets"),
    )
}
