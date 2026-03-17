"""SharePoint site information resources."""

import json
from mcp.server.fastmcp import FastMCP, Context

from auth.sharepoint_auth import refresh_token_if_needed
from config.settings import SHAREPOINT_CONFIG
from utils.graph_client import GraphClient


def register_site_resources(mcp: FastMCP):
    """Register SharePoint site resources with the MCP server."""

    async def site_info_handler(ctx: Context) -> str:
        """Get basic information about the SharePoint site."""
        await refresh_token_if_needed(ctx.request_context.lifespan_context)
        sp_ctx = ctx.request_context.lifespan_context

        try:
            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"

            if site_name == "root" or not site_name:
                endpoint = f"sites/{domain}:"
            else:
                endpoint = f"sites/{domain}:/sites/{site_name}"

            client = GraphClient(sp_ctx)
            site_info = await client.get(endpoint)

            result = {
                "name": site_info.get("displayName", "Unknown"),
                "description": site_info.get("description", "No description"),
                "created": site_info.get("createdDateTime", "Unknown"),
                "last_modified": site_info.get("lastModifiedDateTime", "Unknown"),
                "web_url": site_info.get("webUrl", SHAREPOINT_CONFIG["site_url"]),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error accessing SharePoint: {str(e)}"

    mcp.resource("sharepoint://site-info")(site_info_handler)
