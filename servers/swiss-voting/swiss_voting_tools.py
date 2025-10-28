# servers/swiss-voting/swiss_voting_tools.py

from fastmcp import tool
import os
import json

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

# You can add more tools here as needed!
