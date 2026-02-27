"""
Format Google Maps API responses for human-readable output.
"""

from typing import Dict, List, Any, Optional
import json


def format_geocode_result(result: Dict[str, Any]) -> str:
    """Format geocoding result for display."""
    lines = [
        "📍 **Geocoding Result**",
        "",
        f"**Address:** {result.get('formatted_address', 'N/A')}",
        f"**Place ID:** {result.get('place_id', 'N/A')}",
        f"**Coordinates:** {result.get('location', {}).get('lat', 'N/A')}, {result.get('location', {}).get('lng', 'N/A')}",
    ]
    return "\n".join(lines)


def format_reverse_geocode_result(result: Dict[str, Any]) -> str:
    """Format reverse geocoding result for display."""
    lines = [
        "📍 **Reverse Geocoding Result**",
        "",
        f"**Address:** {result.get('formatted_address', 'N/A')}",
        f"**Place ID:** {result.get('place_id', 'N/A')}",
    ]

    # Extract county from address components
    components = result.get('address_components', [])
    county = None
    for comp in components:
        if 'administrative_area_level_2' in comp.get('types', []):
            county = comp.get('long_name', '')
            break

    if county:
        lines.append(f"**County:** {county}")

    return "\n".join(lines)


def format_place_search_results(results: List[Dict[str, Any]]) -> str:
    """Format place search results for display."""
    if not results:
        return "🔍 **No places found**"

    lines = [
        f"🔍 **Found {len(results)} places**",
        ""
    ]

    for i, place in enumerate(results, 1):
        lines.extend([
            f"**{i}. {place.get('name', 'Unknown Place')}**",
            f"   📍 {place.get('formatted_address', 'No address')}",
            f"   🆔 {place.get('place_id', 'No ID')}",
        ])

        if place.get('rating'):
            lines.append(f"   ⭐ {place['rating']} stars")
        if place.get('types'):
            lines.append(f"   🏷️  {', '.join(place['types'][:3])}")  # Show first 3 types

        lines.append("")

    return "\n".join(lines)


def format_place_details(result: Dict[str, Any]) -> str:
    """Format place details for display."""
    lines = [
        f"🏢 **{result.get('name', 'Unknown Place')}**",
        "",
        f"📍 **Address:** {result.get('formatted_address', 'N/A')}",
    ]

    if result.get('formatted_phone_number'):
        lines.append(f"📞 **Phone:** {result['formatted_phone_number']}")

    if result.get('website'):
        lines.append(f"🌐 **Website:** {result['website']}")

    if result.get('rating'):
        lines.append(f"⭐ **Rating:** {result['rating']} stars")

    if result.get('opening_hours'):
        hours = result['opening_hours']
        lines.append(f"🕒 **Open now:** {'Yes' if hours.get('open_now') else 'No'}")

        if hours.get('weekday_text'):
            lines.append("")
            lines.append("**Hours:**")
            for day in hours['weekday_text'][:7]:  # Show all days
                lines.append(f"• {day}")

    if result.get('reviews'):
        reviews = result['reviews'][:3]  # Show first 3 reviews
        lines.append("")
        lines.append("**Recent Reviews:**")
        for review in reviews:
            author = review.get('author_name', 'Anonymous')
            rating = review.get('rating', 'N/A')
            text = review.get('text', '')[:200]  # Truncate long reviews
            lines.extend([
                f"• **{author}** ({rating}⭐)",
                f"  {text}...",
                ""
            ])

    return "\n".join(lines)


def format_distance_matrix(results: Dict[str, Any]) -> str:
    """Format distance matrix results for display."""
    origins = results.get('origin_addresses', [])
    destinations = results.get('destination_addresses', [])
    rows = results.get('rows', [])

    lines = [
        "🗺️ **Distance Matrix Results**",
        "",
        f"**From:** {len(origins)} origins",
        f"**To:** {len(destinations)} destinations",
        ""
    ]

    for i, row in enumerate(rows):
        origin = origins[i] if i < len(origins) else f"Origin {i+1}"

        for j, element in enumerate(row.get('elements', [])):
            dest = destinations[j] if j < len(destinations) else f"Destination {j+1}"

            if element.get('status') == 'OK':
                distance = element.get('distance', {}).get('text', 'N/A')
                duration = element.get('duration', {}).get('text', 'N/A')
                lines.extend([
                    f"**{origin} → {dest}**",
                    f"   📏 Distance: {distance}",
                    f"   ⏱️  Duration: {duration}",
                    ""
                ])
            else:
                lines.extend([
                    f"**{origin} → {dest}**",
                    f"   ❌ Status: {element.get('status', 'Unknown')}",
                    ""
                ])

    return "\n".join(lines)


def format_elevation_results(results: List[Dict[str, Any]]) -> str:
    """Format elevation results for display."""
    if not results:
        return "🏔️ **No elevation data found**"

    lines = [
        f"🏔️ **Elevation Data for {len(results)} locations**",
        ""
    ]

    for i, result in enumerate(results, 1):
        lat = result.get('location', {}).get('lat', 'N/A')
        lng = result.get('location', {}).get('lng', 'N/A')
        elevation = result.get('elevation', 'N/A')
        resolution = result.get('resolution', 'N/A')

        lines.extend([
            f"**Location {i}:** {lat}, {lng}",
            f"   ⛰️  Elevation: {elevation}m",
            f"   🎯 Resolution: {resolution}m",
            ""
        ])

    return "\n".join(lines)


def format_directions_result(result: Dict[str, Any]) -> str:
    """Format directions result for display."""
    routes = result.get('routes', [])

    if not routes:
        return "🛣️ **No routes found**"

    route = routes[0]  # Take the first/best route
    lines = [
        "🛣️ **Directions**",
        "",
        f"**Route Summary:** {route.get('summary', 'N/A')}",
    ]

    # Add total distance and duration
    distance = route.get('distance', {}).get('text', 'N/A')
    duration = route.get('duration', {}).get('text', 'N/A')
    lines.extend([
        f"**Total Distance:** {distance}",
        f"**Total Duration:** {duration}",
        ""
    ])

    # Add turn-by-turn directions
    steps = route.get('steps', [])
    if steps:
        lines.append("**Directions:**")
        for i, step in enumerate(steps, 1):
            instructions = step.get('html_instructions', '').replace('<b>', '**').replace('</b>', '**').replace('<div>', '\n').replace('</div>', '')
            distance_step = step.get('distance', {}).get('text', 'N/A')
            duration_step = step.get('duration', {}).get('text', 'N/A')

            lines.extend([
                f"{i}. {instructions}",
                f"   📏 {distance_step} • ⏱️ {duration_step}",
                ""
            ])

    return "\n".join(lines)


def format_error_message(error: str) -> str:
    """Format error message for display."""
    return f"❌ **Error:** {error}"
