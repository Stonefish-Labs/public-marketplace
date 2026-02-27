# Google Maps MCP Server

A Python FastMCP server that provides access to Google Maps APIs for location services, geocoding, place search, directions, and more.

## Features

- **Geocoding**: Convert addresses to geographic coordinates
- **Reverse Geocoding**: Convert coordinates to addresses
- **Place Search**: Find places using text queries
- **Place Details**: Get comprehensive information about specific places
- **Distance Matrix**: Calculate travel distances and times between multiple points
- **Elevation Data**: Get elevation information for locations
- **Directions**: Get turn-by-turn driving/walking directions
- **Caching**: Automatic response caching to reduce API calls and improve performance
- **Clean Output**: Human-readable formatted responses using the `utils.py` pattern

## Setup

### 1. Google Maps API Key

Get a Google Maps API key by following the instructions [here](https://developers.google.com/maps/documentation/javascript/get-api-key).

### 2. API Key Configuration

The server uses an interactive elicitation process to securely obtain your Google Maps API key. When you first run a tool, you'll be prompted to enter your API key, which will then be stored in the system's internal keyring for future use.

If the keyring is unavailable or fails, the server will fall back to interactive elicitation on each request.

### 3. Dependencies

The server uses `httpx` for HTTP requests and `fastmcp` for the MCP framework. These are included in the project's `pyproject.toml`.

## Tools

### `maps_geocode`
Convert an address into geographic coordinates.

**Input:**
- `address` (string): The address to geocode

**Example:**
```
maps_geocode("1600 Amphitheatre Parkway, Mountain View, CA")
```

**Output:**
```
📍 **Geocoding Result**

**Address:** 1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA
**Place ID:** ChIJ2eUgeAK6j4ARbn5u_wAg
**Coordinates:** 37.4223878, -122.0841877
```

### `maps_reverse_geocode`
Convert coordinates into an address.

**Input:**
- `latitude` (number): Latitude coordinate
- `longitude` (number): Longitude coordinate

**Example:**
```
maps_reverse_geocode(37.4223878, -122.0841877)
```

### `maps_search_places`
Search for places using Google Places API.

**Input:**
- `query` (string): Search query
- `latitude` (optional): Latitude for location bias
- `longitude` (optional): Longitude for location bias
- `radius` (optional): Search radius in meters (max 50000)

**Example:**
```
maps_search_places("pizza near me", 37.4223878, -122.0841877, 5000)
```

### `maps_place_details`
Get detailed information about a specific place.

**Input:**
- `place_id` (string): The place ID from a search result

**Example:**
```
maps_place_details("ChIJ2eUgeAK6j4ARbn5u_wAg")
```

### `maps_distance_matrix`
Calculate travel distance and time for multiple origins and destinations.

**Input:**
- `origins` (string[]): Array of origin addresses or coordinates
- `destinations` (string[]): Array of destination addresses or coordinates
- `mode` (optional): Travel mode ("driving", "walking", "bicycling", "transit")

**Example:**
```
maps_distance_matrix(
  ["New York, NY", "Boston, MA"],
  ["Washington, DC", "Philadelphia, PA"],
  "driving"
)
```

### `maps_elevation`
Get elevation data for locations on the earth.

**Input:**
- `locations` (array): Array of {latitude, longitude} objects

**Example:**
```
maps_elevation([
  {"latitude": 37.4223878, "longitude": -122.0841877},
  {"latitude": 40.7128, "longitude": -74.0060}
])
```

### `maps_directions`
Get directions between two points.

**Input:**
- `origin` (string): Starting point address or coordinates
- `destination` (string): Ending point address or coordinates
- `mode` (optional): Travel mode ("driving", "walking", "bicycling", "transit")

**Example:**
```
maps_directions("New York, NY", "Boston, MA", "driving")
```

## Running the Server

### Local Development

```bash
cd mcp-servers/google-maps-server

# Run via project script entrypoint
uv run server

# Or directly
python server.py
```

### MCP Configuration

Add to your MCP configuration file (e.g., `mcp.json`):

```json
{
  "mcpServers": {
    "google-maps-mcp": {
      "type": "stdio",
      "command": "uv",
        "args": [
          "--directory",
          "/path/to/google-maps-server/mcp-servers/google-maps-server",
          "run",
          "server"
        ]
    }
  }
}
```

## Architecture

The server follows the same patterns as the `findmy-server`:

- **`server.py`**: Main entrypoint with FastMCP server setup
- **`tools_maps.py`**: All Google Maps API tool implementations
- **`formatter.py`**: Clean, human-readable output formatting
- **`credentials.py`**: Secure API key management
- **`cache.py`**: Response caching to reduce API calls
- **`utils.py`**: Utility functions for clean output (copied from findmy-server)

All runtime files live in `mcp-servers/google-maps-server/`.

## Caching

The server automatically caches API responses for 10 minutes to:
- Reduce API usage and costs
- Improve response times
- Handle temporary network issues

Cache keys are generated based on the request parameters, so identical requests will use cached results.

## Error Handling

All tools include comprehensive error handling:
- API errors are caught and formatted cleanly
- Network issues are handled gracefully
- Invalid parameters return helpful error messages
- All errors use the same `format_error_message` function for consistency


## License

This MCP server is licensed under the MIT License.
