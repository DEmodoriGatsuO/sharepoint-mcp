#!/usr/bin/env python
"""Script to check the contents of an access token"""

import os
import json
import base64
import msal
from dotenv import load_dotenv


def decode_jwt(token):
    """Decode JWT token and display contents"""
    try:
        # Get token parts (header.payload.signature)
        parts = token.split(".")
        if len(parts) != 3:
            print("❌ Invalid JWT token format")
            return None

        # Decode payload part (second part)
        # Add padding
        payload = parts[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)

        # Decode with Base64
        decoded = base64.b64decode(payload)
        claims = json.loads(decoded)

        return claims
    except Exception as e:
        print(f"❌ Error occurred while decoding token: {e}")
        return None


def get_and_analyze_token():
    """Get and analyze token"""
    print("=== Access Token Analysis ===")

    # Load environment variables
    load_dotenv()

    try:
        # Create MSAL client application
        tenant_id = os.getenv("TENANT_ID")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        if not all([tenant_id, client_id, client_secret]):
            print("❌ Required environment variables for authentication are not set")
            return False

        # Set up token cache
        cache = msal.SerializableTokenCache()

        # Create MSAL client application
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
            token_cache=cache,
        )

        # Get token
        print("Getting token...")
        scope = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            print(f"❌ Failed to get token: {result.get('error', 'unknown')}")
            return False

        token = result["access_token"]
        print("✅ Successfully obtained access token")

        # Analyze token
        print("\n--- Detailed Token Analysis ---")
        claims = decode_jwt(token)

        if not claims:
            return False

        # Display important information
        print("\nImportant claim information:")
        print(f"Issuer (iss): {claims.get('iss', 'Unknown')}")
        print(f"Audience (aud): {claims.get('aud', 'Unknown')}")
        print(f"App ID (appid): {claims.get('appid', 'Unknown')}")

        # Check for roles and scp (which can be related to the problem)
        roles = claims.get("roles", [])
        scp = claims.get("scp", "")

        print("\nPermission information:")
        if roles:
            print("✅ roles claim exists:")
            for role in roles:
                print(f"  - {role}")
        else:
            print("❌ roles claim does not exist")

        if scp:
            print("✅ scp claim exists:")
            print(f"  {scp}")
        else:
            print("❌ scp claim does not exist")

        # Validation related to error message cause
        if not roles and not scp:
            print("\n⚠️ Warning: Token contains neither roles nor scp")
            print(
                "   This is the cause of the 'Either scp or roles claim need to be present in the token' error"
            )
            print(
                "   Please set application permissions correctly in Azure AD and get admin consent"
            )

        # Display all claims (optional)
        print("\nAll claims:")
        print(json.dumps(claims, indent=2))

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    get_and_analyze_token()
