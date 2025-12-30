"""Swiss transport API-based MCP functions using transport.opendata.ch"""

from fastmcp import FastMCP
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Any


def register_swiss_transport_functions(mcp: FastMCP):
    """Register Swiss transport MCP functions"""

    @mcp.tool()
    def search_swiss_stations(query: str, limit: int = 10) -> List[Dict[str, Any]]:
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
    def get_swiss_departures(station: str, limit: int = 10) -> Dict[str, Any]:
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
    ) -> List[Dict[str, Any]]:
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
