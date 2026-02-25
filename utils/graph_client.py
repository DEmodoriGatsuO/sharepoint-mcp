"""Microsoft Graph API client for SharePoint MCP server."""

import requests
import logging
from typing import Dict, Any, List, Union, BinaryIO

from auth.sharepoint_auth import SharePointContext

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("graph_client")


class GraphClient:
    """Client for interacting with Microsoft Graph API."""

    def __init__(self, context: SharePointContext):
        """Initialize Graph client with SharePoint context.

        Args:
            context: SharePoint authentication context
        """
        self.context = context
        self.base_url = context.graph_url
        logger.debug(f"GraphClient initialized with base URL: {self.base_url}")

    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Send GET request to Graph API.

        Args:
            endpoint: API endpoint path (without base URL)

        Returns:
            Response from the API as dictionary

        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making GET request to: {url}")

        # Get headers from context (including auth token)
        headers = self.context.headers

        # Send request
        response = requests.get(url, headers=headers)

        # Log response
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")

            # Log detailed info for auth errors
            if response.status_code in (401, 403):
                logger.error("Authentication or authorization error detected")
                if "scp or roles claim" in error_text:
                    logger.error("Token does not have required claims (scp or roles)")
                    logger.error("Please check application permissions in Azure AD")

            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        # Return successful response as JSON
        return response.json()

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send POST request to Graph API.

        Args:
            endpoint: API endpoint path (without base URL)
            data: JSON data to send

        Returns:
            Response from the API as dictionary

        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making POST request to: {url}")
        logger.debug(f"With data: {data}")

        # Get headers from context (including auth token)
        headers = self.context.headers

        # Send request
        response = requests.post(url, headers=headers, json=data)

        # Log response
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")

            # Log detailed info for auth errors
            if response.status_code in (401, 403):
                logger.error("Authentication or authorization error detected")
                if "scp or roles claim" in error_text:
                    logger.error("Token does not have required claims (scp or roles)")
                    logger.error("Please check application permissions in Azure AD")

            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        # Return successful response as JSON
        return response.json()

    async def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send PATCH request to Graph API.

        Args:
            endpoint: API endpoint path (without base URL)
            data: JSON data to send

        Returns:
            Response from the API as dictionary

        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making PATCH request to: {url}")
        logger.debug(f"With data: {data}")

        # Get headers from context (including auth token)
        headers = self.context.headers

        # Send request
        response = requests.patch(url, headers=headers, json=data)

        # Log response
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201, 204):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        # Return successful response as JSON if available
        if response.status_code == 204:
            return {"status": "success"}
        return response.json()

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Send DELETE request to Graph API.

        Args:
            endpoint: API endpoint path (without base URL)

        Returns:
            Status information

        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making DELETE request to: {url}")

        # Get headers from context (including auth token)
        headers = self.context.headers

        # Send request
        response = requests.delete(url, headers=headers)

        # Log response
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201, 204):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        # Return successful status
        return {"status": "success"}

    async def upload_file(
        self,
        endpoint: str,
        file_content: Union[bytes, BinaryIO],
        content_type: str = None,
    ) -> Dict[str, Any]:
        """Upload file content to Graph API.

        Args:
            endpoint: API endpoint path (without base URL)
            file_content: File content as bytes or file-like object
            content_type: MIME type of the file

        Returns:
            Response from the API as dictionary

        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Uploading file to: {url}")

        # Get headers from context (including auth token)
        headers = self.context.headers.copy()

        # Set content type if provided
        if content_type:
            headers["Content-Type"] = content_type

        # Send request
        response = requests.put(url, headers=headers, data=file_content)

        # Log response
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201, 204):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        # Return successful response as JSON if available
        if response.status_code == 204:
            return {"status": "success"}
        return response.json()

    async def get_site_info(self, domain: str, site_name: str) -> Dict[str, Any]:
        """Get SharePoint site information.

        Args:
            domain: SharePoint domain
            site_name: Name of the site (use "root" or empty string for root site)

        Returns:
            Site information
        """
        # For root site, use different endpoint format
        if site_name == "root" or not site_name:
            endpoint = f"sites/{domain}:"
        else:
            endpoint = f"sites/{domain}:/sites/{site_name}"
        logger.info(f"Getting site info for domain: {domain}, site: {site_name}")
        return await self.get(endpoint)

    async def list_document_libraries(
        self, domain: str, site_name: str
    ) -> Dict[str, Any]:
        """List all document libraries in the site.

        Args:
            domain: SharePoint domain
            site_name: Name of the site (use "root" or empty string for root site)

        Returns:
            List of document libraries
        """
        # First get site info to retrieve the site ID
        # This is necessary because application credentials require the site ID format
        site_info = await self.get_site_info(domain, site_name)
        site_id = site_info.get("id")

        if not site_id:
            raise Exception(
                f"Failed to get site ID for domain: {domain}, site: {site_name}"
            )

        # Use site ID to list drives
        endpoint = f"sites/{site_id}/drives"
        logger.info(f"Listing document libraries for site ID: {site_id}")
        return await self.get(endpoint)

    async def create_site(
        self, display_name: str, alias: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new SharePoint site.

        Args:
            display_name: Display name of the site
            alias: Site alias (used in URL)
            description: Site description

        Returns:
            Created site information
        """
        endpoint = "sites/root/sites"
        data = {"displayName": display_name, "alias": alias, "description": description}
        logger.info(f"Creating new site with name: {display_name}, alias: {alias}")
        return await self.post(endpoint, data)

    async def create_list(
        self,
        site_id: str,
        display_name: str,
        template: str = "genericList",
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a new list in a SharePoint site.

        Args:
            site_id: ID of the site
            display_name: Display name of the list
            template: List template type (genericList, documentLibrary, etc.)
            description: List description

        Returns:
            Created list information
        """
        endpoint = f"sites/{site_id}/lists"
        data = {
            "displayName": display_name,
            "list": {"template": template},
            "description": description,
        }
        logger.info(f"Creating new list with name: {display_name} in site: {site_id}")
        return await self.post(endpoint, data)

    async def create_list_item(
        self, site_id: str, list_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new item in a SharePoint list.

        Args:
            site_id: ID of the site
            list_id: ID of the list
            fields: Dictionary of field names and values

        Returns:
            Created list item information
        """
        endpoint = f"sites/{site_id}/lists/{list_id}/items"
        data = {"fields": fields}
        logger.info(f"Creating new list item in list: {list_id}")
        return await self.post(endpoint, data)

    async def update_list_item(
        self, site_id: str, list_id: str, item_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing item in a SharePoint list.

        Args:
            site_id: ID of the site
            list_id: ID of the list
            item_id: ID of the list item
            fields: Dictionary of field names and values to update

        Returns:
            Updated list item information
        """
        endpoint = f"sites/{site_id}/lists/{list_id}/items/{item_id}/fields"
        logger.info(f"Updating list item {item_id} in list: {list_id}")
        return await self.patch(endpoint, fields)

    async def delete_list_item(
        self, site_id: str, list_id: str, item_id: str
    ) -> Dict[str, Any]:
        """Delete an item from a SharePoint list.

        Args:
            site_id: ID of the site
            list_id: ID of the list
            item_id: ID of the list item

        Returns:
            Status information
        """
        endpoint = f"sites/{site_id}/lists/{list_id}/items/{item_id}"
        logger.info(f"Deleting list item {item_id} from list: {list_id}")
        return await self.delete(endpoint)

    async def add_column_to_list(
        self, site_id: str, list_id: str, column_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a column to a SharePoint list.

        Args:
            site_id: ID of the site
            list_id: ID of the list
            column_def: Column definition

        Returns:
            Created column information
        """
        endpoint = f"sites/{site_id}/lists/{list_id}/columns"
        data = {
            "name": column_def["name"],
            "description": column_def.get("description", ""),
        }

        # Set column type-specific properties
        col_type = column_def.get("type", "text")
        if col_type == "text":
            data["text"] = {}
        elif col_type == "choice":
            data["choice"] = {"choices": column_def.get("choices", [])}
        elif col_type == "dateTime":
            data["dateTime"] = {}
        elif col_type == "number":
            data["number"] = {}
        elif col_type == "boolean":
            data["boolean"] = {}
        elif col_type == "person":
            data["personOrGroup"] = {
                "allowMultipleSelection": column_def.get("multiValue", False)
            }
        elif col_type == "richText":
            data["text"] = {"textType": "richText"}
        elif col_type == "currency":
            data["number"] = {"format": "currency"}

        # Set required property if specified
        if column_def.get("required", False):
            data["isRequired"] = True

        logger.info(f"Adding column {column_def['name']} to list {list_id}")
        return await self.post(endpoint, data)

    async def create_page(
        self, site_id: str, name: str, title: str = ""
    ) -> Dict[str, Any]:
        """Create a new page in a SharePoint site.

        Args:
            site_id: ID of the site
            name: Name of the page
            title: Title of the page

        Returns:
            Created page information
        """
        endpoint = f"sites/{site_id}/pages"
        data = {"name": name, "title": title or name}
        logger.info(f"Creating new page with name: {name} in site: {site_id}")
        return await self.post(endpoint, data)

    async def create_modern_page(
        self, site_id: str, name: str, title: str, layout: str = "Article"
    ) -> Dict[str, Any]:
        """Create a modern page with professional layout in SharePoint.

        Args:
            site_id: ID of the site
            name: Name of the page
            title: Title of the page
            layout: Page layout type

        Returns:
            Created page information
        """
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
        """Create a news post in a SharePoint site.

        Args:
            site_id: ID of the site
            title: Title of the news post
            description: Brief description of the news post
            content: HTML content of the news post
            promote: Whether to promote the news post

        Returns:
            Created news post information
        """
        # First create a modern page
        name = f"news-{title.lower().replace(' ', '-')}"
        page_info = await self.create_modern_page(site_id, name, title, "Article")
        page_id = page_info.get("id")

        # Update page with content
        await self.update_page(site_id, page_id, title, content)

        # Publish the page
        published_page = await self.publish_page(site_id, page_id)

        # Set as news post
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
        """Add a section to a SharePoint page.

        Args:
            site_id: ID of the site
            page_id: ID of the page
            section_type: Type of section (OneColumn, TwoColumn, ThreeColumn)

        Returns:
            Updated page information
        """
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
        """Add a web part to a page section.

        Args:
            site_id: ID of the site
            page_id: ID of the page
            section_id: ID of the section
            column_id: ID of the column
            web_part_type: Type of web part
            web_part_data: Web part data

        Returns:
            Updated page information
        """
        endpoint = f"sites/{site_id}/pages/{page_id}/sections/{section_id}/columns/{column_id}/webparts"
        data = {"type": web_part_type, "data": web_part_data}
        logger.info(f"Adding {web_part_type} web part to page {page_id}")
        return await self.post(endpoint, data)

    async def update_page(
        self, site_id: str, page_id: str, title: str = None, content: str = None
    ) -> Dict[str, Any]:
        """Update a SharePoint page.

        Args:
            site_id: ID of the site
            page_id: ID of the page
            title: New title of the page
            content: New content of the page

        Returns:
            Updated page information
        """
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
        """Publish a SharePoint page.

        Args:
            site_id: ID of the site
            page_id: ID of the page

        Returns:
            Published page information
        """
        endpoint = f"sites/{site_id}/pages/{page_id}/publish"
        logger.info(f"Publishing page {page_id}")
        return await self.post(endpoint, {})

    async def get_document_content(
        self, site_id: str, drive_id: str, item_id: str
    ) -> bytes:
        """Get content of a document.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library
            item_id: ID of the document

        Returns:
            Document content as bytes
        """
        url = (
            f"{self.base_url}/sites/{site_id}/drives/{drive_id}/items/{item_id}/content"
        )
        headers = self.context.headers.copy()
        # Remove Content-Type header to respect response Content-Type
        headers.pop("Content-Type", None)

        logger.info(f"Getting document content for item {item_id}")
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        return response.content

    async def upload_document(
        self,
        site_id: str,
        drive_id: str,
        folder_path: str,
        file_name: str,
        file_content: bytes,
        content_type: str = None,
    ) -> Dict[str, Any]:
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
        # Prepare the endpoint
        if folder_path and folder_path != "/":
            # Upload to a subfolder
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
        else:
            # Upload to root folder
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{file_name}:/content"

        logger.info(
            f"Uploading document {file_name} to {folder_path if folder_path else 'root'}"
        )

        # For small files, use simple upload
        if len(file_content) < 4 * 1024 * 1024:  # 4 MB
            return await self.upload_file(endpoint, file_content, content_type)
        else:
            # For larger files, we need to use upload session (not implemented for simplicity)
            # This would involve creating an upload session and uploading the file in chunks
            logger.warning("Large file upload (>4MB) should use upload session.")
            logger.warning(
                "Implementing simple upload instead, which might fail for large files."
            )
            return await self.upload_file(endpoint, file_content, content_type)

    async def create_folder_in_library(
        self, site_id: str, drive_id: str, folder_path: str
    ) -> Dict[str, Any]:
        """Create a folder in a document library.

        Args:
            site_id: ID of the site
            drive_id: ID of the document library
            folder_path: Path of the folder to create

        Returns:
            Created folder information
        """
        # Check if the folder path has multiple levels
        parts = folder_path.split("/")
        current_path = ""
        result = None

        # Create each level of the folder path
        for i, part in enumerate(parts):
            if not part:
                continue

            if current_path:
                current_path += f"/{part}"
            else:
                current_path = part

            # Create the folder
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{current_path}"

            try:
                # Check if folder exists
                result = await self.get(endpoint)
                logger.info(f"Folder '{current_path}' already exists")
            except Exception:
                # Folder doesn't exist, create it
                endpoint = f"sites/{site_id}/drives/{drive_id}/root/children"
                data = {
                    "name": part,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "rename",
                }

                # If it's not the root level, specify the parent folder
                if i > 0:
                    parent_path = "/".join(parts[:i])
                    endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{parent_path}:/children"

                logger.info(f"Creating folder '{part}' in path '{current_path}'")
                result = await self.post(endpoint, data)

        return result

    async def create_intelligent_list(
        self, site_id: str, purpose: str, display_name: str
    ) -> Dict[str, Any]:
        """Create a SharePoint list with AI-optimized schema based on its purpose.

        Args:
            site_id: ID of the site
            purpose: Purpose of the list (e.g. "projects", "contacts", "events")
            display_name: Display name for the list

        Returns:
            Created list information
        """
        # Create basic list first
        endpoint = f"sites/{site_id}/lists"
        data = {
            "displayName": display_name,
            "list": {"template": "genericList"},
            "description": f"AI-optimized list for {purpose}",
        }

        logger.info(f"Creating intelligent list for purpose: {purpose}")
        list_info = await self.post(endpoint, data)
        list_id = list_info.get("id")

        # Add schema columns based on purpose
        columns = await self._get_intelligent_schema_for_purpose(purpose)

        for column in columns:
            try:
                await self.add_column_to_list(site_id, list_id, column)
            except Exception as e:
                logger.warning(f"Error adding column {column.get('name')}: {str(e)}")

        return list_info

    async def _get_intelligent_schema_for_purpose(
        self, purpose: str
    ) -> List[Dict[str, Any]]:
        """Get AI-recommended schema based on list purpose.

        Args:
            purpose: Purpose of the list

        Returns:
            List of column definitions
        """
        # Return optimized schema based on purpose
        schemas = {
            "projects": [
                {"name": "ProjectName", "type": "text", "required": True},
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": [
                        "Not Started",
                        "In Progress",
                        "Completed",
                        "On Hold",
                        "Cancelled",
                    ],
                },
                {"name": "StartDate", "type": "dateTime"},
                {"name": "DueDate", "type": "dateTime"},
                {
                    "name": "Priority",
                    "type": "choice",
                    "choices": ["Low", "Medium", "High", "Critical"],
                },
                {"name": "PercentComplete", "type": "number"},
                {"name": "AssignedTo", "type": "person", "multiValue": True},
                {"name": "Description", "type": "richText"},
                {
                    "name": "Department",
                    "type": "choice",
                    "choices": ["Marketing", "IT", "Finance", "Operations", "HR"],
                },
                {"name": "Budget", "type": "currency"},
            ],
            "events": [
                {"name": "EventTitle", "type": "text", "required": True},
                {"name": "EventDate", "type": "dateTime", "required": True},
                {"name": "EndDate", "type": "dateTime"},
                {"name": "Location", "type": "text"},
                {"name": "Description", "type": "richText"},
                {
                    "name": "Category",
                    "type": "choice",
                    "choices": ["Meeting", "Conference", "Workshop", "Social", "Other"],
                },
                {"name": "Organizer", "type": "person"},
                {"name": "Attendees", "type": "person", "multiValue": True},
                {"name": "IsAllDayEvent", "type": "boolean"},
                {"name": "RequiresRegistration", "type": "boolean"},
            ],
            "tasks": [
                {"name": "TaskName", "type": "text", "required": True},
                {
                    "name": "Priority",
                    "type": "choice",
                    "choices": ["Low", "Normal", "High", "Urgent"],
                },
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": ["Not Started", "In Progress", "Completed", "Deferred"],
                },
                {"name": "DueDate", "type": "dateTime"},
                {"name": "AssignedTo", "type": "person", "multiValue": False},
                {"name": "CompletedDate", "type": "dateTime"},
                {"name": "Description", "type": "richText"},
                {
                    "name": "Category",
                    "type": "choice",
                    "choices": ["Administrative", "Financial", "Customer", "Technical"],
                },
            ],
            "contacts": [
                {"name": "FullName", "type": "text", "required": True},
                {"name": "EmailAddress", "type": "text"},
                {"name": "Company", "type": "text"},
                {"name": "JobTitle", "type": "text"},
                {"name": "BusinessPhone", "type": "text"},
                {"name": "MobilePhone", "type": "text"},
                {"name": "Address", "type": "text"},
                {"name": "City", "type": "text"},
                {"name": "State", "type": "text"},
                {"name": "ZipCode", "type": "text"},
                {"name": "Country", "type": "text"},
                {"name": "WebSite", "type": "text"},
                {"name": "Notes", "type": "richText"},
                {
                    "name": "ContactType",
                    "type": "choice",
                    "choices": ["Customer", "Partner", "Supplier", "Internal", "Other"],
                },
            ],
            "documents": [
                {
                    "name": "DocumentType",
                    "type": "choice",
                    "choices": [
                        "Contract",
                        "Report",
                        "Presentation",
                        "Specification",
                        "Invoice",
                        "Other",
                    ],
                },
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": [
                        "Draft",
                        "In Review",
                        "Approved",
                        "Published",
                        "Archived",
                    ],
                },
                {
                    "name": "Department",
                    "type": "choice",
                    "choices": [
                        "Marketing",
                        "Sales",
                        "HR",
                        "Finance",
                        "IT",
                        "Operations",
                    ],
                },
                {"name": "Author", "type": "person"},
                {"name": "Reviewers", "type": "person", "multiValue": True},
                {"name": "PublishedDate", "type": "dateTime"},
                {"name": "ExpiryDate", "type": "dateTime"},
                {"name": "Keywords", "type": "text"},
                {"name": "Version", "type": "text"},
                {
                    "name": "Confidentiality",
                    "type": "choice",
                    "choices": ["Public", "Internal", "Confidential", "Restricted"],
                },
            ],
        }

        return schemas.get(
            purpose.lower(),
            [
                {"name": "Title", "type": "text", "required": True},
                {"name": "Description", "type": "richText"},
            ],
        )

    async def create_advanced_document_library(
        self, site_id: str, display_name: str, doc_type: str = "general"
    ) -> Dict[str, Any]:
        """Create a document library with advanced metadata settings.

        Args:
            site_id: ID of the site
            display_name: Display name of the library
            doc_type: Type of documents to store (general, contracts, marketing, etc.)

        Returns:
            Created document library information
        """
        # Create the document library
        endpoint = f"sites/{site_id}/lists"
        data = {
            "displayName": display_name,
            "list": {"template": "documentLibrary"},
            "description": f"Advanced document library for {doc_type} documents",
        }

        logger.info(f"Creating advanced document library for {doc_type} documents")
        library_info = await self.post(endpoint, data)
        list_id = library_info.get("id")
        drive_id = None

        # Get the drive ID for the document library
        drives_endpoint = f"sites/{site_id}/lists/{list_id}/drive"
        try:
            drive_info = await self.get(drives_endpoint)
            drive_id = drive_info.get("id")
        except Exception as e:
            logger.warning(f"Could not get drive ID: {str(e)}")

        # Add metadata columns based on document type
        columns = await self._get_document_metadata_schema(doc_type)

        for column in columns:
            try:
                await self.add_column_to_list(site_id, list_id, column)
            except Exception as e:
                logger.warning(f"Error adding column {column.get('name')}: {str(e)}")

        # Create folder structure if drive ID is available
        if drive_id:
            folders = await self._get_folder_structure_for_document_type(doc_type)

            for folder in folders:
                try:
                    await self.create_folder_in_library(site_id, drive_id, folder)
                except Exception as e:
                    logger.warning(f"Error creating folder {folder}: {str(e)}")

        return library_info

    async def _get_document_metadata_schema(
        self, doc_type: str
    ) -> List[Dict[str, Any]]:
        """Get document metadata schema based on document type.

        Args:
            doc_type: Type of documents

        Returns:
            List of column definitions
        """
        # Return optimized schema based on document type
        schemas = {
            "contracts": [
                {
                    "name": "ContractType",
                    "type": "choice",
                    "choices": [
                        "Service",
                        "Employment",
                        "NDA",
                        "License",
                        "Lease",
                        "Purchase",
                    ],
                },
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": [
                        "Draft",
                        "Under Review",
                        "Signed",
                        "Active",
                        "Expired",
                        "Terminated",
                    ],
                },
                {"name": "EffectiveDate", "type": "dateTime"},
                {"name": "ExpirationDate", "type": "dateTime"},
                {"name": "ContractValue", "type": "currency"},
                {"name": "Counterparty", "type": "text"},
                {
                    "name": "ResponsibleDepartment",
                    "type": "choice",
                    "choices": ["Legal", "HR", "Sales", "Procurement", "Finance"],
                },
                {"name": "RenewalTerm", "type": "text"},
                {"name": "NotificationDays", "type": "number"},
                {"name": "Keywords", "type": "text"},
            ],
            "marketing": [
                {
                    "name": "AssetType",
                    "type": "choice",
                    "choices": [
                        "Brochure",
                        "Presentation",
                        "Logo",
                        "Image",
                        "Video",
                        "Social Media",
                        "Campaign",
                    ],
                },
                {"name": "Brand", "type": "text"},
                {"name": "Campaign", "type": "text"},
                {
                    "name": "TargetAudience",
                    "type": "choice",
                    "choices": [
                        "Customers",
                        "Prospects",
                        "Partners",
                        "Employees",
                        "Investors",
                    ],
                },
                {
                    "name": "Channel",
                    "type": "choice",
                    "choices": [
                        "Email",
                        "Social",
                        "Print",
                        "Web",
                        "TV",
                        "Radio",
                        "Event",
                    ],
                },
                {"name": "CreativeVersion", "type": "text"},
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": [
                        "Draft",
                        "In Review",
                        "Approved",
                        "Published",
                        "Archived",
                    ],
                },
                {"name": "PublishDate", "type": "dateTime"},
                {"name": "DesignedBy", "type": "person"},
                {"name": "ApprovedBy", "type": "person"},
            ],
            "reports": [
                {
                    "name": "ReportType",
                    "type": "choice",
                    "choices": [
                        "Financial",
                        "Sales",
                        "Marketing",
                        "Operations",
                        "HR",
                        "Project",
                    ],
                },
                {
                    "name": "Period",
                    "type": "choice",
                    "choices": [
                        "Daily",
                        "Weekly",
                        "Monthly",
                        "Quarterly",
                        "Annual",
                        "Custom",
                    ],
                },
                {
                    "name": "Department",
                    "type": "choice",
                    "choices": [
                        "Finance",
                        "Sales",
                        "Marketing",
                        "IT",
                        "HR",
                        "Operations",
                    ],
                },
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": ["Draft", "In Review", "Final", "Published", "Archived"],
                },
                {"name": "Author", "type": "person"},
                {"name": "ReportDate", "type": "dateTime"},
                {"name": "CoverageStartDate", "type": "dateTime"},
                {"name": "CoverageEndDate", "type": "dateTime"},
                {"name": "Keywords", "type": "text"},
                {
                    "name": "Confidentiality",
                    "type": "choice",
                    "choices": ["Public", "Internal", "Confidential", "Restricted"],
                },
            ],
        }

        return schemas.get(
            doc_type.lower(),
            [
                {
                    "name": "DocumentType",
                    "type": "choice",
                    "choices": [
                        "Report",
                        "Policy",
                        "Procedure",
                        "Form",
                        "Template",
                        "Other",
                    ],
                },
                {
                    "name": "Status",
                    "type": "choice",
                    "choices": [
                        "Draft",
                        "In Review",
                        "Approved",
                        "Published",
                        "Archived",
                    ],
                },
                {"name": "Author", "type": "person"},
                {
                    "name": "Department",
                    "type": "choice",
                    "choices": [
                        "Marketing",
                        "Sales",
                        "HR",
                        "Finance",
                        "IT",
                        "Operations",
                    ],
                },
                {"name": "CreatedDate", "type": "dateTime"},
                {"name": "Keywords", "type": "text"},
            ],
        )

    async def _get_folder_structure_for_document_type(self, doc_type: str) -> List[str]:
        """Get recommended folder structure for document type.

        Args:
            doc_type: Type of documents

        Returns:
            List of folder paths
        """
        # Return recommended folder structure based on document type
        structures = {
            "contracts": [
                "Active Contracts",
                "Expired Contracts",
                "Templates",
                "NDAs",
                "Service Agreements",
                "Employment",
            ],
            "marketing": [
                "Brand Assets",
                "Campaigns",
                "Social Media",
                "Presentations",
                "Print Materials",
                "Digital Assets",
                "Events",
            ],
            "reports": [
                "Financial",
                "Sales",
                "Marketing",
                "Operations",
                "Human Resources",
                "Executive",
                "Archive",
            ],
            "projects": [
                "Planning",
                "Requirements",
                "Design",
                "Implementation",
                "Testing",
                "Deployment",
                "Review",
            ],
        }

        return structures.get(
            doc_type.lower(),
            ["General", "Templates", "Working Documents", "Published", "Archive"],
        )
