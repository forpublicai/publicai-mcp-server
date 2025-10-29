# main.py
from fastmcp import FastMCP
from typing import Dict, List
import urllib.request
import json
import sys

mcp = FastMCP("Swiss Voting Assistant")

# Remote JSON file from GitHub
INITIATIVES_URL = (
    "https://raw.githubusercontent.com/pluzgi/publicai-mcp-server/main/servers/swiss-voting/data/current_initiatives.json"
)

@mcp.tool()
def get_all_federal_initiatives() -> Dict:
    """Return all current federal initiatives from the GitHub-hosted JSON."""
    try:
        with urllib.request.urlopen(INITIATIVES_URL, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data
    except Exception as e:
        return {"error": f"Failed to load initiatives: {e}"}

@mcp.tool()
def get_initiative_by_id(initiative_id: str) -> Dict:
    """Return a specific initiative by ID."""
    try:
        with urllib.request.urlopen(INITIATIVES_URL, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        for item in data.get("federal_initiatives", []):
            if item.get("vote_id") == initiative_id:
                return item
        return {"error": "Initiative not found"}
    except Exception as e:
        return {"error": f"Failed to fetch initiative: {e}"}

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
