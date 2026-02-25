#!/usr/bin/env python
"""Utility script to check SharePoint MCP configuration."""

import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv


def check_config():
    """Check configuration and report any issues."""
    print("=== SharePoint MCP Configuration Checker ===")

    # Check .env file
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if not env_path.exists():
        print("❌ ERROR: .env file not found!")
        if env_example_path.exists():
            print(
                "   Create an .env file from .env.example and fill in your credentials."
            )
        return False

    # Load environment variables
    load_dotenv()

    # Check required variables
    required_vars = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET", "SITE_URL"]

    optional_vars = ["USERNAME", "PASSWORD", "DEBUG"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(
            f"❌ ERROR: Missing required environment variables: {', '.join(missing_vars)}"
        )
        return False

    print("✅ All required environment variables are set")

    # Check optional variables
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_optional:
        print(
            f"⚠️ WARNING: Missing optional environment variables: {', '.join(missing_optional)}"
        )
        if "USERNAME" in missing_optional or "PASSWORD" in missing_optional:
            print(
                "   Note: USERNAME and PASSWORD are needed for user-delegated authentication"
            )

    # Check site URL format
    site_url = os.getenv("SITE_URL")
    if (
        not site_url.startswith("https://")
        or ".sharepoint.com/" not in site_url.lower()
    ):
        print(f"❌ ERROR: Invalid SharePoint site URL: {site_url}")
        print(
            "   URL should be in format: https://your-tenant.sharepoint.com/sites/your-site"
        )
        return False

    print(f"✅ SharePoint site URL format is valid: {site_url}")

    # Check for token cache
    token_cache = Path(".token_cache")
    if token_cache.exists():
        print("✅ Token cache file exists")
        try:
            with open(token_cache, "r") as f:
                cache_data = json.loads(f.read())
            if not cache_data.get("AccessToken"):
                print("⚠️ WARNING: Token cache exists but no access token found")
        except Exception as e:
            print(f"⚠️ WARNING: Error reading token cache: {e}")
    else:
        print("ℹ️ No token cache found - will be created on first authentication")

    # Check permissions in site URL
    try:
        from urllib.parse import urlparse

        parsed_url = urlparse(site_url)
        path_parts = parsed_url.path.strip("/").split("/")

        if len(path_parts) < 2 or path_parts[0].lower() != "sites":
            print(
                "⚠️ WARNING: Site URL path should typically be in format: /sites/your-site-name"
            )
    except Exception:
        pass

    # Final check
    print("\n--- Configuration Summary ---")
    print(f"🔹 Tenant ID: {os.getenv('TENANT_ID')[:5]}...{os.getenv('TENANT_ID')[-5:]}")
    print(f"🔹 Client ID: {os.getenv('CLIENT_ID')[:5]}...{os.getenv('CLIENT_ID')[-5:]}")
    print(f"🔹 Client Secret: {'*' * 10}")
    print(f"🔹 Site URL: {site_url}")
    print(f"🔹 Debug Mode: {os.getenv('DEBUG', 'False')}")

    if os.getenv("USERNAME"):
        print(f"🔹 Username: {os.getenv('USERNAME')}")

    print("\n✅ Configuration check completed")
    return True


if __name__ == "__main__":
    try:
        result = check_config()
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR during configuration check: {e}")
        sys.exit(1)
