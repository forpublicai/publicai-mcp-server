"""Wiki-based MCP functions for accessing community-maintained data from wiki.publicai.co"""

from fastmcp import FastMCP
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Any


# MediaWiki API Configuration
WIKI_BASE_URL = "https://wiki.publicai.co"
WIKI_API_URL = f"{WIKI_BASE_URL}/w/api.php"


def register_wiki_functions(mcp: FastMCP):
    """Register wiki-based MCP functions"""

    @mcp.tool()
    def list_tools_by_community(community: str) -> List[Dict[str, Any]]:
        """List all tools available for a specific community.

        Args:
            community: Community name (e.g., "Switzerland", "Singapore", "Lorong AI")

        Returns:
            List of tools with page name, description, community, and whether they have resources
        """
        try:
            fields = "_pageName=Page,description,community,has_resources"
            where = f"community HOLDS \"{community}\""

            params = {
                'action': 'cargoquery',
                'format': 'json',
                'tables': 'Tools',
                'fields': fields,
                'where': where,
                'limit': '500'
            }

            url = f"{WIKI_API_URL}?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            cargo_query = data.get('cargoquery', [])
            results = [item.get('title', {}) for item in cargo_query]

            return results
        except Exception as e:
            return [{"error": f"Failed to list tools for community: {str(e)}"}]

    @mcp.tool()
    def use_tool(tool: str, country: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
        """Use a Public AI tool. For tools with location-specific resources, provide country/region.
        For tools without resources, returns the full page content.

        Args:
            tool: Tool name or canonical ID (e.g., "SuicideHotline" or "Tool:SuicideHotline")
            country: Country name for location-based resources (e.g., "Singapore", "Switzerland")
            region: Optional region for more specific results (e.g., "ZH" for Zurich)

        Returns:
            Dictionary with tool information and either resources (for location-based tools) or page content
        """
        try:
            # Ensure proper page name format
            if not tool.startswith('Tool:'):
                tool = f'Tool:{tool}'

            # First, get the tool metadata to check if it has resources
            tool_fields = "_pageName=Page,description,community,has_resources"
            tool_where = f"_pageName='{tool}'"

            tool_params = {
                'action': 'cargoquery',
                'format': 'json',
                'tables': 'Tools',
                'fields': tool_fields,
                'where': tool_where,
                'limit': '1'
            }

            tool_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(tool_params)}"

            with urllib.request.urlopen(tool_url, timeout=10) as response:
                tool_data = json.loads(response.read().decode())

            cargo_query = tool_data.get('cargoquery', [])
            if not cargo_query:
                return {"error": f"Tool '{tool}' not found"}

            tool_info = cargo_query[0].get('title', {})
            has_resources = tool_info.get('has resources', '0') == '1'

            result = {
                'tool': tool_info.get('Page', ''),
                'description': tool_info.get('description', ''),
                'community': tool_info.get('community', ''),
                'has_resources': has_resources
            }

            if has_resources:
                # Tool has location-specific resources, query tool-specific resource table
                if not country:
                    return {
                        **result,
                        'error': 'This tool requires a country parameter to fetch location-specific resources',
                        'usage': f'use_tool(tool="{tool}", country="Singapore") or use_tool(tool="{tool}", country="Switzerland")'
                    }

                # Extract tool name and construct resource table name
                # e.g., "Tool:SuicideHotline" -> "SuicideHotlineResources"
                tool_name = tool.replace('Tool:', '')
                resource_table = f"{tool_name}Resources"

                try:
                    # First, get the table schema using cargofields API
                    fields_params = {
                        'action': 'cargofields',
                        'format': 'json',
                        'table': resource_table
                    }

                    fields_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(fields_params)}"

                    with urllib.request.urlopen(fields_url, timeout=10) as response:
                        fields_data = json.loads(response.read().decode())

                    # Extract field names from the cargofields response
                    cargo_fields = fields_data.get('cargofields', {})
                    if not cargo_fields:
                        result['resources'] = []
                        result['warning'] = f"Resource table '{resource_table}' not found or has no fields"
                        return result

                    all_fields = ','.join(cargo_fields.keys())

                    # Build WHERE clause for resources
                    where_clauses = [f"tool='{tool}'", f"country='{country}'"]
                    if region:
                        where_clauses.append(f"region='{region}'")

                    resource_where = ' AND '.join(where_clauses)

                    # Now query with all available fields
                    resource_params = {
                        'action': 'cargoquery',
                        'format': 'json',
                        'tables': resource_table,
                        'fields': all_fields,
                        'where': resource_where,
                        'limit': '500'
                    }

                    resource_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(resource_params)}"

                    with urllib.request.urlopen(resource_url, timeout=10) as response:
                        resource_data = json.loads(response.read().decode())

                    resources = [item.get('title', {}) for item in resource_data.get('cargoquery', [])]
                    result['resources'] = resources

                except urllib.error.HTTPError as e:
                    # Resource table doesn't exist or other HTTP error
                    result['resources'] = []
                    result['warning'] = f"Resource table '{resource_table}' not found or query failed"

            else:
                # Tool doesn't have resources, fetch the page content
                parse_params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': tool,
                    'prop': 'text'
                }

                parse_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(parse_params)}"

                with urllib.request.urlopen(parse_url, timeout=10) as response:
                    parse_data = json.loads(response.read().decode())

                parse_result = parse_data.get('parse', {})
                result['content'] = parse_result.get('text', {}).get('*', '')
                result['page_url'] = f"{WIKI_BASE_URL}/wiki/{tool.replace(':', '/')}"

            return result

        except Exception as e:
            return {"error": f"Failed to use tool: {str(e)}"}

    @mcp.tool()
    def add_resource(
        tool: str,
        country: str,
        resource_data_json: str,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a new resource to a Public AI tool's resource page. Safely prepends content to the page.

        Args:
            tool: Tool name or canonical ID (e.g., "SuicideHotline" or "Tool:SuicideHotline")
            country: Country name for the resource (e.g., "Singapore", "Switzerland")
            resource_data_json: JSON string containing the resource fields and values.
                Example for UpcomingEvents: '{"event_name": "Art Fair", "event_type": "Cultural", "start_date": "2026-03-15", "venue": "National Museum", "admission": "Free", "description": "Annual art exhibition", "last_verified": "2025-12-26"}'
                Example for UpcomingBTO: '{"launch_month": "February 2026", "location": "Bukit Merah", "unit_count": "1040", "flat_types": "2R Flexi, 3R, 4R", "classification": "Prime", "last_verified": "2025-12-26"}'
            region: Optional region within the country

        Returns:
            Dictionary with operation status, resource page URL, and the added content
        """
        try:
            # Parse the JSON string into a dictionary
            try:
                resource_data = json.loads(resource_data_json)
            except json.JSONDecodeError as e:
                # Try to auto-fix common JSON errors (missing closing brace)
                try:
                    # Count opening and closing braces
                    open_braces = resource_data_json.count('{')
                    close_braces = resource_data_json.count('}')

                    if open_braces > close_braces:
                        # Add missing closing braces
                        fixed_json = resource_data_json + ('}' * (open_braces - close_braces))
                        resource_data = json.loads(fixed_json)
                    else:
                        raise e  # Re-raise original error
                except:
                    return {
                        "error": f"Invalid JSON in resource_data_json: {str(e)}",
                        "hint": "Ensure resource_data_json is a valid JSON string",
                        "received": resource_data_json
                    }
            # Ensure proper page name format
            if not tool.startswith('Tool:'):
                tool = f'Tool:{tool}'

            # Extract tool name for template and table lookup
            tool_name = tool.replace('Tool:', '')
            resource_table = f"{tool_name}Resources"
            template_name = f"{tool_name}Resource"

            # Get the table schema using cargofields API to validate fields
            fields_params = {
                'action': 'cargofields',
                'format': 'json',
                'table': resource_table
            }

            fields_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(fields_params)}"

            with urllib.request.urlopen(fields_url, timeout=10) as response:
                fields_data = json.loads(response.read().decode())

            cargo_fields = fields_data.get('cargofields', {})
            if not cargo_fields:
                return {
                    "error": f"Resource table '{resource_table}' not found. This tool may not support resources.",
                    "hint": "Use list_tools_by_community() to find tools with resources"
                }

            # Build the template parameters
            template_params = {
                'tool': tool,
                'country': country
            }

            # Add region if provided
            if region:
                template_params['region'] = region

            # Add all provided resource data
            template_params.update(resource_data)

            # Validate that provided fields exist in the schema
            invalid_fields = []
            for field in template_params.keys():
                if field not in cargo_fields:
                    invalid_fields.append(field)

            if invalid_fields:
                return {
                    "error": f"Invalid field(s): {', '.join(invalid_fields)}",
                    "valid_fields": list(cargo_fields.keys()),
                    "field_types": {k: v['type'] for k, v in cargo_fields.items()}
                }

            # Generate the wikitext template
            wikitext_lines = ["{{" + template_name]
            for key, value in template_params.items():
                # Include all fields (even empty ones for clarity)
                wikitext_lines.append(f"|{key}={value}")
            wikitext_lines.append("}}\n")

            wikitext = "\n".join(wikitext_lines)

            # Construct resource page name
            resource_page = f"Resource:{tool_name}/{country}"
            if region:
                resource_page = f"{resource_page}/{region}"

            # Get CSRF token for editing
            token_params = {
                'action': 'query',
                'meta': 'tokens',
                'format': 'json'
            }

            token_url = f"{WIKI_API_URL}?{urllib.parse.urlencode(token_params)}"
            with urllib.request.urlopen(token_url, timeout=10) as response:
                token_data = json.loads(response.read().decode())

            csrf_token = token_data['query']['tokens']['csrftoken']

            # Use MediaWiki edit API with prependtext to safely add content at the top
            edit_params = {
                'action': 'edit',
                'format': 'json',
                'title': resource_page,
                'prependtext': wikitext,
                'summary': f'Added new {tool_name} resource via MCP',
                'token': csrf_token
            }

            # Make the edit request
            post_data = urllib.parse.urlencode(edit_params).encode('utf-8')
            req = urllib.request.Request(WIKI_API_URL, data=post_data)

            with urllib.request.urlopen(req, timeout=10) as response:
                edit_result = json.loads(response.read().decode())

            # Check if edit was successful
            if 'edit' in edit_result and edit_result['edit'].get('result') == 'Success':
                return {
                    'success': True,
                    'resource_page': resource_page,
                    'resource_page_url': f"{WIKI_BASE_URL}/wiki/{resource_page.replace(':', '/')}",
                    'template_name': template_name,
                    'added_content': wikitext.strip(),
                    'revision_id': edit_result['edit'].get('newrevid'),
                    'message': f'Successfully added resource to {resource_page}'
                }
            else:
                # Edit failed, return error details
                return {
                    'success': False,
                    'error': 'Failed to add resource to wiki',
                    'details': edit_result,
                    'generated_wikitext': wikitext.strip()
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            return {"error": f"HTTP error while adding resource: {e.code} {e.reason}", "details": error_body}
        except Exception as e:
            return {"error": f"Failed to add resource: {str(e)}"}
