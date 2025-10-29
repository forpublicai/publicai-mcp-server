import requests
import time
import json
import os
from bs4 import BeautifulSoup
from typing import Dict, List
from datetime import datetime
    
BASE = "https://swissvotes.ch"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "servers", "swiss-voting", "data")
os.makedirs(OUT_DIR, exist_ok=True)

def parse_parteiparolen(td):
    dls = td.find_all("dl", class_="recommendation")
    parts = []

    for dl in dls:
        last_type = None
        for elem in dl.find_all(["dt", "dd"]):
            if elem.name == "dt":
                last_type = elem.get_text(" ", strip=True)
            elif elem.name == "dd":
                party = elem.get_text(" ", strip=True)
                if last_type:
                    parts.append(f"{last_type}: {party}")
    return parts

    # Fallback: Plain text case
    # e.g. "Ja: EVP, GLP\nNein: FDP, SVP, ..."
    parts = []
    lines = td.get_text("\n", strip=True).split("\n")
    for line in lines:
        if ":" in line:
            label, parties = line.split(":", 1)
            for party in [p.strip() for p in parties.split(",") if p.strip()]:
                parts.append(f"{label.strip()}: {party}")
    return parts

out_file = os.path.join(OUT_DIR, "current_initiatives.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("✅ Wrote current_initiatives.json")

def discover_upcoming_volksinitiative_votes() -> List[str]:
    url = f"{BASE}/votes?page=0"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    ids = []
    today = datetime.today().date()

    for tr in soup.select("tr"):
        cols = tr.find_all("td")
        if not cols or len(cols) < 7:
            continue

        date_str = cols[1].get_text(strip=True)
        rechtsform = cols[2].get_text(strip=True)
        abstimmungsergebnis = cols[4].get_text(strip=True)
        ja_anteil = cols[5].get_text(strip=True)
        stimmbeteiligung = cols[6].get_text(strip=True)

        try:
            vote_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except Exception:
            vote_date = None

        if (
            rechtsform == "Volksinitiative"
            and abstimmungsergebnis == ""
            and ja_anteil == "%"
            and stimmbeteiligung == "%"
            and vote_date is not None
            and vote_date >= today
        ):
            details_link = cols[-1].find("a", href=True)
            if details_link and "/vote/" in details_link["href"]:
                vid = details_link["href"].split("/vote/")[1]
                if vid not in ids:
                    ids.append(vid)
    return ids

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
    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            # Only data rows: th+td or td+td
            cells = row.find_all(["th", "td"], recursive=False)
            if len(cells) != 2:
                continue
            # Skip header rows with colspan or section headers
            if cells[0].name == "th" and ("colspan" in cells[0].attrs or not cells[1].text.strip()):
                continue
            label = cells[0].get_text(" ", strip=True)
            td = cells[1]
            value = td.get_text(" ", strip=True)
            link = td.find("a", href=True)
            # Map official fields
            if label == "Offizieller Titel":
                result["offizieller_titel"] = value
            elif label == "Schlagwort":
                result["schlagwort"] = value
            elif label == "Abstimmungsdatum":
                result["abstimmungsdatum"] = value
            elif label == "Abstimmungsnummer":
                result["abstimmungsnummer"] = value
            elif label == "Rechtsform":
                result["rechtsform"] = value
            elif label == "Politikbereich":
                spans = td.find_all("span")
                if spans:
                    result["politikbereich"] = "; ".join([s.get_text(" ", strip=True) for s in spans])
                else:
                    result["politikbereich"] = value
            elif label == "Beschreibung Année Politique Suisse":
                result["beschreibung_annee_politique_suisse_url"] = link["href"] if link else value
            elif label == "Abstimmungstext":
                result["abstimmungstext_pdf"] = link["href"] if link else value
            elif label == "Offizielle Chronologie":
                result["offizielle_chronologie_url"] = link["href"] if link else value
            elif label == "Urheber:innen":
                result["urheberinnen"] = value
            elif label == "Vorprüfung":
                result["vorpruefung_pdf"] = link["href"] if link else value
            elif label == "Unterschriften":
                result["unterschriften"] = value
            elif label == "Sammeldauer":
                result["sammeldauer"] = value
            elif label == "Zustandekommen":
                result["zustandekommen_pdf"] = link["href"] if link else value
            elif label == "Botschaft des Bundesrats":
                result["botschaft_des_bundesrats_pdf"] = link["href"] if link else value
            elif label == "Geschäftsnummer":
                result["geschaeftsnummer"] = value
            elif label == "Parlamentsberatung":
                result["parlamentsberatung_url"] = link["href"] if link else value
            elif label == "Behandlungsdauer Parlament":
                result["behandlungsdauer_parlament"] = value
            elif label == "Position des Parlaments":
                result["position_parlament"] = value
            elif label == "Position des Nationalrats":
                result["position_nationalrat"] = value
            elif label == "Position des Ständerats":
                result["position_staenderat"] = value
            elif label == "Offizielles Abstimmungsbüchlein":
                result["abstimmungsbuechlein_pdf"] = link["href"] if link else value
            elif label == "Position des Bundesrats":
                result["position_bundesrat"] = value
            elif label == "Online-Informationen der Behörden":
                result["online_informationen_behoerden_url"] = link["href"] if link else value
            elif label == "Parteiparolen":
                result["parteiparolen"] = parse_parteiparolen(td)
            elif label == "Wählendenanteil des Ja-Lagers":
                link_ja = td.find("a", href=True)
                if link_ja:
                    result["waehlendenanteil_ja_lager"] = link_ja["href"]
                else:
                    result["waehlendenanteil_ja_lager"] = value
            elif label == "Weitere Parolen":
                result["weitere_parolen"] = parse_parteiparolen(td)
            elif label == "Abweichende Sektionen":
                result["abweichende_sektionen"] = parse_parteiparolen(td)
            elif label == "Kampagnenfinanzierung":
                link_fin = td.find("a", href=True)
                if link_fin:
                    result["kampagnenfinanzierung_url"] = link_fin["href"]
                else:
                    result["kampagnenfinanzierung_url"] = value
    title_de = soup.find("h1")
    if title_de:
        result["title_de"] = title_de.get_text(strip=True)
    return result

def build_dataset() -> Dict:
    vids = discover_upcoming_volksinitiative_votes()
    ds = {
        "metadata": {
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data_version": "1.0",
            "sources": [BASE, "https://www.admin.ch"]
        },
        "federal_votes": [],
        "usage_metrics": {}
    }
    for vid in vids:
        base = parse_vote_page(vid)
        ds["federal_votes"].append(base)
    return ds

if __name__ == "__main__":
    data = build_dataset()
    out = os.path.join(OUT_DIR, "current_initiatives.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
