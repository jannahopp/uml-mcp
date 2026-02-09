# Deploy to Vercel and Publish on Smithery

This guide walks you through deploying the UML-MCP server to Vercel and publishing it on Smithery so users can connect via **Streamable HTTP** without installing anything. For the full Smithery docs index, see [smithery.ai/docs/llms.txt](https://smithery.ai/docs/llms.txt.

## 1. Deploy to Vercel

### Prerequisites

- A [Vercel](https://vercel.com) account
- This repo connected to Vercel (GitHub/GitLab/Bitbucket)

### Deploy

1. **Connect the repo** in the [Vercel dashboard](https://vercel.com/new): Import your `uml-mcp` repository.
2. **Build settings** (usually auto-detected from `vercel.json`):
   - Framework: Other
   - Build Command: `pip install -r requirements.txt -r requirements-dev.txt && python scripts/generate_server_card.py`
   - Output: handled by `vercel.json`
3. **Deploy** and wait for the build to finish.

Your app will be available at:

- **Production**: `https://<your-project>.vercel.app`
- **REST API**: `https://<your-project>.vercel.app/` (root, `/health`, `/generate_diagram`, etc.)
- **MCP endpoint**: `https://<your-project>.vercel.app/mcp`

Use the **MCP URL** when publishing to Smithery.

## 2. Publish on Smithery

Smithery can list your server so users can add it with one click. You can either **host the server on Smithery** (Docker/stdio) or **point Smithery to your Vercel URL** (self-hosted HTTP.

### Option A: URL (bring your own hosting)

1. Go to [smithery.ai/new](https://smithery.ai/new.
2. Sign in if needed.
3. Choose **URL** (bring your own hosting.
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

**Improve your Smithery listing:** Open **Settings → General** on your server’s Smithery page. Set **Display name**, **Description**, **Homepage** (e.g. your repo URL or `https://umlmcp.vercel.app`), and **Server icon** to improve discoverability and the Server Metadata score. Publishing with `--config-schema smithery-config-schema.json` (see above) improves the Configuration UX score.

**AI and plugin compatibility:** The app serves `/.well-known/ai-plugin.json` with a dynamic base URL (so OpenAI-style plugins work on any deployment), `/openapi.json` and `/openapi.yaml` for API docs and AI consumers, and `/logo.png` (ICO) for manifests. The server card at `/.well-known/mcp/server-card.json` uses correct JSON schema types for all tools so AI models and Smithery get accurate tool schemas.

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
   If you want to keep protection, use Vercel’s [Protection Bypass for automation](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation. Get the bypass token from the project’s Deployment Protection settings, then in Smithery set **MCP Server URL** to:
   ```
   https://<your-project>.vercel.app/mcp?x-vercel-set-bypass-cookie=true&x-vercel-protection-bypass=YOUR_BYPASS_TOKEN
   ```
   Replace `YOUR_BYPASS_TOKEN` with the token from Vercel.

### Connection error: Initialization failed with status 404 or 405 / “advertise server-card”

Smithery discovers your server by requesting `/.well-known/mcp/server-card.json` on the **root** of your deployment. Vercel reserves the `/.well-known` path and does not allow rewrites to serverless functions, so the FastAPI app may never receive that URL (404). If the path is served but only for certain HTTP methods, you can get **405 Method Not Allowed**; serving the server card as a static asset fixes both (GET/HEAD return 200).

**Fix:** This repo serves the server card as a **static file** at `public/.well-known/mcp/server-card.json`. In `vercel.json`, a **rewrite** maps `/.well-known/mcp/server-card.json` to `/public/.well-known/mcp/server-card.json`, and a static **build** entry includes that file in the deployment. Ensure both the rewrite and the `public/.well-known/mcp/server-card.json` build are present in `vercel.json`. Before publishing to Smithery, verify: open `https://<your-project>.vercel.app/.well-known/mcp/server-card.json` in a browser; you should see valid JSON with `serverInfo`, `tools`, and `resources`. If you see 404/405, redeploy and ensure the latest `vercel.json` is deployed (and that `public/.well-known/mcp/server-card.json` exists after the build). To regenerate the file when tools change, run `python scripts/generate_server_card.py`. Then ensure `public/.well-known/mcp/server-card.json` is committed and deployed.

### "Not Acceptable: Client must accept text/event-stream" (JSON-RPC error)

The [MCP Streamable HTTP](https://spec.modelcontextprotocol.io/specification/2025-03-26/basic/transports/) protocol requires clients to send an **Accept** header that includes `text/event-stream` (e.g. `Accept: application/json, text/event-stream`). If the client or proxy (e.g. Smithery) does not send this header, the MCP layer may respond with a JSON-RPC error: `"Not Acceptable: Client must accept text/event-stream"` (code -32600).

**Server-side workaround:** This app includes middleware that, for all requests to `/mcp` and `/mcp/...`, sets or normalizes the `Accept` header to `application/json, text/event-stream` when it is missing or does not include `text/event-stream`. So connections via Smithery or Cursor should work even if the client or proxy omits the header. No client or Smithery configuration change is required.

If you still see this error after deploying the latest version, ensure the middleware is present in `app.py` (`_MCPAcceptHeaderMiddleware`) and that requests to `/mcp` go through the FastAPI app (not a static rewrite).

### "Bad Request: Missing session ID" (JSON-RPC -32600)

If you see `{"error":{"code":-32600,"message":"Bad Request: Missing session ID"}}` when connecting to `/mcp`, the MCP Streamable HTTP transport is rejecting requests because session validation fails (e.g. on serverless, where sessions cannot persist across invocations).

**Fix:** Ensure `FASTMCP_STATELESS_HTTP=true` is set in your Vercel project. In stateless mode, each request gets a fresh context and does not require session IDs. This is already configured in `vercel.json` for this repo; if you use the Vercel Dashboard for env vars, add it there for Production (and Preview if needed).

### 405 on POST /mcp (Reconnect failed)

If you see **405 Method Not Allowed** on **POST /mcp** (e.g. “Reconnect failed” in Cursor via Smithery, or “Streamable HTTP error: Error POSTing to endpoint: {detail:Method Not Allowed}”), it means the MCP HTTP app did not mount at `/mcp`. The server only registered a GET handler for `/mcp`, so Streamable HTTP clients that use POST get 405.

**What to check:**

1. **Vercel build and runtime logs**  
   In the app startup logs, look for either “MCP HTTP app mounted at /mcp” (success) or “MCP HTTP fallback: GET/POST /mcp return 503 (MCP HTTP transport not available).” If you see the fallback message, the MCP app failed to load. Check for any exception logged in the same block (the app logs with `exc_info=True`).

2. **Dependencies**  
   Confirm that `fastmcp` and all modules used by `get_mcp_server()` (e.g. diagram tools, resources, prompts, Kroki, PlantUML) are installed and import without error. The build runs `pip install -r requirements.txt -r requirements-dev.txt`; ensure the build completes and that `fastmcp>=2.3.1` is present.

**405 vs 503 fallback:** When the MCP app is not mounted, the server registers both GET and POST handlers for `/mcp` that return **503** with `{"detail": "MCP HTTP transport is not available."}` (and OPTIONS for CORS). So clients see “service unavailable” rather than “method not allowed,” and the logs make it clear that the fallback is active.

### Other issues

- **405 Method Not Allowed** on the server card URL: usually fixed by ensuring the server card is served as a static asset at `/.well-known/mcp/server-card.json` so GET/HEAD return 200 (see the 404/405 section above).
- **502 / timeout**: Vercel serverless functions have a max duration (e.g. 60s on Hobby). Long-running tool calls may hit this; consider optimizing or using Smithery-hosted Docker for heavy use.
- **MCP at /mcp**: Ensure you use the path `/mcp` (e.g. `https://...vercel.app/mcp`), not the root URL.
- **CORS**: The app allows all origins for API and MCP; restrict in production if needed.
- **Logo or OpenAPI YAML**: `/logo.png` is served by the app (image/x-icon). `/openapi.yaml` returns the spec in YAML when PyYAML is installed (required in `requirements.txt`); if not, it returns 501 and clients should use `/openapi.json`.
