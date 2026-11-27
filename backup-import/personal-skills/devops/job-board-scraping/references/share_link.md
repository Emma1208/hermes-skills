# Sharing generated files as links (no attachment)

When the user wants a generated file (CV/PDF/report) sent as a LINK instead of a Telegram
attachment, upload it to a temp host and paste the URL.

## Working host (tested 2026-07, Kinshasa/RDC context)
`tmpfiles.org` — reliable, no key, ~24-48h retention.

```bash
curl -s -F "file=@CV.pdf" https://tmpfiles.org/api/v1/upload
# -> {"status":"success","data":{"url":"https://tmpfiles.org/<id>/cv.pdf"}}
```

## Hosts that FAILED / are shut (do not retry, they waste time)
- `0x0.st` — "uploads disabled because it's been almost nothing but AI botnet spam" (closed).
- `litterbox.catbox.org` — returned empty response.
- `file.io` — 301 redirect / Cloudflare block on plain curl.
- `transfer.sh` — silent empty response on upload.

## Note
Telegram file attachments also work and arrive in-chat; links are the user's stated PREFERENCE
for reviewable docs, but attach if link hosting is down.
