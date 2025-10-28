# main.py

from fastmcp import FastMCP
import sys
import os

mcp = FastMCP("Swiss Voting Assistant")

# Import & register Swiss Voting tools using absolute path
script_dir = os.path.dirname(os.path.abspath(__file__))
swiss_voting_path = os.path.join(script_dir, "servers", "swiss-voting")
sys.path.append(swiss_voting_path)

from swiss_voting_tools import register_tools
register_tools(mcp)

if __name__ == "__main__":
    # Check if running with Inspector/Claude Desktop (STDIO)
    # or for HTTP server
    if "--http" in sys.argv:
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        mcp.run()  # STDIO mode (default)