#!/usr/bin/env python3
"""
Sandals Data Manager
Loads and queries resort data from local JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class SandalsDataManager:
    """Manages Sandals resort data loaded from JSON files."""

    def __init__(self):
        self.data_path = Path(__file__).parent / "data"
        self.resorts = self._load_resorts()
        self.rooms = self._load_rooms()
        self.restaurants = self._load_restaurants()

    def _load_json_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from file."""
        file_path = self.data_path / filename
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
        return []

    def _load_resorts(self) -> Dict[str, Dict[str, Any]]:
        """Load and index resort data by resort code."""
        resorts_data = self._load_json_data("resorts.json")
        return {resort["resort_code"]: resort for resort in resorts_data}

    def _load_rooms(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load room data organized by resort code."""
        file_path = self.data_path / "rooms.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        return {}

    def _load_restaurants(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load restaurant data organized by resort code."""
        file_path = self.data_path / "restaurants.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                elif isinstance(data, list):
                    by_resort: Dict[str, list] = {}
                    for restaurant in data:
                        if isinstance(restaurant, dict):
                            code = restaurant.get("resort_code", "UNKNOWN")
                            by_resort.setdefault(code, []).append(restaurant)
                    return by_resort
        return {}

    # --- Query Methods ---

    def search_resorts(
        self,
        island: Optional[str] = None,
        kids_allowed: Optional[bool] = None,
        max_airport_distance: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Search resorts with optional filters."""
        results = []
        for code, resort in self.resorts.items():
            if island and resort.get("island", "").lower() != island.lower():
                continue
            if kids_allowed is not None and resort.get("kids_allowed") != kids_allowed:
                continue
            if (
                max_airport_distance
                and resort.get("airport_distance_miles", 999) > max_airport_distance
            ):
                continue
            results.append({**resort, "resort_code": code})
        return results

    def get_resort(self, resort_code: str) -> Optional[Dict[str, Any]]:
        """Get a single resort by code."""
        return self.resorts.get(resort_code.upper())

    def get_rooms(
        self,
        resort_code: str,
        room_category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get rooms for a resort, optionally filtered by category/class."""
        rooms = self.rooms.get(resort_code.upper(), [])
        if room_category:
            rooms = [
                r
                for r in rooms
                if room_category.lower() in r.get("room_class", "").lower()
            ]
        return rooms

    def get_room(
        self, resort_code: str, room_code: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific room by resort and room code."""
        for room in self.rooms.get(resort_code.upper(), []):
            if room.get("room_code") == room_code.upper():
                return room
        return None

    def get_restaurants(
        self,
        resort_code: str,
        cuisine_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get restaurants for a resort, optionally filtered by cuisine."""
        restaurants = self.restaurants.get(resort_code.upper(), [])
        if cuisine_type:
            restaurants = [
                r
                for r in restaurants
                if cuisine_type.lower() in r.get("cuisine_type", "").lower()
            ]
        return restaurants

    def get_restaurant(
        self, resort_code: str, restaurant_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific restaurant by name."""
        for r in self.restaurants.get(resort_code.upper(), []):
            if r.get("name", "").lower() == restaurant_name.lower():
                return r
        return None

    def find_rooms_by_class(
        self, room_class: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find rooms across all resorts by room class."""
        results = []
        target = room_class.upper()
        for resort_code, rooms in self.rooms.items():
            for room in rooms:
                if room.get("room_class", "").upper() == target:
                    resort = self.resorts.get(resort_code, {})
                    results.append(
                        {
                            "resort_code": resort_code,
                            "resort_name": resort.get("name"),
                            "island": resort.get("island"),
                            **room,
                        }
                    )
                    if len(results) >= max_results:
                        return results
        return results
