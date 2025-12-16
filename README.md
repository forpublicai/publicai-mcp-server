# Public AI MCP Server

This is a FastMCP server that provides a collection of tools for various integrations, including Swiss public transport, OpenStreetMap, and UK government services.

## Running the Server

To run the server, execute the following command:

```bash
python main.py
```

This will start the server on `127.0.0.1:8000`.

## Available Tools

### Swiss Public Transport

#### `search_swiss_stations`
Search for Swiss public transport stations.

#### `get_swiss_departures`
Get real-time departures from a Swiss public transport station.

#### `plan_swiss_journey`
Plan a journey on Swiss public transport.

### OpenStreetMap

#### `search_osm_nominatim`
Search OpenStreetMap for a location using Nominatim.

### UK Services (commented out)

#### `lookup_uk_postcode`
Look up detailed information about a UK postcode.

#### `get_uk_bank_holidays`
Get UK bank holidays.

#### `search_nhs_gp_appointments`
Search for available NHS GP appointments near a postcode.

#### `book_nhs_gp_appointment`
Book an NHS GP appointment.

#### `check_dvla_license_status`
Check DVLA driving license status.

#### `renew_dvla_license`
Renew a UK driving license.

#### `check_tv_license`
Check TV License status for an address.

### BBC Services (commented out)

#### `get_bbc_iplayer_recommendations`
Get BBC iPlayer content recommendations.

#### `get_bbc_news`
Get the latest news articles from BBC News.

#### `get_bbc_latest_by_section`
Get the most recent BBC News organized by sections.

#### `get_bbc_languages`
Get a list of all supported languages for BBC News.

#### `search_bbc_news_by_topic`
Search BBC News articles for a specific topic.

#### `get_bbc_multilingual_headlines`
Get top headlines from BBC News in multiple languages.

### Fact Checking (commented out)

#### `fact_check_claim`
Fact-checking service for claims made in the news.

### Accessibility (commented out)

#### `generate_uk_archive_alt_text`
Generate descriptive alt text for UK archive images.
