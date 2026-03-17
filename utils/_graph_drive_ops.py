"""Drive, file, and folder operations mixin for GraphClient."""

import logging
from typing import Dict, Any, List

import requests

from utils._graph_constants import LARGE_FILE_THRESHOLD, UPLOAD_CHUNK_SIZE  # noqa: F401

logger = logging.getLogger("graph_client")


class _GraphDriveOpsMixin:
    """Drive/file/folder operations for the Microsoft Graph API."""

    async def get_document_content(
        self, site_id: str, drive_id: str, item_id: str
    ) -> bytes:
        """Get content of a document by item ID."""
        url = (
            f"{self.base_url}/sites/{site_id}/drives/{drive_id}/items/{item_id}/content"
        )
        headers = self.context.headers.copy()
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
        """Upload a document to a SharePoint document library."""
        if folder_path and folder_path != "/":
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
        else:
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{file_name}:/content"

        logger.info(
            f"Uploading document {file_name} to {folder_path if folder_path else 'root'}"
        )

        if len(file_content) < LARGE_FILE_THRESHOLD:
            return await self.upload_file(endpoint, file_content, content_type)

        if folder_path and folder_path != "/":
            session_endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{folder_path}/{file_name}:/createUploadSession"
        else:
            session_endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{file_name}:/createUploadSession"

        session_url = f"{self.base_url}/{session_endpoint}"
        logger.info(
            f"File size {len(file_content)} bytes exceeds threshold; using upload session"
        )
        session_response = requests.post(
            session_url, headers=self.context.headers, json={}
        )
        if session_response.status_code != 200:
            raise Exception(
                f"Failed to create upload session: {session_response.status_code} - {session_response.text}"
            )

        upload_url = session_response.json().get("uploadUrl")
        if not upload_url:
            raise Exception("Upload session response did not contain uploadUrl")

        return await self._upload_in_chunks(upload_url, file_content, content_type)

    async def create_folder_in_library(
        self, site_id: str, drive_id: str, folder_path: str
    ) -> Dict[str, Any]:
        """Create a folder (and any parent folders) in a document library."""
        parts = folder_path.split("/")
        current_path = ""
        result = None

        for i, part in enumerate(parts):
            if not part:
                continue

            if current_path:
                current_path += f"/{part}"
            else:
                current_path = part

            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{current_path}"

            try:
                result = await self.get(endpoint)
                logger.info(f"Folder '{current_path}' already exists")
            except Exception:
                endpoint = f"sites/{site_id}/drives/{drive_id}/root/children"
                data = {
                    "name": part,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "rename",
                }

                if i > 0:
                    parent_path = "/".join(parts[:i])
                    endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{parent_path}:/children"

                logger.info(f"Creating folder '{part}' in path '{current_path}'")
                result = await self.post(endpoint, data)

        return result

    async def create_advanced_document_library(
        self, site_id: str, display_name: str, doc_type: str = "general"
    ) -> Dict[str, Any]:
        """Create a document library with advanced metadata settings."""
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

        drives_endpoint = f"sites/{site_id}/lists/{list_id}/drive"
        try:
            drive_info = await self.get(drives_endpoint)
            drive_id = drive_info.get("id")
        except Exception as e:
            logger.warning(f"Could not get drive ID: {str(e)}")

        columns = await self._get_document_metadata_schema(doc_type)
        for column in columns:
            try:
                await self.add_column_to_list(site_id, list_id, column)
            except Exception as e:
                logger.warning(f"Error adding column {column.get('name')}: {str(e)}")

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
        """Get document metadata schema based on document type."""
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
        """Get recommended folder structure for document type."""
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

    async def list_folder_contents(
        self, site_id: str, drive_id: str, folder_path: str = ""
    ) -> Dict[str, Any]:
        """List files and folders at a given path in a document library."""
        if not folder_path or folder_path.strip("/") == "":
            endpoint = f"sites/{site_id}/drives/{drive_id}/root/children"
        else:
            clean_path = folder_path.strip("/")
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{clean_path}:/children"

        logger.info(f"Listing folder contents at path: '{folder_path or '/'}'")
        return await self.get(endpoint)

    async def get_document_content_by_path(
        self, site_id: str, drive_id: str, file_path: str
    ) -> bytes:
        """Get content of a document by its path in a document library."""
        clean_path = file_path.strip("/")
        url = f"{self.base_url}/sites/{site_id}/drives/{drive_id}/root:/{clean_path}:/content"

        headers = self.context.headers.copy()
        headers.pop("Content-Type", None)

        logger.info(f"Getting document content by path: '{file_path}'")
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        return response.content

    async def get_item_metadata_by_path(
        self, site_id: str, drive_id: str, item_path: str
    ) -> Dict[str, Any]:
        """Get metadata of a file or folder by its path in a document library."""
        clean_path = item_path.strip("/")
        endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{clean_path}"

        logger.info(f"Getting item metadata by path: '{item_path}'")
        return await self.get(endpoint)
