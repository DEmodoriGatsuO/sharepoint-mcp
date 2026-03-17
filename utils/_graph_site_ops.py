"""Site and document library operations mixin for GraphClient."""

import logging
from typing import Dict, Any

logger = logging.getLogger("graph_client")


class _GraphSiteOpsMixin:
    """Site and top-level library operations for the Microsoft Graph API."""

    async def get_site_info(self, domain: str, site_name: str) -> Dict[str, Any]:
        """Get SharePoint site information."""
        if site_name == "root" or not site_name:
            endpoint = f"sites/{domain}:"
        else:
            endpoint = f"sites/{domain}:/sites/{site_name}"
        logger.info(f"Getting site info for domain: {domain}, site: {site_name}")
        return await self.get(endpoint)

    async def list_document_libraries(
        self, domain: str, site_name: str
    ) -> Dict[str, Any]:
        """List all document libraries in the site."""
        site_info = await self.get_site_info(domain, site_name)
        site_id = site_info.get("id")

        if not site_id:
            raise Exception(
                f"Failed to get site ID for domain: {domain}, site: {site_name}"
            )

        endpoint = f"sites/{site_id}/drives"
        logger.info(f"Listing document libraries for site ID: {site_id}")
        return await self.get(endpoint)

    async def create_site(
        self, display_name: str, alias: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new SharePoint site."""
        endpoint = "sites/root/sites"
        data = {"displayName": display_name, "alias": alias, "description": description}
        logger.info(f"Creating new site with name: {display_name}, alias: {alias}")
        return await self.post(endpoint, data)
