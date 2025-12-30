# Public AI MCP Server

A FastMCP server that provides AI assistants with access to current, community-maintained information and real-time services.

## What is Public AI?

Public AI bridges the gap between AI assistants and real-world information. Instead of relying on outdated training data, AI assistants can query this MCP server to access:

- **Community-maintained data** from [wiki.publicai.co](https://wiki.publicai.co)
- **Real-time APIs** for transit, parking, and location services
- **Localized resources** like crisis hotlines, emergency services, and community information

## How It Works

```
AI Assistant (Claude, etc.)
    ↓ queries
MCP Server (this repository)
    ↓ fetches from
    ├─→ Wiki (community data)
    └─→ External APIs (real-time data)
```

### Understanding Wiki Tools vs MCP Functions

**This repository contains MCP functions** - Python code that AI assistants can call. These functions access two types of data:

**1. Wiki-Based Functions** (access community-maintained data)
- Read from [wiki.publicai.co](https://wiki.publicai.co) where community members maintain **Wiki Tools**
- Wiki Tools = structured data stored using MediaWiki Cargo (database-like tables)
- Examples: Crisis hotlines, BTO launches, community events
- **To contribute data**: Edit Wiki Tools on the wiki (no coding required)
- **To add new tool types**: Create new Wiki Tool with Cargo schema on wiki + add MCP function here

**2. API-Based Functions** (real-time integrations)
- Call external APIs for live data (transit, parking, maps)
- Examples: Swiss transport, Singapore carpark availability
- **To contribute**: Add Python code to this repository

### Example Flow

1. **User asks AI a question**: "What's the suicide hotline in Singapore?"
2. **AI calls MCP function**: `use_tool(tool="SuicideHotline", country="Singapore")`
3. **MCP function queries wiki**: Reads from SuicideHotline Wiki Tool's Cargo database
4. **AI gets current info**: Returns verified, community-maintained resources

## Available MCP Functions

### Wiki-Based Functions
Functions that read community-maintained Wiki Tools from wiki.publicai.co:

#### `list_tools_by_community(community: str)`
List all tools available for a specific community.

**Example:**
```python
list_tools_by_community(community="Switzerland")
# Returns: List of tools tagged with "Switzerland"
```

#### `use_tool(tool: str, country: Optional[str] = None, region: Optional[str] = None)`
Use a Public AI tool. Automatically adapts based on whether the tool has location-specific resources.

**For tools with resources (e.g., SuicideHotline):**
```python
use_tool(tool="SuicideHotline", country="Singapore")
# Returns: Crisis hotline numbers and resources for Singapore
```

**For tools without resources (e.g., UpcomingBTO):**
```python
use_tool(tool="UpcomingBTO")
# Returns: Full page content about BTO launches
```

### API-Based Functions: Swiss Transport
Real-time Swiss public transport information via [transport.opendata.ch](https://transport.opendata.ch):

#### `search_swiss_stations(query: str, limit: int = 10)`
Search for train, bus, and tram stations.

```python
search_swiss_stations(query="Zürich HB")
```

#### `get_swiss_departures(station: str, limit: int = 10)`
Get real-time departures with delay information.

```python
get_swiss_departures(station="Bern", limit=5)
```

#### `plan_swiss_journey(from_station: str, to_station: str, via_station: Optional[str] = None, limit: int = 4)`
Plan journeys with real-time connections.

```python
plan_swiss_journey(from_station="Zürich HB", to_station="Geneva")
```

### API-Based Functions: Singapore
Location services for Singapore:

#### `get_singapore_carpark_availability()`
Get real-time carpark availability data.

```python
get_singapore_carpark_availability()
```

### API-Based Functions: OpenStreetMap

#### `search_osm_nominatim(query: str, limit: int = 10)`
Search for locations worldwide using OpenStreetMap.

```python
search_osm_nominatim(query="Eiffel Tower", limit=5)
```

## Installation

### Prerequisites
- Python 3.8+
- FastMCP

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pai-mcp-server.git
cd pai-mcp-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://127.0.0.1:8000`.

## Configuration

### Using with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "publicai": {
      "command": "python",
      "args": ["/path/to/pai-mcp-server/main.py"]
    }
  }
}
```

### Environment Variables

Currently, no environment variables are required. Future API integrations may require API keys.

## Contributing

Public AI has two contribution pathways:

### 1. Contribute Data (No Coding Required)
Add or update **Wiki Tools** on [wiki.publicai.co](https://wiki.publicai.co):
- Crisis hotline numbers for your country
- BTO launch information
- Community events and resources
- Verify and update existing data

**See:** [Wiki Contribution Guide](https://wiki.publicai.co)

### 2. Add MCP Functions (Python Required)
Integrate new APIs or build functions that require real-time data:

1. Fork this repository
2. Add your Python file to the `functions/` folder
3. Test locally
4. Submit a Pull Request

**See:** [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines

#### Example: Adding a New Function

Create a new file in `functions/weather.py`:

```python
from fastmcp import FastMCP
import json
import urllib.request
from typing import List, Dict, Optional, Any

def register_weather_functions(mcp: FastMCP):
    """Register weather-related MCP functions"""

    @mcp.tool()
    def get_weather_alerts(country: str, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get severe weather alerts for a location.

        Args:
            country: Country name (e.g., "Singapore", "Switzerland")
            region: Optional region/state

        Returns:
            List of active weather alerts
        """
        try:
            # Your implementation here
            url = f"https://api.weather.service/alerts?country={country}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            return data.get('alerts', [])
        except Exception as e:
            return [{"error": f"Failed to get alerts: {str(e)}"}]
```

The function will be automatically loaded by `main.py`.

#### Guidelines for MCP Functions

- ✅ Handle errors gracefully
- ✅ Set appropriate timeouts (10s default)
- ✅ Return consistent data structures
- ✅ Document parameters clearly
- ✅ Use environment variables for API keys
- ✅ Create one file per API/service for easy maintenance

## Architecture

### Wiki-Based Functions Architecture
```
1. Community edits Wiki Tools on wiki.publicai.co
2. MediaWiki stores data in Cargo tables
3. MCP functions query Cargo API
4. AI assistant gets fresh, community-maintained data
```

### API-Based Functions Architecture
```
1. AI assistant calls MCP function
2. Function makes API request to external service
3. Function processes and formats response
4. AI assistant gets real-time data
```

## Use Cases

### Crisis Support
```
User: "I'm in Switzerland and need mental health support"
AI: [Calls use_tool(tool="SuicideHotline", country="Switzerland")]
AI: "You can reach Die Dargebotene Hand at 143 (24/7), or via WhatsApp..."
```

### Transit Planning
```
User: "When's the next train from Zürich to Bern?"
AI: [Calls plan_swiss_journey(from_station="Zürich HB", to_station="Bern")]
AI: "The next train departs at 14:32 from platform 8, arriving at 15:28..."
```

### Community Information
```
User: "What BTO launches are coming up in Singapore?"
AI: [Calls use_tool(tool="UpcomingBTO")]
AI: "The February 2026 BTO launch includes projects in Bukit Merah, Sembawang..."
```

## Why MCP?

The Model Context Protocol (MCP) allows AI assistants to access tools and data sources in a standardized way. This server:

- **Stays current**: Community can update wiki data anytime
- **Scales easily**: Add new tools without retraining AI models
- **Community-driven**: Non-technical people can contribute data
- **Privacy-focused**: No user data stored, only serves public information

## Technical Details

### Dependencies
- **FastMCP**: MCP server framework
- **urllib**: HTTP requests (no external dependencies)
- **json**: Data parsing

### API Endpoints Used
- MediaWiki Cargo API: `https://wiki.publicai.co/w/api.php`
- Swiss Transport: `http://transport.opendata.ch/v1/`
- OpenStreetMap Nominatim: `https://nominatim.openstreetmap.org/`

### Data Format
All tools return either:
- `List[Dict[str, any]]`: For list-based results
- `Dict[str, any]`: For single results

Errors are returned as `{"error": "message"}` within the response structure.

## License

MIT License - See LICENSE file for details

**Built for the community, by the community.**
