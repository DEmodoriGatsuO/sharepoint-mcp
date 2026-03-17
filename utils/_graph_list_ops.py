"""List and list item operations mixin for GraphClient."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("graph_client")


class _GraphListOpsMixin:
    """List CRUD and schema operations for the Microsoft Graph API."""

    async def create_list(
        self,
        site_id: str,
        display_name: str,
        template: str = "genericList",
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a new list in a SharePoint site."""
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
        """Create a new item in a SharePoint list."""
        endpoint = f"sites/{site_id}/lists/{list_id}/items"
        data = {"fields": fields}
        logger.info(f"Creating new list item in list: {list_id}")
        return await self.post(endpoint, data)

    async def update_list_item(
        self, site_id: str, list_id: str, item_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing item in a SharePoint list."""
        endpoint = f"sites/{site_id}/lists/{list_id}/items/{item_id}/fields"
        logger.info(f"Updating list item {item_id} in list: {list_id}")
        return await self.patch(endpoint, fields)

    async def delete_list_item(
        self, site_id: str, list_id: str, item_id: str
    ) -> Dict[str, Any]:
        """Delete an item from a SharePoint list."""
        endpoint = f"sites/{site_id}/lists/{list_id}/items/{item_id}"
        logger.info(f"Deleting list item {item_id} from list: {list_id}")
        return await self.delete(endpoint)

    async def add_column_to_list(
        self, site_id: str, list_id: str, column_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a column to a SharePoint list."""
        endpoint = f"sites/{site_id}/lists/{list_id}/columns"
        data = {
            "name": column_def["name"],
            "description": column_def.get("description", ""),
        }

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

        if column_def.get("required", False):
            data["isRequired"] = True

        logger.info(f"Adding column {column_def['name']} to list {list_id}")
        return await self.post(endpoint, data)

    async def create_intelligent_list(
        self, site_id: str, purpose: str, display_name: str
    ) -> Dict[str, Any]:
        """Create a SharePoint list with AI-optimized schema based on its purpose."""
        endpoint = f"sites/{site_id}/lists"
        data = {
            "displayName": display_name,
            "list": {"template": "genericList"},
            "description": f"AI-optimized list for {purpose}",
        }

        logger.info(f"Creating intelligent list for purpose: {purpose}")
        list_info = await self.post(endpoint, data)
        list_id = list_info.get("id")

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
        """Get AI-recommended schema based on list purpose."""
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
