---
name: oauth-thirdparty-connect
description: Connect the user to a third-party OAuth2 or OpenID API such as LinkedIn Google or GitHub and read their data into the agent including the working manual-code-copy pattern when the agent runs on a server but the user authorizes from their own device.
triggers:
  - user wants to connect their LinkedIn Google GitHub or other account to the agent
  - link my profile or read my profile via API or connect me to an external API
  - building an OAuth2 auth flow for a user-managed external account
  - agent must obtain a users own access token from a provider
---

# Connecting the user to a third-party OAuth API

## Core pattern — manual code-copy (works across device/network boundaries)
When the AGENT runs on a remote server but the USER authorizes from their own phone/PC,
a localhost redirect (http://localhost:8080/) set as the OAuth redirect_uri will NOT
reach the agent's server — the user's browser resolves localhost to THEIR machine. The
automatic "server listens on localhost" auth flow silently fails.

The robust workaround (proven with LinkedIn OpenID Connect, 2026-07):
1. Build the provider authorization URL with redirect_uri=http://localhost:8080/
   (still required by the provider as a registered redirect).
2. Send the FULL auth URL to the user. They open it, log in, click Authorize.
3. The provider redirects to http://localhost:8080/?code=XXXX&state=... which throws
   a browser error on the user's side. NORMAL.
4. User copies the code= value from the address bar and pastes it back to the agent.
5. Agent exchanges the code for tokens server-side (with client_id + client_secret) and
   calls the API. The code is single-use and short-lived (~30s) — tell the user to send it immediately.

DO NOT build a localhost HTTP server expecting the redirect to arrive at the agent unless
the agent and the authorizing browser are on the SAME machine.

## Secrets handling
- Store client_id / client_secret in a local config file (e.g. ~/.agent/<app>/config.json),
  chmod 700, NEVER in chat logs or memory in plaintext beyond first receipt.
- The user WILL paste secrets into chat once. Acknowledge receipt, save locally, then
  instruct them never to re-share in the clear.

## LinkedIn specifics (reference file)
See references/linkedin-openid.md for exact app setup steps, the product to request
(Sign In with LinkedIn using OpenID Connect), the userinfo endpoint, and the HARD
capability limits (no full-profile read, no profile edits, no job-search API).
Key honesty point: a user asking to read my whole profile edit it and search jobs via
the LinkedIn API CANNOT be satisfied through the API — only browser automation can.
Tell them that up front, then offer browser-automation or guided-manual as the real options.

## Generic provider checklist
- Register an app at the provider's developer console.
- Copy Client ID + Secret to local config.
- Register http://localhost:8080/ as a redirect URI.
- Request the minimal scope that covers the need (openid/profile/email for identity).
- Use the provider's /oauth/v2/authorization + /oauth/v2/accessToken + a userinfo
  endpoint (OpenID: .../v2/userinfo). Tune per provider.
- Exchange code to tokens server-side, call API, save result locally as proof.
