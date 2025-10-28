# servers/swiss-voting/swiss_voting_tools.py

import os
import json
import requests
import pdfplumber

# Path to your dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "current_votes.json")


# -----------------------
# Helper Functions
# -----------------------

def load_votes():
    """Load the Swiss votes dataset."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_brochure_pdf_url(vote_id: str, lang: str) -> str:
    """Find the correct official brochure PDF URL for the given vote and language."""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for vote in data.get("federal_votes", []):
        if vote.get("vote_id") == vote_id:
            key = "abstimmungsbuechlein_pdf"
            pdf_url = vote.get(key)
            if not pdf_url:
                return None
            # Prefer an exact language match
            if pdf_url.endswith(f"brochure-{lang}.pdf"):
                return pdf_url
            # Fallback: replace base language code
            for base_lang in ("de", "fr", "it"):
                if f"brochure-{base_lang}.pdf" in pdf_url:
                    return pdf_url.replace(f"brochure-{base_lang}.pdf", f"brochure-{lang}.pdf")
            return pdf_url
    return None


# -----------------------
# Register Tools Function
# -----------------------

def register_tools(mcp):
    """Register all Swiss voting tools with the provided MCP instance."""
    
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
            for vote in data.get("federal_votes", []):
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
            Dict with extracted brochure text or error info.
        """
        pdf_url = get_brochure_pdf_url(vote_id, lang)
        if not pdf_url:
            return {"error": "No brochure PDF URL found for this vote/language"}
        try:
            r = requests.get(pdf_url, timeout=30)
            if r.status_code != 200:
                return {"error": f"Failed to download PDF: status {r.status_code}"}
            tmp_pdf = "/tmp/_sv_brochure.pdf"
            with open(tmp_pdf, "wb") as f:
                f.write(r.content)
            text = []
            with pdfplumber.open(tmp_pdf) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            os.remove(tmp_pdf)
            return {"text": "\n".join(text)}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def search_votes_by_keyword(keyword: str) -> list:
        """Search upcoming Swiss votes by keyword in title or policy area."""
        try:
            data = load_votes()
            results = []
            for vote in data.get("federal_votes", []):
                title = vote.get("offizieller_titel", "").lower()
                policy = vote.get("politikbereich", "").lower()
                if keyword.lower() in title or keyword.lower() in policy:
                    results.append({
                        "vote_id": vote.get("vote_id"),
                        "title": vote.get("offizieller_titel"),
                        "date": vote.get("abstimmungsdatum"),
                    })
            return results or [{"info": f"No matches found for '{keyword}'"}]
        except Exception as e:
            return {"error": str(e)}