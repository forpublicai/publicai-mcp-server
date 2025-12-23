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
WIKI_API_URL = f"{WIKI_BASE_URL}/api.php"

# ============================================================================
# MEDIAWIKI / CARGO QUERY FUNCTIONS
# ============================================================================

def query_cargo_table(table: str, fields: str, where: str = None, limit: int = 50) -> List[Dict]:
    """Query a Cargo table from the MediaWiki instance.
    
    Args:
        table: Cargo table name (e.g., "Tools", "ToolResources")
        fields: Comma-separated list of fields to retrieve
        where: Optional WHERE clause for filtering
        limit: Maximum number of results
        
    Returns:
        List of dictionaries with query results
    """
    try:
        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': table,
            'fields': fields,
            'limit': str(limit)
        }
        
        if where:
            params['where'] = where
            
        url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        # Extract results from MediaWiki API response
        cargo_query = data.get('cargoquery', [])
        results = [item.get('title', {}) for item in cargo_query]
        
        return results
    except Exception as e:
        return [{"error": f"Failed to query Cargo table: {str(e)}"}]

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
def list_all_tools(tool_type: Optional[str] = None) -> List[Dict[str, any]]:
    """List all tools available in Public AI.
    
    Args:
        tool_type: Optional filter by tool type (e.g., "Crisis Support", "Transit", "Mapping")
        
    Returns:
        List of tools with their descriptions and types
    """
    fields = "_pageName,description,tool_type,has_resources"
    where = f"tool_type='{tool_type}'" if tool_type else None
    
    results = query_cargo_table('Tools', fields, where=where, limit=100)
    
    # Clean up the results
    tools = []
    for item in results:
        tools.append({
            'page_name': item.get('_pageName', ''),
            'description': item.get('description', ''),
            'tool_type': item.get('tool_type', ''),
            'has_resources': item.get('has_resources', 'false') == 'true',
            'url': f"{WIKI_BASE_URL}/index.php/{item.get('_pageName', '')}"
        })
    
    return tools

@mcp.tool()
def get_tool_details(tool_name: str) -> Dict[str, any]:
    """Get detailed information about a specific tool.
    
    Args:
        tool_name: Name of the tool (with or without "Tool:" prefix)
        
    Returns:
        Dictionary with tool details and available resources
    """
    # Ensure proper page name format
    if not tool_name.startswith('Tool:'):
        tool_name = f'Tool:{tool_name}'
    
    # Get tool info from Cargo
    fields = "_pageName,description,tool_type,has_resources"
    where = f"_pageName='{tool_name}'"
    tool_info = query_cargo_table('Tools', fields, where=where, limit=1)
    
    if not tool_info or 'error' in tool_info[0]:
        return {"error": f"Tool '{tool_name}' not found"}
    
    # Get associated resources
    resource_fields = "_pageName,country,region,data_field1_name,data_field1_value,data_field2_name,data_field2_value,data_field3_name,data_field3_value,data_field4_name,data_field4_value,data_field5_name,data_field5_value,additional_info,last_verified"
    where_resources = f"tool='{tool_name}'"
    resources = query_cargo_table('ToolResources', resource_fields, where=where_resources, limit=100)
    
    return {
        'tool': tool_info[0],
        'resources': resources,
        'url': f"{WIKI_BASE_URL}/index.php/{tool_name}"
    }

@mcp.tool()
def get_resources_by_country(tool_name: str, country: str) -> List[Dict[str, any]]:
    """Get resources for a specific tool filtered by country.
    
    Args:
        tool_name: Name of the tool (e.g., "SuicideHotline" or "Tool:SuicideHotline")
        country: Country name (e.g., "Singapore", "Switzerland")
        
    Returns:
        List of resources for that country
    """
    # Ensure proper page name format
    if not tool_name.startswith('Tool:'):
        tool_name = f'Tool:{tool_name}'
    
    fields = "_pageName,country,region,data_field1_name,data_field1_value,data_field2_name,data_field2_value,data_field3_name,data_field3_value,data_field4_name,data_field4_value,data_field5_name,data_field5_value,additional_info,last_verified"
    where = f"tool='{tool_name}' AND country='{country}'"
    
    results = query_cargo_table('ToolResources', fields, where=where, limit=50)
    
    # Format the results nicely
    resources = []
    for item in results:
        resource = {
            'page_name': item.get('_pageName', ''),
            'country': item.get('country', ''),
            'region': item.get('region', ''),
            'data': {},
            'additional_info': item.get('additional_info', ''),
            'last_verified': item.get('last_verified', ''),
            'url': f"{WIKI_BASE_URL}/index.php/{item.get('_pageName', '')}"
        }
        
        # Collect all data fields dynamically
        for i in range(1, 6):
            field_name = item.get(f'data_field{i}_name')
            field_value = item.get(f'data_field{i}_value')
            if field_name and field_value:
                resource['data'][field_name] = field_value
        
        resources.append(resource)
    
    return resources

@mcp.tool()
def search_resources(country: Optional[str] = None, region: Optional[str] = None) -> List[Dict[str, any]]:
    """Search for resources by country or region across all tools.
    
    Args:
        country: Optional country filter
        region: Optional region filter
        
    Returns:
        List of matching resources
    """
    fields = "_pageName,tool,country,region,data_field1_name,data_field1_value,data_field2_name,data_field2_value,last_verified"
    
    where_clauses = []
    if country:
        where_clauses.append(f"country='{country}'")
    if region:
        where_clauses.append(f"region='{region}'")
    
    where = ' AND '.join(where_clauses) if where_clauses else None
    
    results = query_cargo_table('ToolResources', fields, where=where, limit=100)
    
    return results

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