# Deploy to Vercel and Publish on Smithery

This guide walks you through deploying the UML-MCP server to Vercel and publishing it on Smithery so users can connect via **Streamable HTTP** without installing anything. For the full Smithery docs index, see [smithery.ai/docs/llms.txt](https://smithery.ai/docs/llms.txt).

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

### Option A: URL (bring your own hosting)

1. Go to [smithery.ai/new](https://smithery.ai/new).
2. Sign in if needed.
3. Choose **URL** (bring your own hosting).
4. Fill in:
   - **Namespace**: your Smithery username (e.g. `antoinebou12`)
   - **Server ID**: short slug (e.g. `uml`)
   - **MCP Server URL**: `https://<your-project>.vercel.app/mcp`  
     Replace `<your-project>` with your actual Vercel project URL. Use the **root** deployment URL (e.g. `https://uml-xxx.vercel.app`), not a path; the MCP endpoint is at `/mcp`.
5. Submit. Smithery will use your server’s Streamable HTTP transport and will fetch metadata from `https://<your-project>.vercel.app/.well-known/mcp/server-card.json` when automatic scanning is not possible.

**Config schema (recommended):** To remove the “No config schema provided” warning and let users set options (output dir, Kroki URL, etc.) in Smithery’s UI, publish (or re-publish) via the CLI and pass the config schema:

```bash
# Use file path (works on Bash, PowerShell, etc.)
npx @smithery/cli publish --name @your-org/uml-mcp --url https://<your-project>.vercel.app/mcp --config-schema smithery-config-schema.json
```

On **PowerShell**, use the same command. Do not use `(Get-Content smithery-config-schema.json -Raw)` — that corrupts the JSON when passed to the CLI.

See [Smithery Session Configuration](https://smithery.ai/docs/build/session-config) for schema format with `x-from` extension.

After publishing, your server will appear at:

`https://smithery.ai/server/@<namespace>/<server-id>`

Example: `https://smithery.ai/server/@antoinebou12/uml`

### Option B: Hosted (Smithery hosts it)

**Note:** Hosted deployment is in private early access — [contact Smithery](mailto:support@smithery.ai) if interested.

If you use Smithery-hosted deployment, the existing `smithery.yaml` defines the server. Connect your GitHub repo and deploy via the Deployments tab, or run `npx @smithery/cli deploy --name @your-org/uml-mcp`. The `smithery.yaml` includes a [Session Configuration](https://smithery.ai/docs/build/session-config) schema for output directory, Kroki URL, log level, and other settings.

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

### HTTP 401 / "Invalid OAuth error response" when connecting via Smithery

If Smithery shows a connection error like `HTTP 401: Invalid OAuth error response: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON`, the gateway is hitting **Vercel Deployment Protection**: Vercel returns an HTML login page instead of JSON, so the MCP handshake fails.

**Fix (choose one):**

1. **Disable Deployment Protection (recommended for public MCP)**  
   In the [Vercel project](https://vercel.com/dashboard) → **Settings** → **Deployment Protection**, turn off protection for Production and/or Preview so your app URL is publicly reachable. Then use the normal MCP URL in Smithery: `https://<your-project>.vercel.app/mcp`.

2. **Keep protection and use a bypass token**  
   If you want to keep protection, use Vercel’s [Protection Bypass for automation](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation). Get the bypass token from the project’s Deployment Protection settings, then in Smithery set **MCP Server URL** to:
   ```
   https://<your-project>.vercel.app/mcp?x-vercel-set-bypass-cookie=true&x-vercel-protection-bypass=YOUR_BYPASS_TOKEN
   ```
   Replace `YOUR_BYPASS_TOKEN` with the token from Vercel.

### Connection error: Initialization failed with status 405 / “advertise server-card”

Smithery discovers your server by requesting `/.well-known/mcp/server-card.json` on the **root** of your deployment (e.g. `https://<your-project>.vercel.app/.well-known/mcp/server-card.json`). If that request fails (e.g. 404 or 405), you get “Your server could not be automatically scanned” and “Please advertise a /.well-known/mcp/server-card.json”.

**Fix:** This repo serves the server card from the FastAPI app. Ensure `vercel.json` does **not** serve `/.well-known/*` as static files so that the request reaches the app. The repo’s `vercel.json` is set up so that `/.well-known/mcp/server-card.json` is handled by the Python app. After redeploying, open `https://<your-project>.vercel.app/.well-known/mcp/server-card.json` in a browser; you should see JSON with `serverInfo` and `tools`. If you see 404/405, check Vercel routes and that the latest `vercel.json` is deployed.

### Other issues

- **502 / timeout**: Vercel serverless functions have a max duration (e.g. 60s on Hobby). Long-running tool calls may hit this; consider optimizing or using Smithery-hosted Docker for heavy use.
- **MCP at /mcp**: Ensure you use the path `/mcp` (e.g. `https://...vercel.app/mcp`), not the root URL.
- **CORS**: The app allows all origins for API and MCP; restrict in production if needed.
