"""SharePoint read-only tools."""

import json
import logging

from mcp.server.fastmcp import FastMCP, Context

from auth.sharepoint_auth import refresh_token_if_needed
from config.settings import SHAREPOINT_CONFIG
from tools._tool_helpers import _check_auth
from utils.document_processor import DocumentProcessor
from utils.graph_client import GraphClient

logger = logging.getLogger("sharepoint_tools")


def register_read_tools(mcp: FastMCP):
    """Register read-only SharePoint tools with the MCP server."""

    @mcp.tool()
    async def get_site_info(ctx: Context) -> str:
        """Get basic information about the SharePoint site."""
        logger.info("Tool called: get_site_info")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"
            logger.info(f"Getting info for site: {site_name} in domain: {domain}")

            site_info = await graph_client.get_site_info(domain, site_name)
            result = {
                "name": site_info.get("displayName", "Unknown"),
                "description": site_info.get("description", "No description"),
                "created": site_info.get("createdDateTime", "Unknown"),
                "last_modified": site_info.get("lastModifiedDateTime", "Unknown"),
                "web_url": site_info.get("webUrl", SHAREPOINT_CONFIG["site_url"]),
                "id": site_info.get("id", "Unknown"),
            }
            logger.info(f"Successfully retrieved site info for: {result['name']}")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in get_site_info: {str(e)}")
            raise

    @mcp.tool()
    async def list_document_libraries(ctx: Context) -> str:
        """List all document libraries in the SharePoint site."""
        logger.info("Tool called: list_document_libraries")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"
            logger.info(
                f"Listing document libraries for site: {site_name} in domain: {domain}"
            )

            result = await graph_client.list_document_libraries(domain, site_name)
            drives = result.get("value", [])
            formatted_drives = [
                {
                    "name": drive.get("name", "Unknown"),
                    "description": drive.get("description", "No description"),
                    "web_url": drive.get("webUrl", "Unknown"),
                    "drive_type": drive.get("driveType", "Unknown"),
                    "id": drive.get("id", "Unknown"),
                }
                for drive in drives
            ]
            logger.info(
                f"Successfully retrieved {len(formatted_drives)} document libraries"
            )
            return json.dumps(formatted_drives, indent=2)
        except Exception as e:
            logger.error(f"Error in list_document_libraries: {str(e)}")
            raise

    @mcp.tool()
    async def search_sharepoint(ctx: Context, query: str) -> str:
        """Search content in the SharePoint site.

        Args:
            query: Search query string
        """
        logger.info(f"Tool called: search_sharepoint with query: {query}")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"
            logger.info(f"Searching for '{query}' in site: {site_name}")

            site_info = await graph_client.get_site_info(domain, site_name)
            site_id = site_info.get("id")
            if not site_id:
                raise Exception("Error: Could not retrieve site ID")

            search_url = f"sites/{site_id}/search"
            search_data = {
                "requests": [
                    {
                        "entityTypes": ["driveItem", "listItem", "list"],
                        "query": {"queryString": query},
                    }
                ]
            }
            logger.debug(f"Search request: {search_data}")
            search_results = await graph_client.post(search_url, search_data)

            formatted_results = []
            for result in search_results.get("value", [])[0].get("hitsContainers", []):
                for hit in result.get("hits", []):
                    formatted_results.append(
                        {
                            "title": hit.get("resource", {}).get("name", "Unknown"),
                            "url": hit.get("resource", {}).get("webUrl", "Unknown"),
                            "type": hit.get("resource", {}).get(
                                "@odata.type", "Unknown"
                            ),
                            "summary": hit.get("summary", "No summary available"),
                        }
                    )
            logger.info(f"Search returned {len(formatted_results)} results")
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            logger.error(f"Error in search_sharepoint: {str(e)}")
            raise

    @mcp.tool()
    async def get_document_content(
        ctx: Context, site_id: str, drive_id: str, item_id: str, filename: str
    ) -> str:
        """Get and process content from a SharePoint document.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library
            item_id: ID of the document
            filename: Name of the file (for content type detection)
        """
        logger.info(f"Tool called: get_document_content for file: {filename}")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            content = await graph_client.get_document_content(
                site_id, drive_id, item_id
            )
            processed_content = DocumentProcessor.process_document(content, filename)
            logger.info(f"Successfully processed document content for: {filename}")
            return json.dumps(processed_content, indent=2)
        except Exception as e:
            logger.error(f"Error in get_document_content: {str(e)}")
            raise

    @mcp.tool()
    async def list_folder_contents(
        ctx: Context, site_id: str, drive_id: str, folder_path: str = ""
    ) -> str:
        """List files and folders at a given path in a SharePoint document library.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library (drive)
            folder_path: Folder path relative to drive root (e.g. "General" or
                "Docs/2026"). Leave empty to list the root of the drive.
        """
        logger.info(f"Tool called: list_folder_contents path='{folder_path or '/'}'")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            result = await graph_client.list_folder_contents(
                site_id, drive_id, folder_path
            )
            items = result.get("value", [])
            formatted = [
                {
                    "name": item.get("name", "Unknown"),
                    "type": "folder" if "folder" in item else "file",
                    "size": item.get("size", 0),
                    "id": item.get("id", "Unknown"),
                    "web_url": item.get("webUrl", "Unknown"),
                    "last_modified": item.get("lastModifiedDateTime", "Unknown"),
                }
                for item in items
            ]
            logger.info(
                f"Successfully listed {len(formatted)} items at path '{folder_path or '/'}'"
            )
            return json.dumps(formatted, indent=2)
        except Exception as e:
            logger.error(f"Error in list_folder_contents: {str(e)}")
            raise

    @mcp.tool()
    async def get_document_by_path(
        ctx: Context, site_id: str, drive_id: str, file_path: str, filename: str
    ) -> str:
        """Get and process the content of a SharePoint document by its path.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library (drive)
            file_path: File path relative to drive root (e.g. "General/report.docx")
            filename: File name used to detect the document type (e.g. "report.docx")
        """
        logger.info(f"Tool called: get_document_by_path path='{file_path}'")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            content = await graph_client.get_document_content_by_path(
                site_id, drive_id, file_path
            )
            processed_content = DocumentProcessor.process_document(content, filename)
            logger.info(
                f"Successfully processed document content for path: '{file_path}'"
            )
            return json.dumps(processed_content, indent=2)
        except Exception as e:
            logger.error(f"Error in get_document_by_path: {str(e)}")
            raise

    @mcp.tool()
    async def get_item_metadata(
        ctx: Context, site_id: str, drive_id: str, item_path: str
    ) -> str:
        """Get metadata of a file or folder by its path in a SharePoint document library.

        Returns the item's id, name, size, web URL, and timestamps.
        Use the returned id with get_document_content to retrieve file content.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library (drive)
            item_path: Item path relative to drive root (e.g. "General/report.docx"
                or "General")
        """
        logger.info(f"Tool called: get_item_metadata path='{item_path}'")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            item = await graph_client.get_item_metadata_by_path(
                site_id, drive_id, item_path
            )
            result = {
                "id": item.get("id", "Unknown"),
                "name": item.get("name", "Unknown"),
                "size": item.get("size", 0),
                "web_url": item.get("webUrl", "Unknown"),
                "created_by": item.get("createdBy", {})
                .get("user", {})
                .get("displayName", "Unknown"),
                "created_datetime": item.get("createdDateTime", "Unknown"),
                "last_modified_datetime": item.get("lastModifiedDateTime", "Unknown"),
            }
            if "folder" in item:
                result["type"] = "folder"
                result["child_count"] = item["folder"].get("childCount", 0)
            elif "file" in item:
                result["type"] = "file"
                result["mime_type"] = item["file"].get("mimeType", "Unknown")

            logger.info(f"Successfully retrieved metadata for path: '{item_path}'")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in get_item_metadata: {str(e)}")
            raise
