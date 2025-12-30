# Contributing to Public AI

Public AI has two types of contributions: **Wiki Tools** (data on the wiki) and **MCP Functions** (Python code). Your contribution path depends on what you want to add or improve.

## Understanding Wiki Tools vs MCP Functions

### Wiki Tools
**What they are:** Structured data stored in the wiki using MediaWiki Cargo. MCP functions read from the wiki and serve the data to AI assistants.

**Examples:**
- **SuicideHotline**: Hotline numbers stored in ToolResources table
- **UpcomingBTO**: BTO launch details stored in wiki page content

**Who can contribute:** Anyone! No coding required. Edit the wiki directly.

**Best for:**
- Location-specific resources (phone numbers, addresses, websites)
- Information that changes over time
- Data that needs localization for different countries/regions
- Content that community members can verify and update

---

### MCP Functions
**What they are:** Python code in the MCP server repository. These typically integrate with external APIs or perform complex data processing.

**Examples:**
- **Swiss Transit Functions**: Call Switzerland's public transport API
- **Singapore Functions**: Real-time carpark availability

**Who can contribute:** Developers with Python experience

**Best for:**
- API integrations (e.g., weather APIs, transit APIs)
- Complex data transformations
- Real-time data that can't be stored in the wiki
- Functions requiring authentication or rate limiting

---

## Contribution Pathways

### 1️⃣ Improve a Wiki Tool
**Add or update localized data for an existing tool**

**Difficulty:** Easy (no coding required)

**Steps:**
1. Browse the [list of all tools](Special:CargoTables)
2. Find a tool with `has_resources=true` that's relevant to your location
3. Create a new resource page: `Resource:ToolName/YourLocation`
4. Use the `{{ToolResource}}` template to add your data
5. Save and rebuild the Cargo table

**Example: Adding Singapore suicide hotline**
```wiki
{{ToolResource
|tool=Tool:SuicideHotline
|country=Singapore
|region=National
|data_field1_name=Phone of National Mindline
|data_field1_value=dialling 1771
|data_field2_name=Text Service
|data_field2_value=WhatsApp at +65-6669-1771
|data_field3_name=Online Chat
|data_field3_value=https://mindline.sg/fsmh
|additional_info=All services are confidential and free. Support available in English, Mandarin, Malay, and Tamil.
|last_verified=2025-12-26
}}
```

**For technically-minded contributors:**
You can set up automations (GitHub Actions, cron jobs, etc.) to periodically update wiki data via the MediaWiki API. This is useful for tools like UpcomingBTO where information changes regularly.

---

### 2️⃣ Add a New Wiki Tool
**Create a new tool where the data lives in the wiki**

**Difficulty:** Easy to Medium

**When to use this:**
- You have location-specific data to contribute
- The data doesn't require API calls
- Community members can verify and maintain the information

**Steps:**
1. Create a new page: `Tool:YourToolName`
2. Use the `{{Tool}}` template
3. Set `has_resources=true` if you'll add location-specific data
4. Add your initial resources (see Pathway #1)
5. Save and rebuild the Cargo table

**Example: Library Hours Tool**
```wiki
{{Tool
|name=Public Library Hours
|description=Operating hours for public libraries by location
|community=Singapore
|has_resources=true
|overview=Provides current operating hours for public libraries across Singapore, including special hours for holidays and events.
|usage=Query by library name or region to get current hours.
}}
```

Then add resources:
```wiki
{{ToolResource
|tool=Tool:PublicLibraryHours
|country=Singapore
|region=Central
|data_field1_name=Library Name
|data_field1_value=National Library Building
|data_field2_name=Weekday Hours
|data_field2_value=10:00 AM - 9:00 PM
|data_field3_name=Weekend Hours
|data_field3_value=10:00 AM - 5:00 PM
|additional_info=Closed on public holidays
|last_verified=2025-12-26
}}
```

---

### 3️⃣ Add a New MCP Function
**Implement a function with Python code that integrates with external APIs**

**Difficulty:** Advanced (requires Python/coding)

**When to use this:**
- You need to call external APIs
- The function requires real-time data (weather, transit, stock prices)
- Complex logic or data transformation is needed
- The data can't be reasonably stored in the wiki

**Steps:**
1. Fork the [pai-mcp-server repository](https://github.com/yourusername/pai-mcp-server)
2. Create a new file in the `functions/` folder (e.g., `functions/weather.py`)
3. Implement your function module:
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
               # Call weather API
               url = f"https://api.weather.gov/alerts?country={country}"
               with urllib.request.urlopen(url, timeout=10) as response:
                   data = json.loads(response.read().decode())

               alerts = []
               for alert in data.get('features', []):
                   alerts.append({
                       'event': alert['properties']['event'],
                       'severity': alert['properties']['severity'],
                       'description': alert['properties']['description']
                   })

               return alerts
           except Exception as e:
               return [{"error": f"Failed to get alerts: {str(e)}"}]
   ```
4. Update `main.py` to import and register your functions:
   ```python
   from functions.weather import register_weather_functions
   register_weather_functions(mcp)
   ```
5. Test locally: `uv run main.py`
6. Submit a Pull Request with:
   - Clear description of what the function does
   - Why it's valuable for AI assistants
   - Any API keys or credentials needed (use environment variables)
   - Example usage

---

## Quick Decision Tree

**I want to contribute data/resources for an existing tool**
→ Use Pathway #1 (Improve a Wiki Tool)

**I want to create a tool with location-specific data that I can maintain**
→ Use Pathway #2 (Add a New Wiki Tool)

**I want to integrate with an external API or build something requiring code**
→ Use Pathway #3 (Add a New MCP Function)

---

## Quality Guidelines

### For All Contributions:
- ✅ Information must be current and verified
- ✅ Include `last_verified` dates for wiki data
- ✅ Test before submitting
- ✅ Follow existing naming conventions
- ✅ Provide clear descriptions

### For Wiki Tools:
- ✅ Use consistent field names across resources
- ✅ Include all relevant contact methods
- ✅ Localize information appropriately
- ✅ Keep `additional_info` concise but helpful

### For MCP Functions:
- ✅ Handle errors gracefully
- ✅ Set appropriate timeouts for API calls (10s default)
- ✅ Return consistent data structures
- ✅ Document required parameters clearly
- ✅ Don't hardcode secrets (use environment variables)
- ✅ Create one file per API/service in the `functions/` folder
- ✅ Use the `register_*_functions(mcp)` pattern

---

## Need Help?

- **Wiki editing questions**: Check the wiki templates and documentation
- **MCP function questions**: See the [FastMCP documentation](https://github.com/jlowin/fastmcp)
- **General questions**: Open an issue in the repository

## Examples to Learn From

### Good Wiki Tools:
- **SuicideHotline**: Clean resource structure with location-specific data
- **UpcomingBTO**: Rich page content with detailed information

### Good MCP Functions:
- See `functions/swiss_transport.py` - Simple API integration pattern
- See `functions/wiki.py` - Complex wiki queries with error handling
- See `functions/singapore.py` - Real-time data API integration
