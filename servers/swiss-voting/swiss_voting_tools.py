# servers/swiss-voting/swiss_voting_tools.py
from fastmcp import tool
import os
import json
import requests
import pdfplumber

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "current_votes.json")

def load_votes():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@tool()
def get_all_federal_votes() -> dict:
    """Returns the full content of the current federal votes dataset."""
    try:
        data = load_votes()
        return data
    except Exception as e:
        return {"error": str(e)}

def get_brochure_pdf_url(vote_id: str, lang: str) -> str:
    # Look up the correct PDF link in your dataset
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for vote in data.get("federal_votes", []):
        if vote.get("vote_id") == vote_id:
            key = "abstimmungsbuechlein_pdf"
            pdf_url = vote.get(key)
            if not pdf_url:
                return None
            # Prefer exact match
            if pdf_url.endswith(f"brochure-{lang}.pdf"):
                return pdf_url
            # Fallback: replace language part in the filename
            for base_lang in ("de", "fr", "it"):
                if f"brochure-{base_lang}.pdf" in pdf_url:
                    return pdf_url.replace(f"brochure-{base_lang}.pdf", f"brochure-{lang}.pdf")
            # As a last resort, just return the original URL
            return pdf_url
    return None

@tool()
def get_brochure_text(vote_id: str, lang: str = "de") -> dict:
    """
    Fetch the text of the official voting brochure for a given vote and language.
    Args:
        vote_id: Swissvotes numeric vote ID as string, e.g., "681"
        lang: Language code ("de", "fr", "it")
    Returns:
        Dict with 'text' field containing the PDF contents (or error)
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
        # Optional: cleanup
        try:
            os.remove(tmp_pdf)
        except Exception:
            pass
        return {"text": "\n".join(text)}
    except Exception as e:
        return {"error": str(e)}
