from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by name.
    
    Args:
        name: The name of the person to greet
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
     mcp.run(transport="http", host="127.0.0.1", port=8000)