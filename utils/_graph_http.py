"""HTTP transport mixin for GraphClient."""

import logging
from typing import Dict, Any, Union, BinaryIO

import requests

from utils._graph_constants import UPLOAD_CHUNK_SIZE

logger = logging.getLogger("graph_client")


class _GraphHttpMixin:
    """Base HTTP methods for the Microsoft Graph API."""

    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Send GET request to Graph API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making GET request to: {url}")

        headers = self.context.headers
        response = requests.get(url, headers=headers)
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            if response.status_code in (401, 403):
                logger.error("Authentication or authorization error detected")
                if "scp or roles claim" in error_text:
                    logger.error("Token does not have required claims (scp or roles)")
                    logger.error("Please check application permissions in Azure AD")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        return response.json()

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send POST request to Graph API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making POST request to: {url}")
        logger.debug(f"With data: {data}")

        headers = self.context.headers
        response = requests.post(url, headers=headers, json=data)
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            if response.status_code in (401, 403):
                logger.error("Authentication or authorization error detected")
                if "scp or roles claim" in error_text:
                    logger.error("Token does not have required claims (scp or roles)")
                    logger.error("Please check application permissions in Azure AD")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        return response.json()

    async def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send PATCH request to Graph API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making PATCH request to: {url}")
        logger.debug(f"With data: {data}")

        headers = self.context.headers
        response = requests.patch(url, headers=headers, json=data)
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201, 204):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        if response.status_code == 204:
            return {"status": "success"}
        return response.json()

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Send DELETE request to Graph API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Making DELETE request to: {url}")

        headers = self.context.headers
        response = requests.delete(url, headers=headers)
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201, 204):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        return {"status": "success"}

    async def upload_file(
        self,
        endpoint: str,
        file_content: Union[bytes, BinaryIO],
        content_type: str = None,
    ) -> Dict[str, Any]:
        """Upload file content to Graph API via simple PUT."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug(f"Uploading file to: {url}")

        headers = self.context.headers.copy()
        if content_type:
            headers["Content-Type"] = content_type

        response = requests.put(url, headers=headers, data=file_content)
        logger.debug(f"Response status code: {response.status_code}")

        if response.status_code not in (200, 201, 204):
            error_text = response.text
            logger.error(f"Graph API error: {response.status_code} - {error_text}")
            raise Exception(f"Graph API error: {response.status_code} - {error_text}")

        if response.status_code == 204:
            return {"status": "success"}
        return response.json()

    async def _upload_in_chunks(
        self,
        upload_url: str,
        file_content: bytes,
        content_type: str = None,
    ) -> Dict[str, Any]:
        """Upload file content to an upload session URL in chunks."""
        total_size = len(file_content)
        start = 0
        result: Dict[str, Any] = {}

        while start < total_size:
            end = min(start + UPLOAD_CHUNK_SIZE - 1, total_size - 1)
            chunk = file_content[start : end + 1]

            headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {start}-{end}/{total_size}",
            }
            if content_type:
                headers["Content-Type"] = content_type

            logger.debug(f"Uploading chunk: bytes {start}-{end}/{total_size}")
            response = requests.put(upload_url, headers=headers, data=chunk)

            if response.status_code not in (200, 201, 202):
                raise Exception(
                    f"Chunk upload failed: {response.status_code} - {response.text}"
                )

            if response.status_code in (200, 201):
                result = response.json()

            start = end + 1

        return result
