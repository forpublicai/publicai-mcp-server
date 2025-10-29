# Swiss Voting Assistant

A FastMCP server providing accessible information about Swiss popular initiatives (Volksabstimmungen).

## 🎯 Overview

The Swiss Voting Assistant makes complex voting information accessible through MCP tools. It provides instant access to details about Swiss popular initiatives, arguments from both sides, and official sources with full attribution.

**Problem:** Swiss citizens receive lengthy voting brochures that are time-consuming and difficult to navigate.

**Solution:** MCP tools that deliver the same information on-demand, structured for easy understanding with pre-extracted brochure texts.

---

## ✨ Features

✅ Discover upcoming popular initiatives - Get dates and overview of all scheduled votes  
✅ Detailed initiative information - Access comprehensive metadata, party positions, parliamentary votes  
✅ **Full brochure text extraction** - Pre-extracted text in German, French, and Italian (when available)  
✅ Search by topic - Find initiatives by keyword (e.g., "Klimapolitik")

---

## 🏗️ Architecture
```
User Query (via MCP Client)
         ↓
   FastMCP Server (main.py)
         ↓
   Tool Selection (4 MCP tools)
         ↓
   GitHub-hosted JSON
    (Auto-updated weekly with pre-extracted PDF texts)
         ↓
   Original Data Source
    (swissvotes.ch)
```

### Four Core MCP Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `get_upcoming_initiatives` | Get all scheduled votes | None | Complete dataset with metadata |
| `get_vote_by_id` | Get specific initiative | vote_id (e.g., "681") | Detailed initiative metadata |
| `get_brochure_text` | Get extracted brochure text | vote_id, lang (de/fr/(it, if provided)) | Pre-extracted full text + PDF URL |
| `search_votes_by_keyword` | Search by topic | keyword | List of matching initiatives |

---

## 💻 Usage

### Via MCP Protocol

The server exposes 4 tools through the Model Context Protocol (MCP). Any MCP-compatible client can use these tools.

**Example queries:**
- "Wann findet die nächste Volksinitiative statt?"
- "Zeige mir Initiative 681"
- "Was steht im Abstimmungsbüchlein zu Initiative 681?"
- "Suche alle Abstimmungen zum Thema Klima"

### Local Testing
```bash
# Run with stdio transport (default)
python main.py

# Run with HTTP transport for testing
python main.py --http
```

---

## 📊 Data Sources

**Primary Source:** swissvotes.ch  
**Update Frequency:** Weekly (via GitHub Actions)  
**Data Structure:** `federal_initiatives` array in JSON with embedded brochure texts

All data from official Swiss government sources:
- **swissvotes.ch** - Historical voting data and comprehensive metadata
- **admin.ch** - Current voting information and official positions
- **Bundesblatt** - Federal gazette with legal texts

**Data includes:**
- Initiative metadata (title, ID, date, initiators)
- Signature collection details
- Parliamentary deliberations
- Party recommendations (Parteiparolen)
- **Pre-extracted brochure texts** (DE/FR/IT)
- Official voting brochures (PDF links)
- Campaign finance information

---

## 📁 Project Structure
```
servers/swiss-voting/
├── main.py                          # FastMCP server (production)
├── requirements.txt                 # Production deps (fastmcp only)
├── requirements-scripts.txt         # Scraping deps (GitHub Actions)
│
├── data/
│   └── current_initiatives.json     # Auto-updated data with pre-extracted texts
│
├── scripts/
│   ├── extract_voting_data.py       # Data scraper + PDF text extraction
│   ├── validate_voting_data.py      # Data validation
│   └── update_voting_data.sh        # Update script
│
├── swiss_voting_tools.py            # Scraping logic (for GitHub Actions)
│
└── .github/workflows/
    └── update_initiatives.yml       # Weekly auto-update
```

---

## 📈 Current Status

### ✅ Implemented

- ✅ Four MCP tools for voting information
- ✅ FastMCP server implementation
- ✅ Official data source integration (swissvotes.ch)
- ✅ **Multilingual brochure text extraction** (DE/FR/IT) - Pre-processed by GitHub Actions
- ✅ GitHub Actions auto-update (weekly)
- ✅ Data validation pipeline
- ✅ Production-ready for PublicAI deployment

### 🚀 Production Deployment

**Requirements for PublicAI:**
- `main.py` (FastMCP server - no PDF processing needed)
- `requirements.txt` (only `fastmcp>=0.1.0`)
- `data/current_initiatives.json` (includes pre-extracted brochure texts)

**Data Update Flow:**
```
GitHub Actions (weekly)
    ↓
Scrape swissvotes.ch
    ↓
Download PDFs and extract text (DE/FR/IT)
    ↓
Save to data/current_initiatives.json
    ↓
Commit to GitHub
    ↓
main.py fetches from GitHub raw URL
    ↓
LLM can immediately access full brochure texts
```

**Key Advantage:** All PDF text extraction happens during GitHub Actions. Production server (`main.py`) simply reads pre-extracted text from JSON - no PDF processing overhead!

---

## 🔧 Development

### Setup
```bash
# Install production dependencies
pip install -r requirements.txt

# Install scraping dependencies (for data updates)
pip install -r requirements-scripts.txt
```

### Update Data Manually
```bash
cd scripts
./update_voting_data.sh
```

This will:
1. Scrape swissvotes.ch for new initiatives
2. Download all brochure PDFs
3. Extract text in DE, FR, and IT
4. Save everything to `current_initiatives.json`

### Validate Data
```bash
python scripts/validate_voting_data.py
```

---

## 📝 Data Schema

Each initiative in `federal_initiatives` contains:

| Field | Description |
|-------|-------------|
| `vote_id` | Short ID (e.g., "681") |
| `official_number` | Full number (e.g., "681.0") |
| `offizieller_titel` | Official title |
| `schlagwort` | Keyword/catchphrase |
| `abstimmungsdatum` | Voting date (DD.MM.YYYY) |
| `rechtsform` | Legal form ("Volksinitiative") |
| `politikbereich` | Policy area |
| `urheberinnen` | Initiative authors |
| `unterschriften` | Number of signatures |
| `position_bundesrat` | Federal Council position |
| `position_parlament` | Parliament position |
| `parteiparolen` | Party recommendations |
| `abstimmungsbuechlein_pdf` | Official brochure PDF URL |
| **`brochure_texts`** | **Pre-extracted text {"de": "...", "fr": "...", "it": "..."}** |
| `details_url` | Full swissvotes.ch page |

---

## 🔗 Links

- **Data Source:** https://swissvotes.ch
- **Federal Admin:** https://www.admin.ch
- **FastMCP Docs:** https://github.com/jlowin/fastmcp
- **PublicAI:** https://publicai.io

---

## 📄 License

Copyright (c) 2025 [Sabine Wildemann]

Open source under MIT License. Free to use for everyone.
Part of the PublicAI MCP Server collection.

---

**Built for Swiss civic engagement** 🇨🇭