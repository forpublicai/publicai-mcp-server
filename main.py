# main.py
from fastmcp import FastMCP
from typing import Dict, List
import urllib.request
import json
import sys

mcp = FastMCP("Swiss Voting Assistant")

# Remote JSON file from GitHub (auto-updated weekly)
INITIATIVES_URL = (
    "https://raw.githubusercontent.com/pluzgi/publicai-mcp-server/main/"
    "servers/swiss-voting/data/current_initiatives.json"
)


def load_votes() -> dict:
    """Internal helper: Load votes from GitHub-hosted JSON."""
    try:
        with urllib.request.urlopen(INITIATIVES_URL, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Failed to load data: {e}", "federal_initiatives": []}


@mcp.tool()
def get_upcoming_initiatives() -> dict:
    """Return the entire Swiss voting dataset."""
    try:
        data = load_votes()
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_vote_by_id(vote_id: str) -> dict:
    """Return metadata for a specific Swiss federal vote by its ID."""
    try:
        data = load_votes()
        for vote in data.get("federal_initiatives", []):
            if vote.get("vote_id") == vote_id:
                return vote
        return {"error": f"No vote found with ID {vote_id}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_brochure_text(vote_id: str, lang: str = "de") -> dict:
    """
    Fetch and extract the text of the official Swiss voting brochure.
    
    Args:
        vote_id: Swissvotes numeric ID, e.g., "681"
        lang: Language code ("de", "fr", "it")
    
    Returns:
        Dict with brochure PDF URL (extraction not implemented in production)
    """
    try:
        data = load_votes()
        
        # Find the vote
        vote = None
        for v in data.get("federal_initiatives", []):
            if v.get("vote_id") == vote_id:
                vote = v
                break
        
        if not vote:
            return {"error": f"No vote found with ID {vote_id}"}
        
        # Get brochure PDF URL
        pdf_url = vote.get("abstimmungsbuechlein_pdf", "")
        
        if not pdf_url:
            return {"error": "No brochure PDF URL found for this vote"}
        
        # For production: return the PDF URL
        # Note: PDF text extraction requires pdfplumber which is not in requirements
        # Users can download and read the PDF themselves
        return {
            "vote_id": vote_id,
            "language": lang,
            "brochure_pdf_url": pdf_url,
            "note": "PDF extraction not available in production. Download the PDF from the URL provided."
        }
    
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def search_votes_by_keyword(keyword: str) -> list:
    """Search upcoming Swiss votes by keyword in title or policy area."""
    try:
        data = load_votes()
        results = []
        
        for vote in data.get("federal_initiatives", []):
            title = vote.get("offizieller_titel", "").lower()
            policy = vote.get("politikbereich", "").lower()
            
            if keyword.lower() in title or keyword.lower() in policy:
                results.append({
                    "vote_id": vote.get("vote_id"),
                    "title": vote.get("offizieller_titel"),
                    "date": vote.get("abstimmungsdatum"),
                })
        
        return results if results else [{"info": f"No matches found for '{keyword}'"}]
    
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        mcp.run()