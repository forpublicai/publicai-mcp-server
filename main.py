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
# PUBLIC AI TOOLS - Consolidated MediaWiki/Cargo Query Functions
# ============================================================================

@mcp.tool()
def list_tools_by_community(community: str) -> List[Dict[str, any]]:
    """List all tools available for a specific community.

    Args:
        community: Community name (e.g., "Switzerland", "Singapore", "Lorong AI")

    Returns:
        List of tools with page name, description, community, and whether they have resources
    """
    try:
        fields = "_pageName=Page,description,community,has_resources"
        where = f"community HOLDS \"{community}\""

        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'Tools',
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
        return [{"error": f"Failed to list tools for community: {str(e)}"}]

@mcp.tool()
def use_tool(tool: str, country: Optional[str] = None, region: Optional[str] = None) -> Dict[str, any]:
    """Use a Public AI tool. For tools with location-specific resources, provide country/region.
    For tools without resources, returns the full page content.

    Args:
        tool: Tool name or canonical ID (e.g., "SuicideHotline" or "Tool:SuicideHotline")
        country: Country name for location-based resources (e.g., "Singapore", "Switzerland")
        region: Optional region for more specific results (e.g., "ZH" for Zurich)

    Returns:
        Dictionary with tool information and either resources (for location-based tools) or page content
    """
    try:
        # Ensure proper page name format
        if not tool.startswith('Tool:'):
            tool = f'Tool:{tool}'

        # First, get the tool metadata to check if it has resources
        tool_fields = "_pageName=Page,description,community,has_resources"
        tool_where = f"_pageName='{tool}'"

        tool_params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'Tools',
            'fields': tool_fields,
            'where': tool_where,
            'limit': '1'
        }

        tool_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(tool_params)}"

        with urllib.request.urlopen(tool_url, timeout=10) as response:
            tool_data = json.loads(response.read().decode())

        cargo_query = tool_data.get('cargoquery', [])
        if not cargo_query:
            return {"error": f"Tool '{tool}' not found"}

        tool_info = cargo_query[0].get('title', {})
        has_resources = tool_info.get('has resources', '0') == '1'

        result = {
            'tool': tool_info.get('Page', ''),
            'description': tool_info.get('description', ''),
            'community': tool_info.get('community', ''),
            'has_resources': has_resources
        }

        if has_resources:
            # Tool has location-specific resources, query ToolResources table
            if not country:
                return {
                    **result,
                    'error': 'This tool requires a country parameter to fetch location-specific resources',
                    'usage': f'use_tool(tool="{tool}", country="Singapore") or use_tool(tool="{tool}", country="Switzerland")'
                }

            resource_fields = "tool,country,region,data_field1_name,data_field1_value,data_field2_name,data_field2_value,data_field3_name,data_field3_value,data_field4_name,data_field4_value,data_field5_name,data_field5_value,additional_info,last_verified"

            # Build WHERE clause for resources
            where_clauses = [f"tool='{tool}'", f"country='{country}'"]
            if region:
                where_clauses.append(f"region='{region}'")

            resource_where = ' AND '.join(where_clauses)

            resource_params = {
                'action': 'cargoquery',
                'format': 'json',
                'tables': 'ToolResources',
                'fields': resource_fields,
                'where': resource_where,
                'limit': '500'
            }

            resource_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(resource_params)}"

            with urllib.request.urlopen(resource_url, timeout=10) as response:
                resource_data = json.loads(response.read().decode())

            resources = [item.get('title', {}) for item in resource_data.get('cargoquery', [])]
            result['resources'] = resources

        else:
            # Tool doesn't have resources, fetch the page content
            parse_params = {
                'action': 'parse',
                'format': 'json',
                'page': tool,
                'prop': 'text'
            }

            parse_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(parse_params)}"

            with urllib.request.urlopen(parse_url, timeout=10) as response:
                parse_data = json.loads(response.read().decode())

            parse_result = parse_data.get('parse', {})
            result['content'] = parse_result.get('text', {}).get('*', '')
            result['page_url'] = f"{WIKI_BASE_URL}/wiki/{tool.replace(':', '/')}"

        return result

    except Exception as e:
        return {"error": f"Failed to use tool: {str(e)}"}

# ============================================================================
# SWISS TOOLS 
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
# Singapore TOOLS
# ============================================================================

@mcp.tool()
def get_singapore_carpark_availability(
    carpark_number: Optional[str] = None,
    limit: int = 50
) -> Dict[str, any]:
    """Get real-time carpark availability across Singapore (updated every minute).

    Args:
        carpark_number: Optional specific carpark number to query (e.g., "HE12", "ACB")
        limit: Maximum number of carparks to return (default: 50)

    Returns:
        Dictionary with timestamp and list of carparks with availability info
    """
    try:
        url = "https://api.data.gov.sg/v1/transport/carpark-availability"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        items = data.get('items', [])
        if not items:
            return {"error": "No carpark data available"}

        latest = items[0]
        timestamp = latest.get('timestamp', '')
        carpark_data = latest.get('carpark_data', [])

        # Filter by carpark number if specified
        if carpark_number:
            carpark_data = [cp for cp in carpark_data if cp.get('carpark_number') == carpark_number]
            if not carpark_data:
                return {
                    "error": f"Carpark '{carpark_number}' not found",
                    "timestamp": timestamp
                }

        # Process carpark data
        carparks = []
        for cp in carpark_data[:limit]:
            carpark_info = {
                'carpark_number': cp.get('carpark_number', ''),
                'update_datetime': cp.get('update_datetime', ''),
                'lots': []
            }

            for lot_info in cp.get('carpark_info', []):
                carpark_info['lots'].append({
                    'lot_type': lot_info.get('lot_type', ''),
                    'total_lots': lot_info.get('total_lots', ''),
                    'lots_available': lot_info.get('lots_available', '')
                })

            carparks.append(carpark_info)

        return {
            'timestamp': timestamp,
            'total_results': len(carpark_data),
            'showing': len(carparks),
            'carparks': carparks
        }
    except Exception as e:
        return {"error": f"Failed to get carpark availability: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)