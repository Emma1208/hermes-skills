#!/bin/bash
# Deploy files to GitHub via the API. The PAT is read from GITHUB_TOKEN env var,
# never passed as a command argument (avoids security-scan blocking).
# Usage: GITHUB_TOKEN=ghp_xxx ./deploy_files.sh <owner> <repo> <local:remote> [...]
set -e
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN in the environment}"
OWNER="${1:?owner missing}"
REPO="${2:?repo missing}"
shift 2
export GH_OWNER="$OWNER" GH_REPO="$REPO" GH_TOKEN="$GITHUB_TOKEN"

for PAIR in "$@"; do
  export GH_LOCAL="${PAIR%%:*}"
  export GH_REMOTE="${PAIR#*:}"
  if [ ! -f "$GH_LOCAL" ]; then
    echo "MISSING FILE: $GH_LOCAL"
    continue
  fi
  # Python builds the JSON payload by reading the file itself (no huge argv).
  python3 - <<'PY' > /tmp/gh_payload.json
import os, json, base64, urllib.request
owner, repo, token = os.environ['GH_OWNER'], os.environ['GH_REPO'], os.environ['GH_TOKEN']
local, remote = os.environ['GH_LOCAL'], os.environ['GH_REMOTE']
base = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote}"
def req(url, method="GET", data=None):
    r = urllib.request.Request(url, method=method, data=data,
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.load(resp)
sha = ""
try:
    sha = req(base).get("sha", "")
except Exception:
    pass
content = base64.b64encode(open(local, 'rb').read()).decode()
payload = {"message": f"Mise a jour {remote}" if sha else f"Ajout {remote}", "content": content}
if sha:
    payload["sha"] = sha
print(json.dumps(payload))
PY
  SHA=$(python3 -c "import json; print(json.load(open('/tmp/gh_payload.json')).get('sha',''))")
  python3 - <<'PY'
import os, json, urllib.request
owner, repo, token = os.environ['GH_OWNER'], os.environ['GH_REPO'], os.environ['GH_TOKEN']
remote = os.environ['GH_REMOTE']
url = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote}"
payload = json.load(open('/tmp/gh_payload.json'))
r = urllib.request.Request(url, method="PUT", data=json.dumps(payload).encode(),
    headers={"Authorization": f"token {token}",
             "Accept": "application/vnd.github+json",
             "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(r, timeout=30) as resp:
        d = json.load(resp)
    print("OK   " + remote + " " + str(d.get('commit', {}).get('sha', '')[:12]))
except urllib.error.HTTPError as e:
    print("ECHEC " + remote + " HTTP " + str(e.code) + " " + e.read().decode()[:200])
PY
done
rm -f /tmp/gh_payload.json
