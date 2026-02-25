# SharePoint MCP Server - Usage Guide

> **DISCLAIMER**: This is an unofficial, community-developed project that is not affiliated with, endorsed by, or related to Microsoft Corporation. This documentation describes interaction with Microsoft services but is not approved by or associated with Microsoft.

This guide demonstrates how to use your SharePoint MCP server with Claude and other LLM applications.

## Setup

1. First, edit the `.env` file with your SharePoint connection details:
   - Get your tenant ID from the Azure Portal
   - Register an application in Azure AD to get client ID and secret
   - Set your SharePoint site URL 

2. Run the server:
   ```bash
   python src/server.py
   ```

3. For development and testing, use MCP Inspector:
   ```bash
   mcp dev src/server.py
   ```

4. To install in Claude Desktop:
   ```bash
   mcp install src/server.py --name "SharePoint Assistant"
   ```

## Available Resources

Access SharePoint content through these resource URIs:

1. Site Information:
   ```
   sharepoint://site-info
   ```

2. Document Library Contents:
   ```
   sharepoint://documents/{library_name}
   ```
   Example: `sharepoint://documents/Shared Documents`

3. List Data:
   ```
   sharepoint://list/{list_name}
   ```
   Example: `sharepoint://list/Tasks`

4. Document Content:
   ```
   sharepoint://document/{library_name}/{file_path}
   ```
   Example: `sharepoint://document/Shared Documents/report.docx`

## Available Tools

Your SharePoint MCP provides these tools to Claude:

### Basic Tools
1. `get_site_info()`: Get information about the current SharePoint site
   - Example: "What information do you have about my SharePoint site?"

2. `search_sharepoint(query: str)`: Search across your SharePoint site
   - Example: "Search for 'marketing campaign' in my SharePoint"

3. `list_document_libraries()`: Get all document libraries in the SharePoint site
   - Example: "Show me all the document libraries on my site"

### Content Creation and Management Tools

4. `create_sharepoint_site(display_name: str, alias: str, description: str)`: Create a new SharePoint site
   - Example: "Create a new SharePoint site called 'Marketing Team' with alias 'marketing'"

5. `create_intelligent_list(site_id: str, purpose: str, display_name: str)`: Create a list with AI-optimized schema
   - Example: "Create a 'projects' list called 'Marketing Projects' on my site"
   - Available purposes: projects, events, tasks, contacts, documents

6. `create_advanced_document_library(site_id: str, display_name: str, doc_type: str)`: Create a document library with optimized metadata
   - Example: "Create a document library for contracts called 'Legal Documents'"
   - Available types: general, contracts, marketing, reports, projects

7. `create_modern_page(site_id: str, name: str, purpose: str, audience: str)`: Create a modern SharePoint page
   - Example: "Create a welcome page called 'home' for our team"
   - Available purposes: welcome, dashboard, team, project, announcement
   - Available audiences: general, executives, team, customers

### Document Processing Tools

8. `get_document_content(site_id: str, drive_id: str, item_id: str, filename: str)`: Process document content
   - Example: "Process the content of 'quarterly-report.xlsx' from my Documents library"

## Example Prompts

Here are some examples of how to interact with the SharePoint MCP in Claude:

### Example 1: Browse Document Libraries
```
Can you tell me what documents are in the "Marketing Materials" library on my SharePoint site?
```

### Example 2: Search for Content
```
Can you search my SharePoint site for documents related to "quarterly revenue"?
```

### Example 3: Get List Items
```
Show me all the items in the "Tasks" list on my SharePoint site.
```

### Example 4: Create a New Task
```
Please create a new task in the "Tasks" list with the title "Prepare monthly report" and status "Not Started".
```

### Example 5: Analyze a Document
```
Can you download and analyze the "sales_data.xlsx" file from my "Reports" document library?
```

### Example 6: Create a New SharePoint Site
```
Can you create a new SharePoint site for our Marketing team with the alias "marketing"?
```

### Example 7: Create an Intelligent List
```
Please create a "Projects" list in our SharePoint site that includes fields for status, priority, and due dates.
```

### Example 8: Create a Modern Page with AI-Generated Content
```
Can you create a welcome page called "home" on our site for our team that includes project updates and key resources?
```

### Example 9: Create a Document Library with Metadata
```
Please create a "Contracts" document library on our SharePoint site that includes appropriate metadata fields like contract type, expiration date, and status.
```

### Example 10: Process Document Content and Generate Insights
```
Can you analyze the contents of the "sales_data.xlsx" file from my Reports library and summarize the key trends?
```

## Advanced Usage

### Combining Actions for Complete Workflows

Here's an example of a workflow that combines multiple actions:

```
I need to set up a new project area in SharePoint. Could you:
1. Create a new project site called "Product Launch" with alias "productlaunch"
2. Add a project tasks list with appropriate fields
3. Create a document library for project documents with metadata
4. Create a welcome page that introduces the project purpose
```

### Using Site IDs

Many tools require a site ID. You can get this by first calling `get_site_info()`:

```
First, get information about my SharePoint site, then use the site ID to create a new list for tracking projects.
```

### Document Processing Capabilities

The document processing tool can handle:

- **CSV/Excel**: Data preview, column analysis, basic statistics
- **Word**: Extract text, tables, document structure, and metadata
- **PDF**: Extract text, metadata, and form fields
- **Text/Markdown/HTML**: Process and analyze textual content

For example:
```
Please analyze the "financial_report.xlsx" document and tell me which sheets it contains and what data is in each.
```

## Troubleshooting

If you encounter issues using the SharePoint MCP:

1. Run the `auth-diagnostic.py` script to check your authentication setup
2. Ensure your application has all the required permissions in Azure AD
3. Check if your SharePoint site URL is correctly specified in the `.env` file
4. Look at the server logs for more detailed error information

For more information, refer to the documentation in the `docs` directory.