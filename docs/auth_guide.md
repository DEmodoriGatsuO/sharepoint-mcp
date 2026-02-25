# SharePoint MCP Authentication Setup Guide

> **DISCLAIMER**: This is an unofficial, community-developed project that is not affiliated with, endorsed by, or related to Microsoft Corporation. This documentation describes interaction with Microsoft services but is not approved by or associated with Microsoft.

To connect your MCP server to SharePoint, you need to set up authentication with Microsoft Azure AD. Follow these steps:

## Step 1: Register an Application in Azure AD

1. Sign in to the [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Enter a name for your application (e.g., "SharePoint MCP Client")
4. Set the supported account type to "Accounts in this organizational directory only"
5. Click **Register**

## Step 2: Get the Application ID and Tenant ID

1. Once your app is registered, note the **Application (client) ID** - this is your `client_id`
2. Also note the **Directory (tenant) ID** - this is your `tenant_id`

## Step 3: Create a Client Secret

1. Navigate to **Certificates & secrets** → **Client secrets** → **New client secret**
2. Enter a description and select an expiration period
3. Click **Add**
4. **IMPORTANT**: Copy the **Value** of the secret immediately - this is your `client_secret`
   (You won't be able to see it again after leaving the page)

## Step 4: Configure API Permissions

For the Microsoft Graph API, add these permissions:

1. Navigate to **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions**
2. Add the following permissions:
   - `Sites.Read.All` - Read files in all site collections
   - `Sites.ReadWrite.All` - Read and write items in all site collections
   - `Sites.Manage.All` - Create new sites and manage site collections
   - `Files.Read.All` - Read files in all site collections
   - `Files.ReadWrite.All` - Read and write files in all site collections
   - `User.Read.All` - Read all users' profiles
3. Click **Add permissions**
4. Click **Grant admin consent for [Your Organization]**

> **NOTE**: The `Sites.Manage.All` permission is required for creating sites. If you don't need this functionality, you can omit this permission.

## Step 5: Update Your Configuration

Update your `.env` file with the values you obtained:

```
TENANT_ID=your_tenant_id_from_step_2
CLIENT_ID=your_client_id_from_step_2
CLIENT_SECRET=your_client_secret_from_step_3
SITE_URL=https://your-tenant.sharepoint.com/sites/your-site
USERNAME=your.email@example.com  # Only needed for user-delegated auth
PASSWORD=your_password           # Only needed for user-delegated auth
```

## Alternative Authentication Methods

### Certificate-Based Authentication (Recommended for Production)

For more secure authentication in production environments, use certificate-based authentication:

1. Generate a self-signed certificate:
   ```bash
   openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
   ```

2. Upload the certificate to your Azure AD application:
   - Go to your app registration in Azure Portal
   - Navigate to **Certificates & secrets** → **Certificates** → **Upload certificate**
   - Upload the certificate.pem file

3. Use certificate authentication in your code:
   ```python
   import msal
   
   # Read certificate
   with open('key.pem', 'rb') as cert_file:
       private_key = cert_file.read()
   
   with open('certificate.pem', 'rb') as cert_file:
       public_certificate = cert_file.read()
   
   # Create client application
   app = msal.ConfidentialClientApplication(
       CONFIG["client_id"],
       authority=f"https://login.microsoftonline.com/{CONFIG['tenant_id']}",
       client_credential={
           'private_key': private_key,
           'thumbprint': 'your-certificate-thumbprint',  # From Azure Portal
           'public_certificate': public_certificate
       }
   )
   ```

## Permission Explanations

Here's a breakdown of what each permission allows:

- **Sites.Read.All**: Allows reading properties and items of all SharePoint sites
- **Sites.ReadWrite.All**: Allows reading and writing properties and items of all SharePoint sites
- **Sites.Manage.All**: Allows full control of all site collections (required for site creation)
- **Files.Read.All**: Allows reading files in all site collections
- **Files.ReadWrite.All**: Allows reading, creating, updating and deleting files in all site collections
- **User.Read.All**: Allows reading user profiles (useful for people-related fields)

## Verifying Permissions

To verify that your application has the correct permissions:

1. Run the `auth-diagnostic.py` script included in this project
2. Look for the "Checking Application Permissions" section in the output
3. Verify that all required permissions are listed

## Troubleshooting

If you encounter authorization errors:

1. Make sure you've granted admin consent for all required permissions
2. Check that your tenant ID and client ID are correct
3. Ensure your client secret hasn't expired
4. Verify that your SharePoint site URL is correct and accessible to the account
5. For specific Microsoft Graph API errors, consult the [Microsoft Graph documentation](https://docs.microsoft.com/en-us/graph/errors)

### Common Permission-Related Errors

- **Access denied due to insufficient privileges**: Your application lacks the required permissions. Ensure you've granted all required permissions and admin consent has been provided.
- **Either scp or roles claim need to be present in the token**: Your application is not correctly configured for application permissions. Check that admin consent was provided.
- **Access to the specified resource is forbidden**: The application has authentication but lacks authorization for the specific resource. Check site-specific permissions.
- **Resource not found**: The SharePoint site or resource doesn't exist or your application doesn't have permission to see it.