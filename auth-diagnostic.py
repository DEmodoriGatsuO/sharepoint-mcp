#!/usr/bin/env python
"""SharePoint authentication diagnostic script"""

import os
import sys
import json
import uuid
import requests
from dotenv import load_dotenv


def run_auth_diagnostic():
    """Execute SharePoint authentication diagnostic"""
    print("=== SharePoint Authentication Diagnostic ===")

    # Check for .env file
    if not os.path.exists(".env"):
        print("❌ Error: .env file not found")
        print("   Please copy .env.example and configure it")
        return False

    # Load environment variables
    load_dotenv()

    # Check required variables
    required_vars = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET", "SITE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(
            f"❌ Error: The following environment variables are not set: {', '.join(missing_vars)}"
        )
        return False

    print("✅ All required environment variables are set")

    # Check SharePoint site URL format
    site_url = os.getenv("SITE_URL")
    if (
        not site_url.startswith("https://")
        or ".sharepoint.com/" not in site_url.lower()
    ):
        print(f"❌ Error: Invalid SharePoint site URL: {site_url}")
        print(
            "   URL must be in the format: https://your-tenant.sharepoint.com/sites/your-site"
        )
        return False

    print(f"✅ SharePoint site URL format is valid: {site_url}")

    # Test authentication
    print("\n--- Testing Authentication and Requests ---")

    try:
        import msal

        # Set up token cache
        cache = msal.SerializableTokenCache()

        # Create MSAL client application
        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        print(f"Tenant ID: {tenant_id[:5]}...{tenant_id[-5:]}")
        print(f"Client ID: {client_id[:5]}...{client_id[-5:]}")

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
            token_cache=cache,
        )

        # Try client credential flow
        print("Attempting client credential flow with Microsoft Entra ID...")
        scope = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            error_code = result.get("error", "unknown")
            error_description = result.get("error_description", "Unknown error")
            print(
                f"❌ Error: Authentication failed: {error_code} - {error_description}"
            )

            # Detailed explanations for common errors
            if "AADSTS700016" in str(error_description):
                print("   Application not found or is disabled for the tenant")
                print(
                    "   Please check your application registration in Microsoft Entra ID"
                )
            elif "AADSTS7000215" in str(error_description):
                print("   Invalid client secret")
                print("   Check if your client secret is correct and not expired")
            elif "AADSTS650057" in str(error_description):
                print("   Invalid client credentials")
                print("   Check your client ID and client secret")
            elif "AADSTS70011" in str(error_description):
                print("   Application was not found in the tenant")
                print("   Make sure the application is registered in this tenant")

            print(f"\nFull error response: \n{json.dumps(result, indent=2)}")
            return False

        print("✅ Successfully obtained access token")

        # Try accessing SharePoint site
        print("Attempting to access SharePoint site...")

        headers = {
            "Authorization": f"Bearer {result['access_token']}",
            "Content-Type": "application/json",
        }

        # Extract domain and site name from site URL
        site_parts = site_url.replace("https://", "").split("/")
        domain = site_parts[0]
        site_name = site_parts[2] if len(site_parts) > 2 else "root"

        print(f"Domain: {domain}, Site: {site_name}")

        graph_url = (
            f"https://graph.microsoft.com/v1.0/sites/{domain}:/sites/{site_name}"
        )
        print(f"Request: {graph_url}")

        response = requests.get(graph_url, headers=headers)

        if response.status_code != 200:
            print(
                f"❌ Error: Failed to access SharePoint site: HTTP {response.status_code}"
            )
            print(f"Response: {response.text}")

            if response.status_code == 404:
                print("   Specified site not found")
                print("   Please check that your site URL is correct")
            elif response.status_code == 401:
                print("   No access permission")
                print(
                    "   Please check that your application has been granted appropriate permissions"
                )
                print(
                    "   Permissions such as Sites.Read.All, Files.Read.All are required"
                )

            return False

        site_info = response.json()
        print("✅ Successfully accessed SharePoint site")
        print(f"Site name: {site_info.get('displayName', 'Unknown')}")
        print(f"Site ID: {site_info.get('id', 'Unknown')}")

        # Try listing document libraries
        print("\nAttempting to list document libraries...")

        drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_info['id']}/drives"
        response = requests.get(drives_url, headers=headers)

        if response.status_code != 200:
            print(
                f"❌ Error: Failed to list document libraries: HTTP {response.status_code}"
            )
            print(f"Response: {response.text}")
        else:
            drives = response.json().get("value", [])
            print(f"✅ Successfully listed {len(drives)} document libraries")
            for drive in drives:
                print(f"  - {drive.get('name', 'Unknown')}")

        # Test write permissions
        print("\n--- Testing Write Permissions ---")
        try:
            # Try to create a test list
            test_list_name = f"TestList_{uuid.uuid4().hex[:8]}"

            create_list_url = (
                f"https://graph.microsoft.com/v1.0/sites/{site_info['id']}/lists"
            )
            create_list_data = {
                "displayName": test_list_name,
                "list": {"template": "genericList"},
                "description": "Test list created by diagnostic tool",
            }

            print(f"Attempting to create test list: {test_list_name}")
            create_response = requests.post(
                create_list_url, headers=headers, json=create_list_data
            )

            if create_response.status_code in (201, 200):
                print(
                    "✅ Successfully created a test list - write permissions confirmed"
                )

                # Clean up - delete test list
                list_id = create_response.json().get("id")
                delete_url = f"https://graph.microsoft.com/v1.0/sites/{site_info['id']}/lists/{list_id}"
                delete_response = requests.delete(delete_url, headers=headers)

                if delete_response.status_code in (204, 200):
                    print("✅ Test list deleted successfully")
                else:
                    print(
                        f"⚠️ Warning: Could not delete test list: {delete_response.status_code}"
                    )
            else:
                print(f"❌ Failed to create test list: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                print("   You may not have sufficient write permissions")
                print(
                    "   Check that your application has Sites.ReadWrite.All permission"
                )
                print(
                    "   For creating sites, you also need Sites.Manage.All permission"
                )
        except Exception as e:
            print(f"❌ Error during write permission test: {str(e)}")

        # Check application permissions
        print("\n--- Checking Application Permissions ---")
        try:
            # Decode token to check permissions
            token = result["access_token"]
            token_parts = token.split(".")
            if len(token_parts) >= 2:
                # Add padding
                payload = token_parts[1]
                payload += "=" * ((4 - len(payload) % 4) % 4)

                # Decode
                import base64

                decoded = base64.b64decode(payload)
                claims = json.loads(decoded)

                # Check roles
                roles = claims.get("roles", [])

                if roles:
                    print("Found the following roles in token:")
                    for role in roles:
                        print(f"  - {role}")

                    # Check for specific permissions
                    required_permissions = [
                        "Sites.Read.All",
                        "Sites.ReadWrite.All",
                        "Files.ReadWrite.All",
                        "Sites.Manage.All",
                    ]

                    missing_permissions = [
                        p
                        for p in required_permissions
                        if not any(p in r for r in roles)
                    ]

                    if missing_permissions:
                        print(
                            "\n⚠️ Warning: The following permissions are recommended but not found:"
                        )
                        for p in missing_permissions:
                            print(f"  - {p}")
                        print("   Some operations may fail without these permissions")
                    else:
                        print("\n✅ All required permissions are present in the token")
                else:
                    print(
                        "❌ No roles found in token - check application permissions in Microsoft Entra ID"
                    )
            else:
                print("⚠️ Could not decode token to check permissions")
        except Exception as e:
            print(f"⚠️ Error checking permissions: {str(e)}")

    except Exception as e:
        print(f"❌ Error: Exception during diagnostic: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    print("\n✅ Authentication diagnostic completed successfully")
    return True


if __name__ == "__main__":
    try:
        result = run_auth_diagnostic()
        if not result:
            print("\n❌ Authentication diagnostic failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: An error occurred during diagnostic execution: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
