# Skill + Cron Persistence Recipe (condensed)

Source of truth: session 2026-07-09. Verified working on the `/root` environment; phone paths differ (`/data/data/com.termux/files/home/...`).

## 1. Persist personal skills into the backup repo
```bash
cd /root/hermes-termux-backup
mkdir -p personal-skills
cp -r /root/.hermes/skills/* personal-skills/
```
Add to `auto_sync.sh` (Python sync block, after step 8):
```python
personal_skills_src = hermes / 'skills'
if personal_skills_src.exists():
    for f in personal_skills_src.rglob('*'):
        if f.is_dir():
            continue
        rel = f.relative_to(personal_skills_src)
        if '__pycache__' in str(rel) or '.pyc' in str(rel) or '.usage.json' in str(rel):
            continue
        target = backup / 'personal-skills' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or f.stat().st_mtime > target.stat().st_mtime:
            shutil.copy2(f, target)
```
Add to `restore.sh` AFTER the source-skills copy:
```bash
if [ -d "$BACKUP_DIR/personal-skills" ]; then
    cp -r "$BACKUP_DIR/personal-skills/"* "$HERMES_DIR/skills/" 2>/dev/null || true
    echo "  ✓ Personal skills (custom)"
fi
```

## 2. Persist cron dir
In `auto_sync.sh` (after skills step):
```python
cron_src = hermes / 'cron'
if cron_src.exists():
    cron_dst = backup / 'cron'
    cron_dst.mkdir(parents=True, exist_ok=True)
    for f in cron_src.rglob('*'):
        if f.is_dir() or f.name.endswith('.lock'):
            continue
        rel = f.relative_to(cron_src)
        target = cron_dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or f.stat().st_mtime > target.stat().st_mtime:
            shutil.copy2(f, target)
```

## 3. Recreate the auto-backup cron on a device
Cron `script` MUST be a filename inside `~/.hermes/scripts/` (absolute/home paths are rejected).
```bash
# script lives at /root/.hermes/scripts/auto_sync.sh, paths adapted to /root
chmod +x /root/.hermes/scripts/auto_sync.sh
```
Then: `cronjob create --name 'Auto-Backup Hermes' --schedule 'every 2h' --script auto_sync.sh --no-agent --deliver local`

## 4. Git identity (run once per clone)
```bash
cd /root/hermes-termux-backup
git config user.name "Emmanuel Kakesa Mudimba"
git config user.email "emmanuelkakesa@outlook.com"
```

## 5. Pre-push secret scan (mandatory)
```bash
grep -rniE "ghp_[A-Za-z0-9]{20,}|api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9]{20,}" /root/.hermes/skills
# pattern mentions like 820389... / ghp_* in prose are OK; real secret VALUES are not
```

## Known limitation
LAN-only Termux server (`10.253.42.225:22`, user `u0_a556`) is unreachable from sandboxed/external envs — `/dev/tcp` connect refused. Don't attempt to pull live bot code from it; it is already captured by the phone's own `auto_sync.sh` (the `code/` dir). Reconstruct custom skills from `memories/MEMORY.md` + `USER.md` if the source device is gone.
