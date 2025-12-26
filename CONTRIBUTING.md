# Contributing to Public AI Wiki

Public AI has two types of tools, and your contribution path depends on what you want to add or improve.

## Understanding Tool Types

### Wiki Tools
**What they are:** Tools where the data and content live in this wiki. The MCP server simply reads from the wiki and serves it to AI assistants.

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

### MCP Tools
**What they are:** Tools implemented as Python code in the MCP server repository. These typically integrate with external APIs or perform complex data processing.

**Examples:**
- **Swiss Transit**: Calls Switzerland's public transport API
- **OSM Nominatim**: Searches OpenStreetMap for locations

**Who can contribute:** Developers with Python experience

**Best for:**
- API integrations (e.g., weather APIs, transit APIs)
- Complex data transformations
- Real-time data that can't be stored in the wiki
- Tools requiring authentication or rate limiting

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

### 3️⃣ Add a New MCP Tool
**Implement a tool with Python code that integrates with external APIs**

**Difficulty:** Advanced (requires Python/coding)

**When to use this:**
- You need to call external APIs
- The tool requires real-time data (weather, transit, stock prices)
- Complex logic or data transformation is needed
- The data can't be reasonably stored in the wiki

**Steps:**
1. Fork the [pai-mcp-server repository](https://github.com/yourusername/pai-mcp-server)
2. Add your tool function to `main.py`:
   ```python
   @mcp.tool()
   def your_new_tool(param1: str, param2: Optional[str] = None) -> Dict[str, any]:
       """Tool description.

       Args:
           param1: Description of parameter
           param2: Optional parameter description

       Returns:
           Dictionary with results
       """
       try:
           # Your implementation here
           # Call external APIs, process data, etc.
           return {"result": "data"}
       except Exception as e:
           return {"error": f"Failed: {str(e)}"}
   ```
3. Test locally: `python main.py`
4. Submit a Pull Request with:
   - Clear description of what the tool does
   - Why it's valuable for AI assistants
   - Any API keys or credentials needed (use environment variables)
   - Example usage

**Example: Weather API Integration**
```python
@mcp.tool()
def get_weather_alerts(country: str, region: Optional[str] = None) -> List[Dict[str, any]]:
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

---

## Quick Decision Tree

**I want to contribute data/resources for an existing tool**
→ Use Pathway #1 (Improve a Wiki Tool)

**I want to create a tool with location-specific data that I can maintain**
→ Use Pathway #2 (Add a New Wiki Tool)

**I want to integrate with an external API or build something requiring code**
→ Use Pathway #3 (Add a New MCP Tool)

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

### For MCP Tools:
- ✅ Handle errors gracefully
- ✅ Set appropriate timeouts for API calls
- ✅ Return consistent data structures
- ✅ Document required parameters clearly
- ✅ Don't hardcode secrets (use environment variables)

---

## Need Help?

- **Wiki editing questions**: Check [Template:Tool](Template:Tool) and [Template:ToolResource](Template:ToolResource)
- **MCP tool questions**: See the [FastMCP documentation](https://github.com/jlowin/fastmcp)
- **General questions**: Open an issue in the repository

## Examples to Learn From

### Good Wiki Tools:
- [Tool:SuicideHotline](Tool:SuicideHotline) - Clean resource structure
- [Tool:UpcomingBTO](Tool:UpcomingBTO) - Rich page content

### Good MCP Tools:
- See `search_swiss_stations()` in main.py - Simple API integration
- See `plan_swiss_journey()` in main.py - Complex API with parameters
