"""SharePoint write tools (CRUD on existing structures)."""

import base64
import json
import logging
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP, Context

from auth.sharepoint_auth import refresh_token_if_needed
from tools._tool_helpers import _check_auth
from utils.graph_client import GraphClient

logger = logging.getLogger("sharepoint_tools")


def register_write_tools(mcp: FastMCP):
    """Register write tools for SharePoint list and drive mutations."""

    @mcp.tool()
    async def upload_document(
        ctx: Context,
        site_id: str,
        drive_id: str,
        folder_path: str,
        file_name: str,
        file_content: str,
        content_type: str = None,
    ) -> str:
        """Upload a document to a SharePoint document library.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library
            folder_path: Path to the folder (e.g. "General" or "Documents/Folder1")
            file_name: Name of the file to create
            file_content: Base64-encoded file content. Use the content_base64 field
                returned by download_file directly.
            content_type: MIME type of the file

        Returns:
            Created document information
        """
        logger.info(f"Tool called: upload_document with name: {file_name}")
        try:
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            try:
                file_bytes = base64.b64decode(file_content)
            except Exception as e:
                raise ValueError(
                    f"file_content must be valid base64-encoded data: {e}"
                )

            doc_info = await graph_client.upload_document(
                site_id, drive_id, folder_path, file_name, file_bytes, content_type
            )
            logger.info(f"Successfully uploaded document: {file_name}")
            return json.dumps(doc_info, indent=2)
        except Exception as e:
            logger.error(f"Error in upload_document: {str(e)}")
            raise

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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            item_info = await graph_client.create_list_item(site_id, list_id, fields)
            logger.info(f"Successfully created list item in list: {list_id}")
            return json.dumps(item_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_list_item: {str(e)}")
            raise

    @mcp.tool()
    async def update_list_item(
        ctx: Context,
        site_id: str,
        list_id: str,
        item_id: str,
        fields: Dict[str, Any],
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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            item_info = await graph_client.update_list_item(
                site_id, list_id, item_id, fields
            )
            logger.info(f"Successfully updated list item {item_id} in list: {list_id}")
            return json.dumps(item_info, indent=2)
        except Exception as e:
            logger.error(f"Error in update_list_item: {str(e)}")
            raise
