from fastmcp import FastMCP
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math
import urllib.request
import urllib.parse

mcp = FastMCP("Public AI MCP Server")

# MediaWiki API Configuration
WIKI_BASE_URL = "https://wiki.publicai.co"
WIKI_API_URL = f"{WIKI_BASE_URL}/w/api.php"

# ============================================================================
# MEDIAWIKI / CARGO QUERY FUNCTIONS
# ============================================================================

def get_wiki_page(page_title: str) -> Dict[str, any]:
    """Fetch the content of a wiki page.
    
    Args:
        page_title: Full page title (e.g., "Tool:SuicideHotline")
        
    Returns:
        Dictionary with page content and metadata
    """
    try:
        params = {
            'action': 'parse',
            'format': 'json',
            'page': page_title,
            'prop': 'text|categories|links'
        }
        
        url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        parse_result = data.get('parse', {})
        
        return {
            'title': parse_result.get('title', ''),
            'page_id': parse_result.get('pageid', ''),
            'html': parse_result.get('text', {}).get('*', ''),
            'categories': [c.get('*', '') for c in parse_result.get('categories', [])],
            'links': [l.get('*', '') for l in parse_result.get('links', [])]
        }
    except Exception as e:
        return {"error": f"Failed to fetch page: {str(e)}"}

# ============================================================================
# PUBLIC AI TOOLS - Query the Wiki
# ============================================================================

@mcp.tool()
def list_tools() -> List[Dict[str, any]]:
    """List all tools available in Public AI.

    Returns:
        List of all tools with canonical tool ID, description, type, and whether resources exist, ordered by tool name
    """
    try:
        fields = "_pageName=tool,description,tool_type=toolType,has_resources=hasResources"
        order_by = "_pageName"
        
        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'Tools',
            'fields': fields,
            'order_by': order_by,
            'limit': '500'
        }
        
        url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        cargo_query = data.get('cargoquery', [])
        results = [item.get('title', {}) for item in cargo_query]
        
        return results
    except Exception as e:
        return [{"error": f"Failed to list tools: {str(e)}"}]

@mcp.tool()
def get_tool(tool: str) -> List[Dict[str, any]]:
    """Get a specific tool by its canonical ID.

    Args:
        tool: Canonical tool ID (e.g., "Tool:SuicideHotline")

    Returns:
        List containing the tool information with canonical tool ID, description, type, and whether resources exist
    """
    try:
        # Ensure proper page name format
        if not tool.startswith('Tool:'):
            tool = f'Tool:{tool}'
        
        fields = "_pageName=tool,description,tool_type=toolType,has_resources=hasResources"
        where = f"_pageName='{tool}'"
        
        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'Tools',
            'fields': fields,
            'where': where,
            'limit': '1'
        }
        
        url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        cargo_query = data.get('cargoquery', [])
        results = [item.get('title', {}) for item in cargo_query]
        
        return results
    except Exception as e:
        return [{"error": f"Failed to get tool: {str(e)}"}]

@mcp.tool()
def list_tool_resources(tool: str) -> List[Dict[str, any]]:
    """List all resources for a specific tool.

    Args:
        tool: Canonical tool ID (e.g., "Tool:SuicideHotline")

    Returns:
        List of resources with resource page, tool, country, region, data fields, additional info, and last verified timestamp, ordered by country
    """
    try:
        # Ensure proper page name format
        if not tool.startswith('Tool:'):
            tool = f'Tool:{tool}'
        
        fields = "_pageName=resource,tool,country,region,data_field1_name,data_field1_value,data_field2_name,data_field2_value,data_field3_name,data_field3_value,data_field4_name,data_field4_value,data_field5_name,data_field5_value,additional_info,last_verified"
        where = f"tool='{tool}'"
        order_by = "country"
        
        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'ToolResources',
            'fields': fields,
            'where': where,
            'order_by': order_by,
            'limit': '500'
        }
        
        url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        cargo_query = data.get('cargoquery', [])
        results = [item.get('title', {}) for item in cargo_query]
        
        return results
    except Exception as e:
        return [{"error": f"Failed to list tool resources: {str(e)}"}]

@mcp.tool()
def list_tool_resources_by_location(tool: str, country: str, region: Optional[str] = None) -> List[Dict[str, any]]:
    """List resources for a specific tool filtered by location.

    Args:
        tool: Canonical tool ID (e.g., "Tool:SuicideHotline")
        country: Country name (required, e.g., "Singapore", "Switzerland")
        region: Optional region filter (e.g., "ZH" for Zurich)

    Returns:
        List of resources with resource page, tool, country, region, data fields, additional info, and last verified timestamp
    """
    try:
        # Ensure proper page name format
        if not tool.startswith('Tool:'):
            tool = f'Tool:{tool}'
        
        fields = "_pageName=resource,tool,country,region,data_field1_name,data_field1_value,data_field2_name,data_field2_value,data_field3_name,data_field3_value,data_field4_name,data_field4_value,data_field5_name,data_field5_value,additional_info,last_verified"
        
        # Build WHERE clause
        where_clauses = [f"tool='{tool}'", f"country='{country}'"]
        if region:
            where_clauses.append(f"region='{region}'")
        
        where = ' AND '.join(where_clauses)
        
        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'ToolResources',
            'fields': fields,
            'where': where,
            'limit': '500'
        }
        
        url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        cargo_query = data.get('cargoquery', [])
        results = [item.get('title', {}) for item in cargo_query]
        
        return results
    except Exception as e:
        return [{"error": f"Failed to list tool resources by location: {str(e)}"}]

# ============================================================================
# SWISS TRANSIT TOOLS (Your existing tools)
# ============================================================================

@mcp.tool()
def search_swiss_stations(query: str, limit: int = 10) -> List[Dict[str, any]]:
    """Search for Swiss public transport stations (train, bus, tram).

    Args:
        query: Station name to search for (e.g., "Zürich", "Bern")
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of stations with id, name, and coordinates
    """
    try:
        url = f"http://transport.opendata.ch/v1/locations?query={urllib.parse.quote(query)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        stations = data.get('stations', [])[:limit]
        return [
            {
                'id': s['id'],
                'name': s['name'],
                'coordinates': {
                    'lat': s['coordinate']['x'],
                    'lon': s['coordinate']['y']
                },
                'type': s.get('icon', 'unknown')
            }
            for s in stations
        ]
    except Exception as e:
        return [{"error": f"Failed to search stations: {str(e)}"}]

@mcp.tool()
def get_swiss_departures(station: str, limit: int = 10) -> Dict[str, any]:
    """Get real-time departures from a Swiss public transport station.

    Args:
        station: Station name or ID (e.g., "Zürich HB", "Bern")
        limit: Number of departures to return (default: 10, max: 40)

    Returns:
        Dictionary with station info and list of upcoming departures with delays
    """
    try:
        url = f"http://transport.opendata.ch/v1/stationboard?station={urllib.parse.quote(station)}&limit={min(limit, 40)}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        station_info = data.get('station', {})
        stationboard = data.get('stationboard', [])

        departures = []
        for item in stationboard:
            stop = item.get('stop', {})
            prognosis = stop.get('prognosis', {})

            scheduled_time = stop.get('departure', '')
            actual_time = prognosis.get('departure', scheduled_time)
            delay = stop.get('delay', 0)

            departures.append({
                'time': scheduled_time,
                'actual_time': actual_time,
                'delay_minutes': delay,
                'platform': stop.get('platform', 'N/A'),
                'type': item.get('category', ''),
                'number': item.get('number', ''),
                'to': item.get('to', ''),
                'operator': item.get('operator', '')
            })

        return {
            'station': station_info.get('name', station),
            'station_id': station_info.get('id', ''),
            'departures': departures
        }
    except Exception as e:
        return {"error": f"Failed to get departures: {str(e)}"}

@mcp.tool()
def plan_swiss_journey(
    from_station: str,
    to_station: str,
    via_station: Optional[str] = None,
    limit: int = 4
) -> List[Dict[str, any]]:
    """Plan a journey on Swiss public transport with real-time connections.

    Args:
        from_station: Departure station name (e.g., "Zürich HB")
        to_station: Arrival station name (e.g., "Bern")
        via_station: Optional intermediate station (e.g., "Olten")
        limit: Number of connection options to return (default: 4, max: 6)

    Returns:
        List of journey options with times, platforms, transfers, and products
    """
    try:
        url = f"http://transport.opendata.ch/v1/connections?from={urllib.parse.quote(from_station)}&to={urllib.parse.quote(to_station)}&limit={min(limit, 6)}"
        if via_station:
            url += f"&via[]={urllib.parse.quote(via_station)}"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        connections = data.get('connections', [])

        journeys = []
        for conn in connections:
            from_info = conn.get('from', {})
            to_info = conn.get('to', {})

            journey = {
                'departure': {
                    'station': from_info.get('station', {}).get('name', ''),
                    'time': from_info.get('departure', ''),
                    'platform': from_info.get('platform', 'N/A'),
                    'delay_minutes': from_info.get('delay', 0)
                },
                'arrival': {
                    'station': to_info.get('station', {}).get('name', ''),
                    'time': to_info.get('arrival', ''),
                    'platform': to_info.get('platform', 'N/A'),
                    'delay_minutes': to_info.get('delay', 0) if to_info.get('delay') else None
                },
                'duration': conn.get('duration', ''),
                'transfers': conn.get('transfers', 0),
                'products': conn.get('products', [])
            }

            journeys.append(journey)

        return journeys
    except Exception as e:
        return [{"error": f"Failed to plan journey: {str(e)}"}]

# ============================================================================
# OPENSTREETMAP NOMINATIM SEARCH
# ============================================================================

@mcp.tool()
def search_osm_nominatim(query: str, limit: int = 10) -> List[Dict[str, any]]:
    """Search OpenStreetMap for a location using Nominatim.
    
    Args:
        query: Natural language search query (e.g., "Eiffel Tower", "London Bridge")
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        List of locations with address, coordinates, and other details
    """
    try:
        params = {
            'q': query,
            'format': 'json',
            'limit': str(limit),
            'addressdetails': '1'
        }
        
        url = f"https://nominatim.openstreetmap.org/search?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'PublicAI-MCP-Server/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        results = []
        for item in data:
            results.append({
                'display_name': item.get('display_name', ''),
                'lat': item.get('lat', ''),
                'lon': item.get('lon', ''),
                'type': item.get('type', ''),
                'category': item.get('class', ''),
                'importance': item.get('importance', 0),
                'address': item.get('address', {}),
                'osm_id': item.get('osm_id', ''),
                'osm_type': item.get('osm_type', '')
            })
        
        return results
    except Exception as e:
        return [{"error": f"Failed to search OSM: {str(e)}"}]

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)