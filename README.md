Swiss Voting Assistant

A conversational AI tool providing accessible information about Swiss popular initiatives (Volksabstimmungen).

🎯 Overview
The Swiss Voting Assistant makes complex voting information accessible through natural conversation. It provides instant access to details about Swiss popular initiatives, balanced arguments from both sides, and official sources with full attribution.
Problem: Swiss citizens receive lengthy voting brochures (80+ pages) that are time-consuming and difficult to navigate.
Solution: A conversational interface that delivers the same information on-demand, structured for easy understanding.

✨ Features

✅ Discover upcoming popular initiatives - Get dates and overview of all scheduled votes
✅ Detailed initiative information - Access comprehensive metadata, party positions, parliamentary votes
✅ Balanced arguments - Read pro/contra arguments from official sources
✅ Official brochures - Extract content in German, French, or Italian
✅ Search by topic - Find initiatives by keyword (e.g., "Klimapolitik", "Armee")


🎬 Demo
Example: Initiative 681 (November 30, 2025)
User: "Wann findet die nächste Volksinitiative statt?"
Assistant: Die nächsten Volksabstimmungen finden am 30. November 2025 statt...

User: "681"
Assistant: Initiative für eine Zukunft - Erbschaftssteuer zur Klimafinanzierung...

User: "Gib mir die Pro-Argumente"
Assistant: [Structured arguments from JUSO initiative committee]
```

**Information provided:**
- 📅 Voting date and deadline
- 📝 Full title and description  
- 🏛️ Initiators and signatures collected
- 📊 Parliamentary recommendations (National- and Ständerat)
- 🎯 Party positions (Ja/Nein)
- ⚖️ Pro arguments (Initiative Committee)
- ⚖️ Contra arguments (Federal Council/Parliament)
- 💰 Cost estimates and impact analysis
- 🔗 Links to official documents

---

## 🏗️ Architecture
```
User Query (Natural Language)
         ↓
   AI Processing Layer
         ↓
   Tool Selection (4 functions)
         ↓
Swiss Federal Government APIs
    (swissvotes.ch, admin.ch)
```

### Four Core Functions

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `get_upcoming_initiatives` | Get all scheduled votes | None | List of upcoming initiatives |
| `get_vote_by_id` | Get specific initiative details | vote_id (e.g., "681") | Detailed metadata |
| `get_brochure_text` | Extract official brochure | vote_id, lang (de/fr/it) | Full brochure text |
| `search_votes_by_keyword` | Search by topic | keyword | Matching initiatives |

---

## 💻 Usage

### In Public AI Chat Interface
```
"Wann findet die nächste Volksinitiative statt?"
"Zeige mir Initiative 681"
"Was sind die Pro-Argumente?"
"Suche alle Abstimmungen zum Thema Klima"
API Example (Future)
pythonfrom swiss_voting_assistant import SwissVotingAssistant

assistant = SwissVotingAssistant()

# Get upcoming votes
upcoming = assistant.query("Wann findet die nächste Volksinitiative statt?")

# Get specific initiative
vote_681 = assistant.get_vote_details("681")

# Get arguments
pro_args = assistant.get_arguments("681", side="pro")

📊 Data Sources
All data from official Swiss government sources:

swissvotes.ch - Historical voting data and comprehensive metadata
admin.ch - Current voting information and official positions
Bundesblatt - Federal gazette with legal texts

Data includes:

Initiative metadata (title, ID, date, initiators)
Signature collection details
Parliamentary deliberations
Party recommendations
Official voting brochures (PDF)
Campaign finance information


📈 Current Status
✅ Implemented

 Four core functions for voting information
 Natural language query processing
 Official data source integration
 Multilingual brochure extraction (DE/FR/IT)
 Balanced pro/contra argument extraction
 Real-time data for November 30, 2025 votes

❌ Not Yet Implemented
Data Flywheel Components:

 User feedback collection
 Opt-in consent system
 Differential privacy infrastructure (PySyft)
 Model fine-tuning pipeline
 Data packaging for Swiss AI Initiative

Production Requirements:

 Deployment to chat.publicai.co
 MCP (Model Context Protocol) integration
 Rate limiting and caching
 Monitoring and analytics
 CI/CD pipeline