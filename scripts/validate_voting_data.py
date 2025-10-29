#validate_voting_data.py

import json
import os
import requests

REQUIRED_FIELDS = [
    "vote_id",
    "offizieller_titel",
    "abstimmungsdatum",
    "rechtsform",
    "politikbereich",
    "abstimmungstext_pdf",
    "botschaft_des_bundesrats_pdf",
    "abstimmungsbuechlein_pdf",
    "parteiparolen"
]

PDF_FIELDS = [
    "abstimmungstext_pdf",
    "botschaft_des_bundesrats_pdf",
    "abstimmungsbuechlein_pdf"
]

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "servers", "swiss-voting", "data", "current_initiatives.json")

def validate_vote_fields(vote):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in vote or not vote[field]:
            errors.append(f"Missing or empty: {field}")
    return errors

def validate_pdf_links(vote):
    errors = []
    for field in PDF_FIELDS:
        url = vote.get(field)
        if not url or not url.endswith(".pdf"):
            errors.append(f"{field} is not a valid PDF link: {url}")
            continue
        try:
            r = requests.head(url, allow_redirects=True, timeout=10)
            if r.status_code == 405 or r.status_code == 403:
                # Fallback: try GET (some servers disallow HEAD)
                r = requests.get(url, stream=True, allow_redirects=True, timeout=10)
            if r.status_code != 200:
                errors.append(f"{field} request failed: {url} (status {r.status_code})")
            elif "pdf" not in r.headers.get("content-type", "").lower():
                errors.append(f"{field} not returning PDF content: {url} (type {r.headers.get('content-type')})")
        except Exception as e:
            errors.append(f"{field} failed request: {e}")
    return errors


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    print(f"🔍 Validating {len(data['federal_votes'])} votes...")
    total_errors = 0

    for vote in data["federal_votes"]:
        field_errors = validate_vote_fields(vote)
        link_errors = validate_pdf_links(vote)
        all_errors = field_errors + link_errors

        if all_errors:
            total_errors += len(all_errors)
            print(f"\n❌ Errors in vote {vote.get('vote_id')} - {vote.get('offizieller_titel')[:50]}...")
            for err in all_errors:
                print(f"  - {err}")

    if total_errors == 0:
        print("\n✅ All votes passed validation.")
    else:
        print(f"\n🚨 Total validation issues: {total_errors}")

if __name__ == "__main__":
    main()
