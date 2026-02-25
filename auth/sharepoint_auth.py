"""SharePoint authentication handler module."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import logging

import msal
import requests
from config.settings import SHAREPOINT_CONFIG, TOKEN_CACHE_FILE

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sharepoint_auth")


@dataclass
class SharePointContext:
    """Context object for SharePoint connection."""

    access_token: str
    token_expiry: datetime
    graph_url: str = "https://graph.microsoft.com/v1.0"

    @property
    def headers(self) -> dict[str, str]:
        """Get authorization headers for API calls."""
        # ヘッダーの内容をログに出力（トークンは一部のみ表示）
        token_preview = (
            f"{self.access_token[:10]}...{self.access_token[-10:]}"
            if self.access_token
            else "None"
        )
        logger.debug(f"Using token (preview): {token_preview}")

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def is_token_valid(self) -> bool:
        """Check if the access token is still valid."""
        # Add safety check to handle None expiry
        if not self.token_expiry:
            return False
        is_valid = datetime.now() < self.token_expiry
        logger.debug(f"Token valid: {is_valid}, Expires: {self.token_expiry}")
        return is_valid

    def test_connection(self) -> bool:
        """Test the connection to SharePoint."""
        try:
            # Extract site domain and name from site URL
            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"

            # Get site information via Microsoft Graph API
            # For root site, use different endpoint format
            if site_name == "root" or not site_name:
                site_url = f"{self.graph_url}/sites/{domain}:"
            else:
                site_url = f"{self.graph_url}/sites/{domain}:/sites/{site_name}"
            logger.debug(f"Testing connection to: {site_url}")

            response = requests.get(site_url, headers=self.headers)

            if response.status_code != 200:
                logger.error(
                    f"Connection test failed: HTTP {response.status_code} - {response.text}"
                )
                return False

            logger.info(f"Connection test successful: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Error during connection test: {e}")
            return False

    def test_write_permissions(self) -> bool:
        """Test if the current token has write permissions."""
        try:
            logger.debug("Testing write permissions...")

            # Extract site domain and name from site URL
            site_parts = (
                SHAREPOINT_CONFIG["site_url"].replace("https://", "").split("/")
            )
            domain = site_parts[0]
            site_name = site_parts[2] if len(site_parts) > 2 else "root"

            # First get site ID
            # For root site, use different endpoint format
            if site_name == "root" or not site_name:
                site_url = f"{self.graph_url}/sites/{domain}:"
            else:
                site_url = f"{self.graph_url}/sites/{domain}:/sites/{site_name}"
            response = requests.get(site_url, headers=self.headers)

            if response.status_code != 200:
                logger.error(
                    f"Failed to get site ID: {response.status_code} - {response.text}"
                )
                return False

            site_id = response.json().get("id")
            if not site_id:
                logger.error("Site ID not found in response")
                return False

            # Try to create a simple folder in a document library
            # First, get document libraries
            drives_url = f"{self.graph_url}/sites/{site_id}/drives"
            response = requests.get(drives_url, headers=self.headers)

            if response.status_code != 200:
                logger.error(
                    f"Failed to get document libraries: {response.status_code} - {response.text}"
                )
                return False

            drives = response.json().get("value", [])
            if not drives:
                logger.error("No document libraries found")
                return False

            # Try to create a test folder in the first document library
            drive_id = drives[0].get("id")
            folder_url = (
                f"{self.graph_url}/sites/{site_id}/drives/{drive_id}/root/children"
            )

            test_folder_name = f"test-folder-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            folder_data = {
                "name": test_folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename",
            }

            response = requests.post(folder_url, headers=self.headers, json=folder_data)

            if response.status_code not in (200, 201):
                logger.error(
                    f"Failed to create test folder: {response.status_code} - {response.text}"
                )
                if response.status_code == 401 or response.status_code == 403:
                    logger.error("Insufficient permissions for write operations")
                return False

            logger.info(f"Write permission test successful: {response.status_code}")

            # Try to delete the test folder
            folder_id = response.json().get("id")
            delete_url = (
                f"{self.graph_url}/sites/{site_id}/drives/{drive_id}/items/{folder_id}"
            )

            delete_response = requests.delete(delete_url, headers=self.headers)
            if delete_response.status_code not in (200, 204):
                logger.warning(
                    f"Could not delete test folder: {delete_response.status_code}"
                )
            else:
                logger.info("Test folder deleted successfully")

            return True

        except Exception as e:
            logger.error(f"Error during write permission test: {e}")
            return False

    def decode_and_log_token_permissions(self) -> None:
        """Decode token and log the permissions it contains."""
        try:
            import base64

            # Split token into parts
            token_parts = self.access_token.split(".")
            if len(token_parts) < 2:
                logger.error("Invalid token format")
                return

            # Decode the payload (second part)
            payload = token_parts[1]
            # Add padding if necessary
            payload += "=" * ((4 - len(payload) % 4) % 4)
            decoded = base64.b64decode(payload)
            claims = json.loads(decoded)

            # Log token information
            logger.info("Token information:")
            logger.info(f"Token expires: {claims.get('exp', 'unknown')}")
            logger.info(f"Token issued: {claims.get('iat', 'unknown')}")
            logger.info(f"Token issuer: {claims.get('iss', 'unknown')}")

            # Check for roles (app permissions) or scp (delegated permissions)
            roles = claims.get("roles", [])
            scp = claims.get("scp", "")

            if roles:
                logger.info("Application permissions (roles):")
                for role in roles:
                    logger.info(f"  - {role}")

                # Check for write permissions
                write_permissions = [
                    p for p in roles if "ReadWrite" in p or "Manage" in p
                ]
                if write_permissions:
                    logger.info("Write permissions found:")
                    for p in write_permissions:
                        logger.info(f"  - {p}")
                else:
                    logger.warning("No write permissions found in token")

            if scp:
                logger.info(f"Delegated permissions (scp): {scp}")

            if not roles and not scp:
                logger.error(
                    "No roles or scp claims found in token - operations will likely fail"
                )

        except Exception as e:
            logger.error(f"Error decoding token: {e}")


def validate_config() -> None:
    """Validate SharePoint configuration."""
    missing_vars = []
    for key in ["tenant_id", "client_id", "client_secret", "site_url"]:
        if not SHAREPOINT_CONFIG.get(key):
            missing_vars.append(key)

    if missing_vars:
        error_msg = f"Missing required configuration: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Validate site URL format
    site_url = SHAREPOINT_CONFIG["site_url"]
    if not site_url.startswith("https://") or ".sharepoint.com" not in site_url.lower():
        logger.error(f"Invalid SharePoint site URL: {site_url}")
        raise ValueError(f"Invalid SharePoint site URL: {site_url}")


async def get_auth_context() -> SharePointContext:
    """Get SharePoint authentication context."""
    # Validate configuration first
    validate_config()

    # Set up token cache
    cache = msal.SerializableTokenCache()

    # Load existing cache file if it exists
    if os.path.exists(TOKEN_CACHE_FILE):
        try:
            with open(TOKEN_CACHE_FILE, "r") as cache_file:
                cache.deserialize(cache_file.read())
            logger.info("Loaded token cache from file")

            # Check if cache has a valid token
            accounts = cache.find(msal.TokenCache.CredentialType.REFRESH_TOKEN)
            if accounts:
                logger.info("Found refresh token in cache, attempting to use it")
        except Exception as e:
            logger.warning(f"Error loading token cache: {e}")

    # Create MSAL client application
    app = msal.ConfidentialClientApplication(
        SHAREPOINT_CONFIG["client_id"],
        authority=f"https://login.microsoftonline.com/{SHAREPOINT_CONFIG['tenant_id']}",
        client_credential=SHAREPOINT_CONFIG["client_secret"],
        token_cache=cache,
    )

    # First try to get token silently from cache
    result = None
    accounts = app.get_accounts()
    if accounts:
        logger.info("Account found in cache, attempting silent token acquisition")
        result = app.acquire_token_silent(
            SHAREPOINT_CONFIG["scope"], account=accounts[0]
        )

    # If silent token acquisition fails, get new token
    if not result:
        logger.info(
            "No token in cache or silent acquisition failed, acquiring new token"
        )
        result = app.acquire_token_for_client(scopes=SHAREPOINT_CONFIG["scope"])

    # Raise error if token acquisition fails
    if "access_token" not in result:
        error_code = result.get("error", "unknown")
        error_description = result.get("error_description", "Unknown error")
        logger.error(f"Authentication failed: {error_code} - {error_description}")

        # Log more detailed error information for troubleshooting
        if "AADSTS" in error_description:
            if "AADSTS50034" in error_description:
                logger.error("User account doesn't exist or is invalid")
            elif "AADSTS50126" in error_description:
                logger.error("Invalid username or password")
            elif "AADSTS65001" in error_description:
                logger.error("Application does not have the required permissions")
            elif "AADSTS70011" in error_description:
                logger.error(
                    "Application specified in the request is not found in the tenant"
                )

        raise Exception(f"Authentication failed: {error_code} - {error_description}")

    # Log a preview of the token (for security, only partial token is shown)
    token_preview = f"{result['access_token'][:10]}...{result['access_token'][-10:]}"
    logger.info(f"Token acquired successfully: {token_preview}")

    # Save token cache
    try:
        with open(TOKEN_CACHE_FILE, "w") as cache_file:
            cache_file.write(cache.serialize())
        logger.info("Token cache saved to file")
    except Exception as e:
        logger.warning(f"Error saving token cache: {e}")

    # Calculate token expiry (default is 1 hour)
    expiry = datetime.now() + timedelta(seconds=result.get("expires_in", 3600))
    logger.info(f"Authentication successful, token expires at {expiry}")

    # Return auth context
    context = SharePointContext(
        access_token=result["access_token"], token_expiry=expiry
    )

    # Decode and log token permissions
    context.decode_and_log_token_permissions()

    # Test connection immediately
    logger.info("Testing connection with acquired token...")
    if not context.test_connection():
        logger.warning("Connection test failed, but continuing anyway...")

    # Test write permissions
    logger.info("Testing write permissions...")
    if not context.test_write_permissions():
        logger.warning("Write permission test failed. Some operations may not work.")
    else:
        logger.info("Write permission test successful. Token has write permissions.")

    return context


async def refresh_token_if_needed(context: SharePointContext) -> None:
    """Refresh token if needed."""
    if not context.is_token_valid():
        logger.info("Token expired, refreshing...")
        try:
            # Re-authenticate to get a new token
            new_context = await get_auth_context()

            # Update the context
            context.access_token = new_context.access_token
            context.token_expiry = new_context.token_expiry
            logger.info("Token refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
