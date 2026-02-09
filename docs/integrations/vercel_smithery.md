# Deploy to Vercel and Publish on Smithery

This guide walks you through deploying the UML-MCP server to Vercel and publishing it on Smithery so users can connect via **Streamable HTTP** without installing anything.

## 1. Deploy to Vercel

### Prerequisites

- A [Vercel](https://vercel.com) account
- This repo connected to Vercel (GitHub/GitLab/Bitbucket)

### Deploy

1. **Connect the repo** in the [Vercel dashboard](https://vercel.com/new): Import your `uml-mcp` repository.
2. **Build settings** (usually auto-detected from `vercel.json`):
   - Framework: Other
   - Build Command: `pip install -r requirements.txt -r requirements-dev.txt`
   - Output: handled by `vercel.json`
3. **Deploy** and wait for the build to finish.

Your app will be available at:

- **Production**: `https://<your-project>.vercel.app`
- **REST API**: `https://<your-project>.vercel.app/` (root, `/health`, `/generate_diagram`, etc.)
- **MCP endpoint**: `https://<your-project>.vercel.app/mcp`

Use the **MCP URL** when publishing to Smithery.

## 2. Publish on Smithery

Smithery can list your server so users can add it with one click. You can either **host the server on Smithery** (Docker/stdio) or **point Smithery to your Vercel URL** (self-hosted HTTP).

### Option A: Self-hosted (Vercel URL)

1. Go to [smithery.ai/new](https://smithery.ai/new).
2. Sign in if needed.
3. Choose **Publish a self-hosted server** (or equivalent “external” / “URL” flow).
4. Fill in:
   - **Namespace**: your Smithery username (e.g. `antoinebou12`)
   - **Server ID**: short slug (e.g. `uml`)
   - **MCP Server URL**: `https://<your-project>.vercel.app/mcp`  
     Replace `<your-project>` with your actual Vercel project URL.
5. Submit. Smithery will use your server’s Streamable HTTP transport and may scan metadata from `/.well-known/mcp/server-card.json` if needed.

After publishing, your server will appear at:

`https://smithery.ai/server/@<namespace>/<server-id>`

Example: `https://smithery.ai/server/@antoinebou12/uml`

### Option B: Smithery-hosted (Docker)

If you prefer Smithery to run the server (Docker/stdio), use the existing `smithery.yaml` and deploy via Smithery’s Docker flow. The server will be hosted by Smithery; no Vercel URL is required.

## 3. Connect from a client

Once the server is on Smithery (or you have the Vercel URL), configure your MCP client with the **Streamable HTTP** URL:

- **From Smithery**: Use the “Add to Cursor” (or similar) button on the server page, or copy the URL Smithery shows.
- **Direct**: In Cursor (or another client), set the MCP server URL to:
  `https://<your-project>.vercel.app/mcp`

Example Cursor config (`.cursor/mcp.json` or project MCP settings):

```json
{
  "mcpServers": {
    "uml": {
      "url": "https://<your-project>.vercel.app/mcp"
    }
  }
}
```

Replace `<your-project>` with your real Vercel URL.

## Troubleshooting

- **502 / timeout**: Vercel serverless functions have a max duration (e.g. 60s on Hobby). Long-running tool calls may hit this; consider optimizing or using Smithery-hosted Docker for heavy use.
- **MCP at /mcp**: Ensure you use the path `/mcp` (e.g. `https://...vercel.app/mcp`), not the root URL.
- **CORS**: The app allows all origins for API and MCP; restrict in production if needed.
