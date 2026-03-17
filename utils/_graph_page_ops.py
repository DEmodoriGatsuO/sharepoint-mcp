"""Page and news post operations mixin for GraphClient."""

import logging
from typing import Dict, Any

logger = logging.getLogger("graph_client")


class _GraphPageOpsMixin:
    """Page creation and management operations for the Microsoft Graph API."""

    async def create_page(
        self, site_id: str, name: str, title: str = ""
    ) -> Dict[str, Any]:
        """Create a new page in a SharePoint site."""
        endpoint = f"sites/{site_id}/pages"
        data = {"name": name, "title": title or name}
        logger.info(f"Creating new page with name: {name} in site: {site_id}")
        return await self.post(endpoint, data)

    async def create_modern_page(
        self, site_id: str, name: str, title: str, layout: str = "Article"
    ) -> Dict[str, Any]:
        """Create a modern page with professional layout in SharePoint."""
        endpoint = f"sites/{site_id}/pages"
        data = {"name": name, "title": title, "layoutType": layout}
        logger.info(f"Creating modern page with name: {name}, layout: {layout}")
        return await self.post(endpoint, data)

    async def create_news_post(
        self,
        site_id: str,
        title: str,
        description: str = "",
        content: str = "",
        promote: bool = True,
    ) -> Dict[str, Any]:
        """Create a news post in a SharePoint site."""
        name = f"news-{title.lower().replace(' ', '-')}"
        page_info = await self.create_modern_page(site_id, name, title, "Article")
        page_id = page_info.get("id")

        await self.update_page(site_id, page_id, title, content)
        published_page = await self.publish_page(site_id, page_id)

        endpoint = f"sites/{site_id}/pages/{page_id}/setAsNewsPost"
        data = {"promotionKind": "microsoftNewsService" if promote else "none"}
        logger.info(f"Setting page {page_id} as news post")
        await self.post(endpoint, data)

        return {
            "page_info": published_page,
            "title": title,
            "description": description,
            "isNewsPost": True,
        }

    async def add_section_to_page(
        self, site_id: str, page_id: str, section_type: str = "OneColumn"
    ) -> Dict[str, Any]:
        """Add a section to a SharePoint page."""
        endpoint = f"sites/{site_id}/pages/{page_id}/sections"
        data = {"columnLayoutType": section_type}
        logger.info(f"Adding {section_type} section to page {page_id}")
        return await self.post(endpoint, data)

    async def add_web_part_to_section(
        self,
        site_id: str,
        page_id: str,
        section_id: str,
        column_id: str,
        web_part_type: str,
        web_part_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a web part to a page section."""
        endpoint = f"sites/{site_id}/pages/{page_id}/sections/{section_id}/columns/{column_id}/webparts"
        data = {"type": web_part_type, "data": web_part_data}
        logger.info(f"Adding {web_part_type} web part to page {page_id}")
        return await self.post(endpoint, data)

    async def update_page(
        self, site_id: str, page_id: str, title: str = None, content: str = None
    ) -> Dict[str, Any]:
        """Update a SharePoint page."""
        endpoint = f"sites/{site_id}/pages/{page_id}"
        data = {}
        if title:
            data["title"] = title
        if content:
            data["canvasLayout"] = {
                "horizontal": {
                    "sections": [
                        {
                            "columns": [
                                {
                                    "width": 12,
                                    "webparts": [
                                        {"type": "Text", "data": {"text": content}}
                                    ],
                                }
                            ]
                        }
                    ]
                }
            }
        logger.info(f"Updating page {page_id}")
        return await self.patch(endpoint, data)

    async def publish_page(self, site_id: str, page_id: str) -> Dict[str, Any]:
        """Publish a SharePoint page."""
        endpoint = f"sites/{site_id}/pages/{page_id}/publish"
        logger.info(f"Publishing page {page_id}")
        return await self.post(endpoint, {})
