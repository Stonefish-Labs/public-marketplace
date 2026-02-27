#!/usr/bin/env python3
"""
Sandals BoujieBot MCP Server
FastMCP 3.x — luxury travel concierge for Sandals and Beaches Resorts
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List

from fastmcp import FastMCP, Context
from fastmcp.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult
from fastmcp.exceptions import ToolError
from fastmcp.prompts import Message

from utils import text_response
from data_manager import SandalsDataManager
from tools.check_availability import AvailabilityChecker
from price_monitor import PriceMonitor

mcp = FastMCP(
    name="SandalsBoujieBot",
    instructions="""
        Luxury travel concierge for Sandals and Beaches Resorts.
        Use for resort recommendations, room availability, restaurant info, and price monitoring.
        Can send Discord notifications when tracked prices drop below a target.
    """,
    on_duplicate="error",
)

# Core modules — business logic lives here, server.py is just the MCP envelope
data_manager = SandalsDataManager()
availability_checker = AvailabilityChecker()
price_monitor = PriceMonitor()


# ---------------------------------------------------------------------------
# Resort Lookup Tools (read-only, local data)
# ---------------------------------------------------------------------------


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def search_resorts(
    island: Optional[str] = None,
    kids_allowed: Optional[bool] = None,
    max_airport_distance: Optional[float] = None,
) -> ToolResult:
    """Search Sandals/Beaches resorts by island, kid-friendliness, or airport proximity."""
    results = data_manager.search_resorts(island, kids_allowed, max_airport_distance)
    if not results:
        return text_response("No resorts match those criteria.")

    lines = [f"**{len(results)} resort(s) found**\n"]
    for r in results:
        lines.append(f"### {r['name']} ({r['resort_code']})")
        lines.append(f"**Island:** {r.get('island', 'N/A')}")
        desc = r.get("description", "")
        if desc:
            lines.append(desc[:200] + "...")
        kids = "Kids welcome" if r.get("kids_allowed") else "Adults only"
        dist = r.get("airport_distance_miles", "?")
        code = r.get("nearest_airport_code", "airport")
        lines.append(f"_{kids} | {dist} mi from {code}_\n")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def get_resort_details(resort_code: str) -> ToolResult:
    """Get detailed information about a specific Sandals/Beaches resort."""
    resort = data_manager.get_resort(resort_code)
    if not resort:
        raise ToolError(f"Resort code '{resort_code.upper()}' not found.")

    code = resort_code.upper()
    room_count = len(data_manager.get_rooms(code))
    restaurant_count = len(data_manager.get_restaurants(code))

    lines = [
        f"# {resort.get('name')}",
        f"**Code:** {code}",
        f"**Island:** {resort.get('island')}",
        f"**Description:** {resort.get('description', 'N/A')}",
        f"**Kids Allowed:** {'Yes' if resort.get('kids_allowed') else 'No'}",
        f"**Airport:** {resort.get('nearest_airport')} ({resort.get('nearest_airport_code')})",
        f"**Distance:** {resort.get('airport_distance_miles')} mi / {resort.get('airport_travel_time_minutes')} min",
        f"**Rooms:** {room_count} categories | **Restaurants:** {restaurant_count}",
    ]
    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def get_resort_restaurants(
    resort_code: str,
    cuisine_type: Optional[str] = None,
) -> ToolResult:
    """List restaurants at a resort, optionally filtered by cuisine type."""
    restaurants = data_manager.get_restaurants(resort_code, cuisine_type)
    if not restaurants:
        msg = f"No restaurants found at {resort_code.upper()}"
        if cuisine_type:
            msg += f" for cuisine '{cuisine_type}'"
        return text_response(msg + ".")

    lines = [f"**{len(restaurants)} restaurant(s) at {resort_code.upper()}**\n"]
    for r in restaurants:
        lines.append(f"### {r.get('name')}")
        lines.append(
            f"**Cuisine:** {r.get('cuisine_type', 'N/A')} | "
            f"**Dress Code:** {r.get('dress_code', 'Resort Casual')}"
        )
        short = r.get("short_description") or r.get("description", "")
        if short:
            lines.append(short[:200])
        meals = []
        if r.get("breakfast"):
            meals.append("Breakfast")
        if r.get("lunch"):
            meals.append("Lunch")
        if r.get("dinner"):
            meals.append("Dinner")
        if meals:
            lines.append(f"**Meals:** {', '.join(meals)}")
        if r.get("reservation_required"):
            lines.append("_Reservation required_")
        lines.append("")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def get_resort_rooms(
    resort_code: str,
    room_category: Optional[str] = None,
) -> ToolResult:
    """List room categories at a resort, optionally filtered by class (e.g. Butler, Swim-up, Overwater)."""
    rooms = data_manager.get_rooms(resort_code, room_category)
    if not rooms:
        msg = f"No rooms found at {resort_code.upper()}"
        if room_category:
            msg += f" matching '{room_category}'"
        return text_response(msg + ".")

    lines = [f"**{len(rooms)} room category(ies) at {resort_code.upper()}**\n"]
    for r in rooms:
        lines.append(f"### {r.get('name')} ({r.get('room_code', 'N/A')})")
        lines.append(
            f"**Class:** {r.get('room_class', 'N/A')} | "
            f"**Max Occupancy:** {r.get('max_occupancy', 'N/A')}"
        )
        lines.append(f"**Bedding:** {r.get('bedding', 'N/A')}")
        views = r.get("Room View(s)")
        if views:
            lines.append(f"**Views:** {views}")
        desc = r.get("description", "")
        if desc:
            lines.append(desc[:200])
        lines.append("")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def get_room_details(resort_code: str, room_code: str) -> ToolResult:
    """Get detailed information about a specific room type at a resort."""
    room = data_manager.get_room(resort_code, room_code)
    if not room:
        raise ToolError(
            f"Room '{room_code.upper()}' not found at resort {resort_code.upper()}."
        )

    lines = [
        f"# {room.get('name')}",
        f"**Room Code:** {room.get('room_code')}",
        f"**Class:** {room.get('room_class', 'N/A')}",
        f"**Bedding:** {room.get('bedding', 'N/A')}",
        f"**Max Occupancy:** {room.get('max_occupancy', 'N/A')} "
        f"(Adults: {room.get('max_adults', 'N/A')})",
        f"**Transfer:** {room.get('transfer_type', 'N/A')}",
    ]
    views = room.get("Room View(s)")
    if views:
        lines.append(f"**Views:** {views}")
    desc = room.get("description")
    if desc:
        lines.append(f"\n{desc}")
    amenities = room.get("amenities", [])
    if amenities:
        shown = ", ".join(amenities[:15])
        lines.append(f"\n**Amenities ({len(amenities)}):** {shown}")
        if len(amenities) > 15:
            lines.append(f"_...and {len(amenities) - 15} more_")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def get_restaurant_menu(resort_code: str, restaurant_name: str) -> ToolResult:
    """Get menu and details for a specific restaurant at a resort."""
    restaurant = data_manager.get_restaurant(resort_code, restaurant_name)
    if not restaurant:
        raise ToolError(
            f"Restaurant '{restaurant_name}' not found at resort {resort_code.upper()}."
        )

    lines = [
        f"# {restaurant.get('name')}",
        f"**Cuisine:** {restaurant.get('cuisine_type', 'N/A')}",
        f"**Dress Code:** {restaurant.get('dress_code', 'Resort Casual')}",
    ]
    desc = restaurant.get("description")
    if desc:
        lines.append(f"\n{desc}")

    meals = []
    if restaurant.get("breakfast"):
        meals.append("Breakfast")
    if restaurant.get("lunch"):
        meals.append("Lunch")
    if restaurant.get("dinner"):
        meals.append("Dinner")
    if meals:
        lines.append(f"\n**Meals:** {', '.join(meals)}")

    hours = restaurant.get("hours", [])
    if hours:
        lines.append("\n**Hours:**")
        for h in hours:
            lines.append(f"- {h}")

    if restaurant.get("reservation_required"):
        lines.append("\n_Reservation required_")

    menu_links = restaurant.get("menus", [])
    if menu_links:
        lines.append("\n**Menu Links:**")
        for m in menu_links:
            lines.append(f"- {m}")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def find_rooms_by_class(room_class: str, max_results: int = 10) -> ToolResult:
    """Find rooms across all resorts by room class (e.g. BUTLER, SWIM_UP, OVERWATER)."""
    results = data_manager.find_rooms_by_class(room_class, max_results)
    if not results:
        return text_response(f"No rooms found with class '{room_class.upper()}'.")

    lines = [f"**{len(results)} room(s) with class '{room_class.upper()}'**\n"]
    for r in results:
        resort_name = r.get("resort_name", r.get("resort_code"))
        lines.append(
            f"- **{r.get('name')}** ({r.get('room_code')}) "
            f"at {resort_name} -- {r.get('island', 'N/A')}"
        )
        views = r.get("Room View(s)")
        if views:
            lines.append(f"  Views: {views}")

    return text_response("\n".join(lines))


# ---------------------------------------------------------------------------
# Availability Tools (external API calls)
# ---------------------------------------------------------------------------


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
def check_room_availability(
    resort_code: str,
    check_in_date: str,
    check_out_date: str,
    guests: int = 2,
    room_code: Optional[str] = None,
) -> ToolResult:
    """Check live room availability and pricing for specific dates at a resort.

    Args:
        resort_code: Three-letter resort code (e.g. SMB, SRC, SNG)
        check_in_date: Check-in date as YYYY-MM-DD
        check_out_date: Check-out date as YYYY-MM-DD
        guests: Number of guests (default 2)
        room_code: Optional specific room code to filter results
    """
    result = availability_checker.check_availability(
        resort_code=resort_code.upper(),
        check_in=check_in_date,
        check_out=check_out_date,
        adults=guests,
    )

    if not result.get("success"):
        raise ToolError(result.get("error", "Failed to check availability"))

    rooms = availability_checker.parse_availability_response(result)
    if room_code:
        rooms = [
            r for r in rooms if r.get("room_category_code") == room_code.upper()
        ]

    available = [r for r in rooms if r.get("available")]
    unavailable = [r for r in rooms if not r.get("available")]

    lines = [
        f"# Availability: {resort_code.upper()}",
        f"**Dates:** {check_in_date} to {check_out_date} | **Guests:** {guests}\n",
    ]

    if available:
        lines.append(f"**{len(available)} available room(s):**\n")
        for r in available:
            price = r.get("total_price_entire_stay", 0)
            per_night = r.get("adult_rate", 0)
            count = r.get("available_rooms", "?")
            lines.append(
                f"- **{r['room_category_code']}** -- "
                f"${price:,.0f} total (${per_night:,.0f}/night) -- "
                f"{count} rooms"
            )
    else:
        lines.append("**No rooms available for these dates.**")

    if unavailable and not room_code:
        lines.append(f"\n_{len(unavailable)} room category(ies) unavailable_")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
async def find_flexible_dates(
    resort_code: str,
    preferred_date: str,
    room_code: str,
    flexibility_days: int = 7,
    guests: int = 2,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Search for available dates around a preferred date for a specific room.
    Checks each day within the flexibility window -- may take a moment.

    Args:
        resort_code: Three-letter resort code
        preferred_date: Preferred check-in as YYYY-MM-DD
        room_code: Room code to search for
        flexibility_days: Days before/after to check (default 7)
        guests: Number of guests
    """
    await ctx.info(
        f"Searching {flexibility_days * 2 + 1} dates around {preferred_date} for {room_code}..."
    )

    try:
        preferred = datetime.strptime(preferred_date, "%Y-%m-%d")
    except ValueError:
        raise ToolError("Invalid date format. Use YYYY-MM-DD.")

    found = []
    total = flexibility_days * 2 + 1
    checked = 0

    for offset in range(-flexibility_days, flexibility_days + 1):
        check_in = preferred + timedelta(days=offset)
        check_out = check_in + timedelta(days=7)

        if check_in < datetime.now():
            checked += 1
            continue

        result = availability_checker.check_availability(
            resort_code=resort_code.upper(),
            check_in=check_in.strftime("%Y-%m-%d"),
            check_out=check_out.strftime("%Y-%m-%d"),
            adults=guests,
        )

        if result.get("success"):
            rooms = availability_checker.parse_availability_response(result)
            for room in rooms:
                if (
                    room.get("room_category_code") == room_code.upper()
                    and room.get("available")
                ):
                    found.append(
                        {
                            "check_in": check_in.strftime("%Y-%m-%d"),
                            "check_out": check_out.strftime("%Y-%m-%d"),
                            "offset": offset,
                            "price": room.get("total_price_entire_stay", 0),
                            "per_night": room.get("adult_rate", 0),
                        }
                    )
                    break

        checked += 1
        await ctx.report_progress(checked, total)
        await asyncio.sleep(0.5)

    lines = [
        f"# Flexible Dates: {room_code.upper()} at {resort_code.upper()}",
        f"**Preferred:** {preferred_date} | **Window:** +/-{flexibility_days} days\n",
    ]

    if found:
        lines.append(f"**{len(found)} date(s) available:**\n")
        for item in found:
            offset_label = (
                f"({item['offset']:+d} days)"
                if item["offset"] != 0
                else "(preferred)"
            )
            lines.append(
                f"- **{item['check_in']}** to {item['check_out']} "
                f"{offset_label} -- ${item['price']:,.0f} total"
            )
    else:
        lines.append("**No availability found in this window.**")

    return text_response("\n".join(lines))


# ---------------------------------------------------------------------------
# Price Monitoring Tools
# ---------------------------------------------------------------------------


@mcp.tool(annotations={"readOnlyHint": False, "openWorldHint": False})
def add_price_watch(
    resort_code: str,
    room_code: str,
    check_in_date: str,
    check_out_date: str,
    max_price: float,
    guests: int = 2,
    watch_name: Optional[str] = None,
) -> ToolResult:
    """Create a price watch that alerts via Discord when price drops below target.
    Requires DISCORD_WEBHOOK_URL environment variable.

    Args:
        resort_code: Three-letter resort code
        room_code: Room code to monitor
        check_in_date: Check-in date as YYYY-MM-DD
        check_out_date: Check-out date as YYYY-MM-DD
        max_price: Alert when total price drops below this amount
        guests: Number of guests
        watch_name: Optional friendly name for the watch
    """
    result = price_monitor.add_watch(
        resort_code=resort_code,
        room_code=room_code,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        max_price=max_price,
        guests=guests,
        watch_name=watch_name,
    )

    if result.get("error"):
        raise ToolError(result["error"])

    name = watch_name or f"{resort_code} {room_code}"
    return text_response(
        f"Price watch created: **{name}**\n"
        f"Alert when total price drops below **${max_price:,.0f}**\n"
        f"Watch ID: `{result.get('watch_id')}`"
    )


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": False})
def list_price_watches() -> ToolResult:
    """List all active price watches."""
    result = price_monitor.list_watches()

    if result.get("error"):
        raise ToolError(result["error"])

    watches = result.get("watches", [])
    if not watches:
        return text_response("No active price watches.")

    lines = [f"**{len(watches)} active watch(es)**\n"]
    for w in watches:
        last_price = w.get("last_price")
        price_str = f"${last_price:,.0f}" if last_price else "Not checked yet"
        lines.append(f"### {w.get('watch_name', 'Unnamed')}")
        lines.append(f"**ID:** `{w['watch_id']}`")
        lines.append(f"**Resort:** {w['resort_code']} | **Room:** {w['room_code']}")
        lines.append(f"**Dates:** {w['check_in_date']} to {w['check_out_date']}")
        lines.append(f"**Target:** ${w['max_price']:,.0f} | **Last Price:** {price_str}")
        lines.append("")

    return text_response("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": False, "openWorldHint": False})
def remove_price_watch(watch_id: str) -> ToolResult:
    """Remove a price watch by ID.

    Args:
        watch_id: The watch ID to remove
    """
    result = price_monitor.remove_watch(watch_id)

    if result.get("error"):
        raise ToolError(result["error"])

    return text_response(f"Price watch `{watch_id}` removed.")


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": True, "idempotentHint": True}
)
async def check_price_watches(ctx: Context = CurrentContext()) -> ToolResult:
    """Check all active price watches against current prices.
    Sends Discord notifications when prices drop below target."""
    await ctx.info("Checking all active price watches...")
    result = await price_monitor.check_all_watches()

    if result.get("error"):
        raise ToolError(result["error"])

    if result.get("message"):
        return text_response(result["message"])

    watch_results = result.get("results", [])
    notifications = result.get("notifications_sent", 0)

    lines = [
        "# Price Watch Results",
        f"**Checked:** {result.get('total_watches_checked', 0)} | "
        f"**Alerts Sent:** {notifications}\n",
    ]

    for wr in watch_results:
        status = wr.get("status")
        price = wr.get("current_price")
        target = wr.get("target_price")

        if status == "alert_sent":
            lines.append(
                f"- **{wr['watch_id']}** -- ALERT SENT! "
                f"Current: ${price:,.0f} (target: ${target:,.0f})"
            )
        elif status == "no_alert":
            price_str = f"${price:,.0f}" if price else "N/A"
            lines.append(
                f"- **{wr['watch_id']}** -- {price_str} (target: ${target:,.0f})"
            )
        elif status == "error":
            lines.append(
                f"- **{wr['watch_id']}** -- Error: {wr.get('message', 'unknown')}"
            )
        else:
            lines.append(f"- **{wr['watch_id']}** -- {status}")

    return text_response("\n".join(lines))


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------


@mcp.resource("sandals://resorts/all")
def get_all_resorts_resource() -> str:
    """All Sandals and Beaches resort codes and locations."""
    lines = []
    for code, resort in data_manager.resorts.items():
        kids = "Kids OK" if resort.get("kids_allowed") else "Adults only"
        lines.append(f"{resort.get('name')} ({code}) -- {resort.get('island')} [{kids}]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


@mcp.prompt
def plan_vacation(
    island: str,
    duration_nights: int,
    budget_range: str,
    interests: List[str],
) -> list[Message]:
    """Create a vacation planning prompt based on preferences."""
    interests_text = ", ".join(interests)
    return [
        Message(
            role="user",
            content=(
                f"Help me plan a {duration_nights}-night vacation to {island} "
                f"with a {budget_range} budget. I'm interested in: {interests_text}.\n\n"
                "Please recommend:\n"
                "1. The best Sandals resort for my preferences\n"
                "2. Specific room categories to consider\n"
                "3. Must-try restaurants\n"
                "4. Best time to visit for optimal pricing\n\n"
                "Use the Sandals BoujieBot tools to get current information."
            ),
        )
    ]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main():
    """Run the server. Uses stdio by default; set PORT env var for HTTP."""
    port = os.getenv("PORT")
    if port:
        mcp.run(
            port=int(port),
            host=os.getenv("HOST", "127.0.0.1"),
            transport="streamable-http",
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
