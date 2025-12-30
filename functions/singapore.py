"""Singapore API-based MCP functions using data.gov.sg"""

from fastmcp import FastMCP
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Any


# HDB Carpark Information Dataset ID
HDB_CARPARK_DATASET_ID = "d_23f946fa557947f93a8043bbef41dd09"


def register_singapore_functions(mcp: FastMCP):
    """Register Singapore MCP functions"""

    @mcp.tool()
    def search_singapore_carparks(
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search for HDB carparks by location, area name, or carpark number.

        Args:
            query: Search term (e.g., "Bedok", "Ang Mo Kio", "ACB", "Block 123")
            limit: Maximum number of results to return (default: 10, max: 100)

        Returns:
            Dictionary with total results found and list of matching carparks with number and address
        """
        try:
            params = {
                'resource_id': HDB_CARPARK_DATASET_ID,
                'q': query,
                'fields': 'car_park_no,address',
                'limit': min(limit, 100)
            }

            url = f"https://data.gov.sg/api/action/datastore_search?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            if not data.get('success'):
                return {"error": "Failed to search carparks", "details": data.get('error', {})}

            result = data.get('result', {})
            records = result.get('records', [])
            total = result.get('total', 0)

            carparks = []
            for record in records:
                carparks.append({
                    'carpark_number': record.get('car_park_no', ''),
                    'address': record.get('address', '')
                })

            return {
                'total_found': total,
                'showing': len(carparks),
                'carparks': carparks
            }

        except Exception as e:
            return {"error": f"Failed to search carparks: {str(e)}"}

    @mcp.tool()
    def get_singapore_carpark_availability(
        carpark_number: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
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
