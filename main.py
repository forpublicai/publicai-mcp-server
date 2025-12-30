from fastmcp import FastMCP

# Import function registration modules
from functions.wiki import register_wiki_functions
from functions.swiss_transport import register_swiss_transport_functions
from functions.singapore import register_singapore_functions

# Initialize MCP server
mcp = FastMCP("Public AI MCP Server")

# Register all MCP functions
register_wiki_functions(mcp)
register_swiss_transport_functions(mcp)
register_singapore_functions(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
