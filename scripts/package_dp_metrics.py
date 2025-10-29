#package_dp_metrics.py
import json, os, glob, hashlib
from datetime import datetime

METRICS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "community",
    "owui_functions",
    "swiss_voting_metrics",
)
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public_release")
os.makedirs(OUT_DIR, exist_ok=True)

def load_records():
    recs = []
    for p in glob.glob(os.path.join(METRICS_DIR, "batch_*.jsonl")):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    recs.append(json.loads(line))
                except Exception:
                    pass
    return recs

def anonymize(records):
    # Drop identifiers and hash free-text patterns
    for r in records:
        r.pop("pid", None)
        r.pop("pref_use", None)
        if r.get("pattern"):
            r["pattern"] = hashlib.sha256(r["pattern"].encode()).hexdigest()[:12]
    return records

if __name__ == "__main__":
    records = anonymize(load_records())
    out = os.path.join(
        OUT_DIR,
        f"dp_public_metrics_{datetime.now(datetime.UTC).strftime('%Y%m%d')}.json",
    )
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {"records": records, "generated_at": datetime.utcnow().isoformat() + "Z"},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"✅ Wrote anonymized metrics → {out}")
