# Swiss Public Transport Tools

## `search_swiss_stations`
Search for train, bus, and tram stations across Switzerland

**Example queries:**
- "Search for stations in Zürich"
- "Find stations near Lausanne"
- "Show me train stations in Geneva"

---

## `get_swiss_departures`
Get real-time departures with delay information from any station

**Example queries:**
- "Show me departures from Bern station"
- "What trains are leaving from Zürich HB?"
- "Get the next 5 buses from Basel SBB"

**Returns:**
- Live departure times
- Real-time delays (in minutes)
- Platform numbers
- Train/bus types and destinations
- Operators (SBB, BLS, etc.)

---

## `plan_swiss_journey`
Plan journeys with connections and transfers

**Example queries:**
- "Plan a trip from Zürich to Geneva"
- "How do I get from Bern to Lugano?"
- "Show me connections from Basel to Interlaken"

**Returns:**
- Multiple journey options
- Departure/arrival times and platforms
- Number of transfers
- Duration
- Train types (IC, IR, S-Bahn, etc.)
- Real-time delay information
