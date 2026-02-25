"""SharePoint site information tools."""

import json
import logging
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP, Context

from auth.sharepoint_auth import refresh_token_if_needed
from utils.graph_client import GraphClient
from utils.document_processor import DocumentProcessor
from utils.content_generator import ContentGenerator
from config.settings import SHAREPOINT_CONFIG

# Set up logging
logger = logging.getLogger("sharepoint_tools")


def _check_auth(sp_ctx) -> None:
    """Check if authentication context is valid, raise exception if not."""
    if not sp_ctx or sp_ctx.access_token == "error" or not sp_ctx.is_token_valid():
        raise Exception(
            "SharePoint authentication failed. Please check your configuration (CLIENT_ID, CLIENT_SECRET, TENANT_ID, SITE_URL)."
        )


def register_site_tools(mcp: FastMCP):
    """Register SharePoint site tools with the MCP server."""

    @mcp.tool()
    async def get_site_info(ctx: Context) -> str:
        """Get basic information about the SharePoint site."""
        logger.info("Tool called: get_site_info")

        try:
            # Get authentication context from context object
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)

            # Refresh token if needed
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Extract site domain and name from site URL
            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"

            logger.info(f"Getting info for site: {site_name} in domain: {domain}")

            # Get site info using Graph client
            site_info = await graph_client.get_site_info(domain, site_name)

            # Format response
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
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def list_document_libraries(ctx: Context) -> str:
        """List all document libraries in the SharePoint site."""
        logger.info("Tool called: list_document_libraries")

        try:
            # Get authentication context from context object
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)

            # Refresh token if needed
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Extract site domain and name from site URL
            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"

            logger.info(
                f"Listing document libraries for site: {site_name} in domain: {domain}"
            )

            # List document libraries using Graph client
            result = await graph_client.list_document_libraries(domain, site_name)

            # Extract drive information from response
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
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def search_sharepoint(ctx: Context, query: str) -> str:
        """Search content in the SharePoint site.

        Args:
            query: Search query string
        """
        logger.info(f"Tool called: search_sharepoint with query: {query}")

        try:
            # Get authentication context from context object
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)

            # Refresh token if needed
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Extract site domain and name from site URL
            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"

            logger.info(f"Searching for '{query}' in site: {site_name}")

            # First get site info to get site ID
            site_info = await graph_client.get_site_info(domain, site_name)
            site_id = site_info.get("id")

            if not site_id:
                logger.error("Failed to get site ID")
                raise Exception("Error: Could not retrieve site ID")

            # Execute search request
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

            # Format search results
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
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def create_sharepoint_site(
        ctx: Context, display_name: str, alias: str, description: str = ""
    ) -> str:
        """Create a new SharePoint site.

        Args:
            display_name: Display name of the site
            alias: Site alias (used in URL)
            description: Site description
        """
        logger.info(
            f"Tool called: create_sharepoint_site with name: {display_name}, alias: {alias}"
        )

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Create the site
            site_info = await graph_client.create_site(display_name, alias, description)

            logger.info(f"Successfully created site: {display_name}")
            return json.dumps(site_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_sharepoint_site: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def create_intelligent_list(
        ctx: Context, site_id: str, purpose: str, display_name: str
    ) -> str:
        """Create a SharePoint list with AI-optimized schema based on its purpose.

        Args:
            site_id: ID of the site
            purpose: Purpose of the list (projects, events, tasks, contacts, documents)
            display_name: Display name for the list
        """
        logger.info(
            f"Tool called: create_intelligent_list with purpose: {purpose}, name: {display_name}"
        )

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Create the intelligent list
            list_info = await graph_client.create_intelligent_list(
                site_id, purpose, display_name
            )

            logger.info(f"Successfully created intelligent list: {display_name}")
            return json.dumps(list_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_intelligent_list: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def create_list_item(
        ctx: Context, site_id: str, list_id: str, fields: Dict[str, Any]
    ) -> str:
        """Create a new item in a SharePoint list.

        Args:
            site_id: ID of the site
            list_id: ID of the list
            fields: Dictionary of field names and values

        Returns:
            Created list item information
        """
        logger.info(f"Tool called: create_list_item in list: {list_id}")

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Create the list item
            item_info = await graph_client.create_list_item(site_id, list_id, fields)

            logger.info(f"Successfully created list item in list: {list_id}")
            return json.dumps(item_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_list_item: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def update_list_item(
        ctx: Context, site_id: str, list_id: str, item_id: str, fields: Dict[str, Any]
    ) -> str:
        """Update an existing item in a SharePoint list.

        Args:
            site_id: ID of the site
            list_id: ID of the list
            item_id: ID of the list item
            fields: Dictionary of field names and values to update

        Returns:
            Updated list item information
        """
        logger.info(
            f"Tool called: update_list_item for item: {item_id} in list: {list_id}"
        )

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Update the list item
            item_info = await graph_client.update_list_item(
                site_id, list_id, item_id, fields
            )

            logger.info(f"Successfully updated list item {item_id} in list: {list_id}")
            return json.dumps(item_info, indent=2)
        except Exception as e:
            logger.error(f"Error in update_list_item: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def create_advanced_document_library(
        ctx: Context, site_id: str, display_name: str, doc_type: str = "general"
    ) -> str:
        """Create a document library with advanced metadata settings.

        Args:
            site_id: ID of the site
            display_name: Display name of the library
            doc_type: Type of documents (general, contracts, marketing, reports, projects)
        """
        logger.info(
            f"Tool called: create_advanced_document_library with type: {doc_type}, name: {display_name}"
        )

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Create the advanced document library
            library_info = await graph_client.create_advanced_document_library(
                site_id, display_name, doc_type
            )

            logger.info(
                f"Successfully created advanced document library: {display_name}"
            )
            return json.dumps(library_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_advanced_document_library: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def upload_document(
        ctx: Context,
        site_id: str,
        drive_id: str,
        folder_path: str,
        file_name: str,
        file_content: bytes,
        content_type: str = None,
    ) -> str:
        """Upload a document to a SharePoint document library.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library
            folder_path: Path to the folder (e.g. "General" or "Documents/Folder1")
            file_name: Name of the file to create
            file_content: Content of the file as bytes
            content_type: MIME type of the file

        Returns:
            Created document information
        """
        logger.info(f"Tool called: upload_document with name: {file_name}")

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Upload the document
            doc_info = await graph_client.upload_document(
                site_id, drive_id, folder_path, file_name, file_content, content_type
            )

            logger.info(f"Successfully uploaded document: {file_name}")
            return json.dumps(doc_info, indent=2)
        except Exception as e:
            logger.error(f"Error in upload_document: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def create_modern_page(
        ctx: Context,
        site_id: str,
        name: str,
        purpose: str = "general",
        audience: str = "general",
    ) -> str:
        """Create a modern SharePoint page with beautiful layout.

        Args:
            site_id: ID of the site
            name: Name of the page (for URL)
            purpose: Purpose of the page (welcome, dashboard, team, project, announcement)
            audience: Target audience (general, executives, team, customers)
        """
        logger.info(
            f"Tool called: create_modern_page with name: {name}, purpose: {purpose}"
        )

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Generate title from purpose and name
            title = ContentGenerator.generate_page_title(purpose, name)

            # Map purpose to template
            template = ContentGenerator.map_purpose_to_template(purpose)

            # Create the modern page
            page_info = await graph_client.create_modern_page(
                site_id, name, title, template
            )
            page_id = page_info.get("id")

            # Generate content based on purpose and audience
            content = ContentGenerator.generate_page_content(purpose, title, audience)

            # Update the page with the generated content
            await graph_client.update_page(
                site_id, page_id, content["title"], content["main_content"]
            )

            # Publish the page
            publish_info = await graph_client.publish_page(site_id, page_id)

            # Combine information for return
            result = {
                "page_info": page_info,
                "publish_info": publish_info,
                "content_summary": {
                    "title": content["title"],
                    "layout": content["layout_suggestion"],
                    "content_sections": len(content["main_content"].split("##")),
                },
            }

            logger.info(f"Successfully created and published modern page: {name}")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error in create_modern_page: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

    @mcp.tool()
    async def create_news_post(
        ctx: Context, site_id: str, title: str, description: str = "", content: str = ""
    ) -> str:
        """Create a news post in a SharePoint site.

        Args:
            site_id: ID of the site
            title: Title of the news post
            description: Brief description of the news post
            content: HTML or Markdown content of the news post

        Returns:
            Created news post information
        """
        logger.info(f"Tool called: create_news_post with title: {title}")

        try:
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Create the news post
            news_info = await graph_client.create_news_post(
                site_id, title, description, content, promote=True
            )

            logger.info(f"Successfully created news post: {title}")
            return json.dumps(news_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_news_post: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

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
            # Get authentication context and refresh if needed
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)

            # Create Graph client
            graph_client = GraphClient(sp_ctx)

            # Get document content
            content = await graph_client.get_document_content(
                site_id, drive_id, item_id
            )

            # Process document content based on file type
            processed_content = DocumentProcessor.process_document(content, filename)

            logger.info(f"Successfully processed document content for: {filename}")
            return json.dumps(processed_content, indent=2)
        except Exception as e:
            logger.error(f"Error in get_document_content: {str(e)}")
            raise  # Re-raise exception so FastMCP can mark it as an error

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
