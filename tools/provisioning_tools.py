"""SharePoint provisioning tools (create new structures)."""

import json
import logging

from mcp.server.fastmcp import FastMCP, Context

from auth.sharepoint_auth import refresh_token_if_needed
from tools._tool_helpers import _check_auth
from utils.content_generator import ContentGenerator
from utils.graph_client import GraphClient

logger = logging.getLogger("sharepoint_tools")


def register_provisioning_tools(mcp: FastMCP):
    """Register provisioning tools for SharePoint structure creation."""

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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            site_info = await graph_client.create_site(display_name, alias, description)
            logger.info(f"Successfully created site: {display_name}")
            return json.dumps(site_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_sharepoint_site: {str(e)}")
            raise

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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            list_info = await graph_client.create_intelligent_list(
                site_id, purpose, display_name
            )
            logger.info(f"Successfully created intelligent list: {display_name}")
            return json.dumps(list_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_intelligent_list: {str(e)}")
            raise

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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            library_info = await graph_client.create_advanced_document_library(
                site_id, display_name, doc_type
            )
            logger.info(
                f"Successfully created advanced document library: {display_name}"
            )
            return json.dumps(library_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_advanced_document_library: {str(e)}")
            raise

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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            title = ContentGenerator.generate_page_title(purpose, name)
            template = ContentGenerator.map_purpose_to_template(purpose)

            page_info = await graph_client.create_modern_page(
                site_id, name, title, template
            )
            page_id = page_info.get("id")

            content = ContentGenerator.generate_page_content(purpose, title, audience)
            await graph_client.update_page(
                site_id, page_id, content["title"], content["main_content"]
            )
            publish_info = await graph_client.publish_page(site_id, page_id)

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
            raise

    @mcp.tool()
    async def create_news_post(
        ctx: Context,
        site_id: str,
        title: str,
        description: str = "",
        content: str = "",
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
            sp_ctx = ctx.request_context.lifespan_context
            _check_auth(sp_ctx)
            await refresh_token_if_needed(sp_ctx)
            graph_client = GraphClient(sp_ctx)

            news_info = await graph_client.create_news_post(
                site_id, title, description, content, promote=True
            )
            logger.info(f"Successfully created news post: {title}")
            return json.dumps(news_info, indent=2)
        except Exception as e:
            logger.error(f"Error in create_news_post: {str(e)}")
            raise
