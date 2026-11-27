# Baileys (personal) vs WhatsApp Business Cloud — detail

## Commands (from `hermes` CLI help)
- `hermes whatsapp` → "Configure WhatsApp and pair via QR code"
- `hermes whatsapp-cloud` → "Configure the official Meta WhatsApp Business Cloud API adapter (Business account required, public webhook URL required). Distinct from `hermes whatsapp` which sets up the Baileys bridge for personal accounts."
- `hermes gateway setup` → configures messaging platforms (no extra args shown in --help).
- `hermes gateway {run,start,status,...}` → runs the gateway that hosts the WhatsApp adapter.

## Source locations inspected (read-only)
- `plugins/platforms/whatsapp/adapter.py` — the gateway adapter.
  - Line ~12: "3. Baileys (via Node.js subprocess) - alternative for personal accounts"
  - Uses `find_node_executable`, `with_hermes_node_path` → Node subprocess bridge.
  - ~L489-505: if `creds.json` absent, bridge prints QR to log and never reaches `status:connected`; status message: "WhatsApp enabled but not paired — pair from the dashboard or run `hermes whatsapp`."
  - Policies: `dm_policy` / `group_policy` (open / allowlist / disabled / pairing), default "pairing".
- `hermes_cli/subcommands/whatsapp.py` — thin parser that wires `hermes whatsapp` to `cmd_whatsapp`.
- `hermes_cli/setup_whatsapp_cloud.py` — Cloud API setup helper.
- `gateway/platforms/whatsapp_cloud.py`, `gateway/platforms/whatsapp_common.py`, `gateway/whatsapp_identity.py` — Cloud adapter + shared bits.

## Capability matrix
| Capability | Baileys (A) | WABA (B) |
|------------|-------------|----------|
| Read personal chats | ✅ | ❌ (separate number) |
| Send messages/media | ✅ | ✅ (templated/API) |
| Delete own sent msgs | ✅ (time-limited) | n/a (API-sent) |
| Manage groups | ✅ leave/create | ✅ via API |
| Change number / delete account | ❌ | ❌ (Meta console) |
| Needs 2nd screen for auth | QR yes / pairing-code maybe | ❌ (no QR) |
| Ban risk | low–moderate (unofficial) | none (official) |
| Cost | free | free tier ~1000 msg/mo then billed |
| Public webhook required | ❌ | ✅ |

## Single-phone QR workaround (unverified for Hermes)
Standard Baileys supports `sock.requestPairingCode(phoneNumber)` → 8-digit code shown in app, typed on phone under Linked Devices → "Link with phone number". Hermes's bundled `bridge.js` was NOT found in this session (no `bridge.js` outside node_modules; bridge path resolves at runtime). **Verify the bridge exposes this before promising the user a code-based pairing.**

## Environment notes (this host)
- Node v26.4.0 / npm 11.18.0 present → Baileys bridge can run.
- Host is local (proot-distro Linux, no public IP) → WABA webhook needs ngrok or hosted server.
