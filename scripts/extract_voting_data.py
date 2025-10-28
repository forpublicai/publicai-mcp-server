import requests, pdfplumber, time, json, os
from bs4 import BeautifulSoup
from typing import Dict, List

BASE = "https://swissvotes.ch"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "servers", "swiss-voting", "data")
os.makedirs(OUT_DIR, exist_ok=True)

def discover_upcoming_volksinitiative_votes() -> List[str]:
    url = f"{BASE}/votes?page=0"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    ids = []
    # Each row in the table
    for tr in soup.select("tr"):
        cols = tr.find_all("td")
        if not cols or len(cols) < 5:
            continue
        rechtsform = cols[2].get_text(strip=True)
        if rechtsform != "Volksinitiative":
            continue
        # Find link in "Details" column
        details_link = cols[-1].find("a", href=True)
        if details_link and "/vote/" in details_link["href"]:
            vid = details_link["href"].split("/vote/")[1]
            if vid not in ids:
                ids.append(vid)
    return ids  # remove [:5] to get all, or [:N] to limit


def extract_pdf_text(vote_id: str, lang: str) -> str:
    pdf_url = f"{BASE}/vote/{vote_id}/brochure-{lang}.pdf"
    r = requests.get(pdf_url, timeout=30)
    if r.status_code != 200:
        return ""
    with open("/tmp/_sv.pdf", "wb") as f:
        f.write(r.content)
    text = []
    with pdfplumber.open("/tmp/_sv.pdf") as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)

def parse_vote_page(vote_id: str) -> Dict:
    url = f"{BASE}/vote/{vote_id}"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    result = {
        "vote_id": vote_id.split(".")[0],
        "official_number": vote_id,
        "details_url": url
    }

    # Extract main details table
    table = soup.find("table")
    if table:
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) != 2:
                continue
            label = cols[0].get_text(strip=True)
            value = cols[1].get_text(strip=True)
            link = cols[1].find("a", href=True)
            # Map labels to your field names
            if "Abstimmungsdatum" in label:
                result["abstimmungsdatum"] = value
            elif "Abstimmungsnummer" in label:
                result["abstimmungsnummer"] = value
            elif "Politikbereich" in label:
                result["politikbereich"] = value
            elif "Beschreibung Année Politique Suisse" in label and link:
                result["beschreibung_annee_politique_suisse_url"] = link["href"]
            elif "Abstimmungstext" in label and link:
                result["abstimmungstext_pdf"] = link["href"]
            elif "Offizielle Chronologie" in label and link:
                result["offizielle_chronologie_url"] = link["href"]
            elif "Urheber" in label:
                result["urheber"] = value
            elif "Vorprüfung" in label and link:
                result["vorpruefung_pdf"] = link["href"]
            elif "Unterschriften" in label:
                result["unterschriften"] = value
            elif "Offizielles Abstimmungsbüchlein" in label and link:
                result["abstimmungsbuechlein_pdf"] = link["href"]
            elif "Position des Bundesrats" in label:
                result["federal_council_position"] = value

    # Extract title as before
    title_de = soup.find("h1")
    if title_de:
        result["title_de"] = title_de.get_text(strip=True)
    return result


def build_dataset() -> Dict:
    vids = discover_upcoming_volksinitiative_votes()
    ds = {
        "metadata": {
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "next_voting_date": "2025-11-30",
            "data_version": "1.0",
            "sources": [BASE, "https://www.admin.ch"]
        },
        "federal_votes": [],
        "usage_metrics": {}
    }
    for vid in vids:
        base = parse_vote_page(vid)
        for lang in ("de", "fr", "it"):
            txt = extract_pdf_text(vid, lang)
            if not txt:
                continue
            base.setdefault(f"summary_{lang}", txt)
            base.setdefault(f"title_{lang}", base.get("title_de", ""))
        base.setdefault("type", "Volksinitiative")
        base.setdefault("federal_council_position", "neutral")
        ds["federal_votes"].append(base)
    return ds

if __name__ == "__main__":
    data = build_dataset()
    out = os.path.join(OUT_DIR, "current_votes.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out}")
