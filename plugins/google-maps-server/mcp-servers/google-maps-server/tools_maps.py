"""
Google Maps API tools.
"""

from typing import Dict, List, Optional, Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult

from cache import cache_response, get_cached_response
from credentials import get_api_key, get_api_key_from_user
from google_maps_client import GoogleMapsApiError, get_json, require_ok_status
from formatter import (
    format_geocode_result,
    format_reverse_geocode_result,
    format_place_search_results,
    format_place_details,
    format_distance_matrix,
    format_elevation_results,
    format_directions_result,
    format_error_message
)
from utils import text_response


VALID_TRAVEL_MODES = {"driving", "walking", "bicycling", "transit"}


def validate_latitude_longitude(latitude: float, longitude: float) -> None:
    if not (-90 <= latitude <= 90):
        raise ValueError("latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise ValueError("longitude must be between -180 and 180")


def validate_mode(mode: str) -> str:
    normalized_mode = mode.lower().strip()
    if normalized_mode not in VALID_TRAVEL_MODES:
        allowed = ", ".join(sorted(VALID_TRAVEL_MODES))
        raise ValueError(f"mode must be one of: {allowed}")
    return normalized_mode


def validate_radius(radius: int) -> None:
    if not (1 <= radius <= 50000):
        raise ValueError("radius must be between 1 and 50000 meters")


def validate_locations(locations: List[Dict[str, float]]) -> None:
    if not locations:
        raise ValueError("locations must contain at least one coordinate")
    for loc in locations:
        if "latitude" not in loc or "longitude" not in loc:
            raise ValueError("each location must include latitude and longitude")
        validate_latitude_longitude(loc["latitude"], loc["longitude"])


async def get_or_elicit_api_key(ctx: Context) -> str:
    """
    Get API key from storage or elicit from user if not available.

    Args:
        ctx: FastMCP context for user interaction

    Returns:
        str: The API key
    """
    api_key = get_api_key()
    if not api_key or not api_key.strip():
        await ctx.info("API key not found, requesting from user...")
        api_key = await get_api_key_from_user(ctx)
    return api_key


async def ensure_external_call_consent(ctx: Context) -> None:
    """Require one-time session consent before making external API calls."""
    already_approved = await ctx.get_state("external_call_approved")
    if already_approved:
        return

    result = await ctx.elicit(
        "This tool will call Google Maps APIs over the network. Continue?",
        response_type=None,
    )
    action = getattr(result, "action", None)
    if action == "accept":
        await ctx.set_state("external_call_approved", True)
        return
    if action == "decline":
        raise ValueError("User declined external API call")
    if action == "cancel":
        raise ValueError("User cancelled external API call")
    raise ValueError("Unexpected elicitation response")


def register(mcp: FastMCP) -> None:
    """Register all Google Maps API tools."""

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_geocode(address: str, ctx: Context = CurrentContext()) -> ToolResult:
        """
        Convert an address into geographic coordinates.

        Args:
            address: The address to geocode (e.g., "1600 Amphitheatre Parkway, Mountain View, CA")

        Returns:
            Formatted result with coordinates, formatted address, and place ID.
        """
        await ctx.info(f"Geocoding address: {address}")

        # Check cache first
        cache_key = f"geocode:{address}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved result from cache")
            return text_response(format_geocode_result(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            data = await get_json("geocode/json", {"address": address, "key": api_key})
            require_ok_status(data, "Geocoding failed")

            result = {
                "location": data["results"][0]["geometry"]["location"],
                "formatted_address": data["results"][0]["formatted_address"],
                "place_id": data["results"][0]["place_id"]
            }

            # Cache the result
            cache_response(cache_key, result)

            await ctx.info("Successfully geocoded address")
            return text_response(format_geocode_result(result))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error geocoding address: {str(e)}"))

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_reverse_geocode(
        latitude: float,
        longitude: float,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Convert coordinates into an address.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Formatted result with address, place ID, and address components.
        """
        await ctx.info(f"Reverse geocoding coordinates: {latitude}, {longitude}")
        validate_latitude_longitude(latitude, longitude)

        # Check cache first
        cache_key = f"reverse_geocode:{latitude},{longitude}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved result from cache")
            return text_response(format_reverse_geocode_result(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            data = await get_json(
                "geocode/json",
                {"latlng": f"{latitude},{longitude}", "key": api_key},
            )
            require_ok_status(data, "Reverse geocoding failed")

            result = {
                "formatted_address": data["results"][0]["formatted_address"],
                "place_id": data["results"][0]["place_id"],
                "address_components": data["results"][0]["address_components"]
            }

            # Cache the result
            cache_response(cache_key, result)

            await ctx.info("Successfully reverse geocoded coordinates")
            return text_response(format_reverse_geocode_result(result))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error reverse geocoding: {str(e)}"))

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_search_places(
        query: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Search for places using Google Places API.

        Args:
            query: Search query (e.g., "restaurants in New York")
            latitude: Optional latitude for location bias
            longitude: Optional longitude for location bias
            radius: Optional search radius in meters (max 50000)

        Returns:
            Formatted list of places with names, addresses, and details.
        """
        await ctx.info(f"Searching for places: {query}")
        if not query.strip():
            raise ValueError("query must be a non-empty string")
        if latitude is not None and longitude is not None:
            validate_latitude_longitude(latitude, longitude)
        elif latitude is not None or longitude is not None:
            raise ValueError("latitude and longitude must both be provided")
        if radius is not None:
            validate_radius(radius)

        # Build cache key
        location_str = f"{latitude},{longitude}" if latitude and longitude else "none"
        cache_key = f"places_search:{query}:{location_str}:{radius or 'none'}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved places from cache")
            return text_response(format_place_search_results(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            params = {
                "query": query,
                "key": api_key
            }

            if latitude and longitude:
                params["location"] = f"{latitude},{longitude}"

            if radius:
                params["radius"] = str(radius)

            data = await get_json("place/textsearch/json", params)
            require_ok_status(data, "Place search failed")

            results = []
            for place in data.get("results", []):
                place_data = {
                    "name": place.get("name"),
                    "formatted_address": place.get("formatted_address"),
                    "place_id": place.get("place_id"),
                    "location": place.get("geometry", {}).get("location"),
                    "rating": place.get("rating"),
                    "types": place.get("types", [])
                }
                results.append(place_data)

            # Cache the results
            cache_response(cache_key, results)

            await ctx.info(f"Found {len(results)} places")
            return text_response(format_place_search_results(results))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error searching places: {str(e)}"))

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_place_details(
        place_id: str,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Get detailed information about a specific place.

        Args:
            place_id: The place ID to get details for

        Returns:
            Detailed place information including contact info, ratings, reviews, and hours.
        """
        await ctx.info(f"Getting details for place ID: {place_id}")

        # Check cache first
        cache_key = f"place_details:{place_id}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved place details from cache")
            return text_response(format_place_details(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            data = await get_json("place/details/json", {"place_id": place_id, "key": api_key})
            require_ok_status(data, "Place details request failed")

            result = data.get("result", {})
            formatted_result = {
                "name": result.get("name"),
                "formatted_address": result.get("formatted_address"),
                "location": result.get("geometry", {}).get("location"),
                "formatted_phone_number": result.get("formatted_phone_number"),
                "website": result.get("website"),
                "rating": result.get("rating"),
                "reviews": result.get("reviews"),
                "opening_hours": result.get("opening_hours")
            }

            # Cache the result
            cache_response(cache_key, formatted_result)

            await ctx.info("Successfully retrieved place details")
            return text_response(format_place_details(formatted_result))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error getting place details: {str(e)}"))

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_distance_matrix(
        origins: List[str],
        destinations: List[str],
        mode: str = "driving",
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Calculate travel distance and time for multiple origins and destinations.

        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            mode: Travel mode (driving, walking, bicycling, transit)

        Returns:
            Distance and duration matrix for all origin-destination pairs.
        """
        await ctx.info(f"Calculating distance matrix for {len(origins)} origins and {len(destinations)} destinations")
        if not origins:
            raise ValueError("origins must contain at least one value")
        if not destinations:
            raise ValueError("destinations must contain at least one value")
        mode = validate_mode(mode)

        # Build cache key
        origins_str = "|".join(origins)
        destinations_str = "|".join(destinations)
        cache_key = f"distance_matrix:{origins_str}:{destinations_str}:{mode}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved distance matrix from cache")
            return text_response(format_distance_matrix(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            data = await get_json(
                "distancematrix/json",
                {
                    "origins": "|".join(origins),
                    "destinations": "|".join(destinations),
                    "mode": mode,
                    "key": api_key,
                },
            )
            require_ok_status(data, "Distance matrix request failed")

            result = {
                "origin_addresses": data.get("origin_addresses", []),
                "destination_addresses": data.get("destination_addresses", []),
                "rows": data.get("rows", [])
            }

            # Cache the result
            cache_response(cache_key, result)

            await ctx.info("Successfully calculated distance matrix")
            return text_response(format_distance_matrix(result))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error calculating distance matrix: {str(e)}"))

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_elevation(
        locations: List[Dict[str, float]],
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Get elevation data for locations on the earth.

        Args:
            locations: List of locations with latitude and longitude

        Returns:
            Elevation data for each provided location.
        """
        await ctx.info(f"Getting elevation for {len(locations)} locations")
        validate_locations(locations)

        # Build cache key from locations
        location_strings = [f"{loc['latitude']},{loc['longitude']}" for loc in locations]
        cache_key = f"elevation:{'|'.join(location_strings)}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved elevation data from cache")
            return text_response(format_elevation_results(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            location_string = "|".join(location_strings)
            data = await get_json(
                "elevation/json",
                {"locations": location_string, "key": api_key},
            )
            require_ok_status(data, "Elevation request failed")

            results = []
            for result in data.get("results", []):
                elevation_data = {
                    "elevation": result.get("elevation"),
                    "location": result.get("location"),
                    "resolution": result.get("resolution")
                }
                results.append(elevation_data)

            # Cache the results
            cache_response(cache_key, results)

            await ctx.info("Successfully retrieved elevation data")
            return text_response(format_elevation_results(results))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error getting elevation data: {str(e)}"))

    @mcp.tool(
        annotations={"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True},
    )
    async def maps_directions(
        origin: str,
        destination: str,
        mode: str = "driving",
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Get directions between two points.

        Args:
            origin: Starting point address or coordinates
            destination: Ending point address or coordinates
            mode: Travel mode (driving, walking, bicycling, transit)

        Returns:
            Turn-by-turn directions with distance, duration, and route details.
        """
        await ctx.info(f"Getting directions from {origin} to {destination}")
        if not origin.strip():
            raise ValueError("origin must be a non-empty string")
        if not destination.strip():
            raise ValueError("destination must be a non-empty string")
        mode = validate_mode(mode)

        # Build cache key
        cache_key = f"directions:{origin}:{destination}:{mode}"
        cached_result = get_cached_response(cache_key)
        if cached_result:
            await ctx.info("Retrieved directions from cache")
            return text_response(format_directions_result(cached_result))

        try:
            await ensure_external_call_consent(ctx)
            api_key = await get_or_elicit_api_key(ctx)
            data = await get_json(
                "directions/json",
                {
                    "origin": origin,
                    "destination": destination,
                    "mode": mode,
                    "key": api_key,
                },
            )
            require_ok_status(data, "Directions request failed")

            # Process the route data
            routes = []
            for route in data.get("routes", []):
                route_data = {
                    "summary": route.get("summary"),
                    "distance": route.get("legs", [{}])[0].get("distance"),
                    "duration": route.get("legs", [{}])[0].get("duration"),
                    "steps": []
                }

                # Process steps
                for step in route.get("legs", [{}])[0].get("steps", []):
                    step_data = {
                        "instructions": step.get("html_instructions", ""),
                        "distance": step.get("distance"),
                        "duration": step.get("duration"),
                        "travel_mode": step.get("travel_mode")
                    }
                    route_data["steps"].append(step_data)

                routes.append(route_data)

            result = {"routes": routes}

            # Cache the result
            cache_response(cache_key, result)

            await ctx.info("Successfully retrieved directions")
            return text_response(format_directions_result(result))

        except GoogleMapsApiError as e:
            return text_response(format_error_message(str(e)))
        except Exception as e:
            return text_response(format_error_message(f"Error getting directions: {str(e)}"))
