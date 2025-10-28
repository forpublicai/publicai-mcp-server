import json, sys, os

DATA = os.path.join(
    os.path.dirname(__file__),
    "..",
    "community",
    "owui_functions",
    "swiss_voting_data",
    "current_votes.json",
)

def main():
    try:
        with open(DATA, "r", encoding="utf-8") as f:
            j = json.load(f)
        assert "metadata" in j, "missing metadata"
        assert "federal_votes" in j, "missing federal_votes"
        for v in j["federal_votes"]:
            assert "vote_id" in v and "title_de" in v, f"incomplete vote record {v}"
        print("✅ Validation OK")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
