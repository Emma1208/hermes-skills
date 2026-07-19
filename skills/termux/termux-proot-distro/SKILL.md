---
name: termux-proot-distro
description: Install and run Linux distributions (Void, Ubuntu, Debian, Alpine...) inside Termux on Android using proot-distro. Covers the current Python/OCI-based proot-distro 5.x, the correct image-reference syntax, and the common "Unauthorized", "Layer integrity check failed", and login shell errors. Use whenever the user wants a Linux container in Termux, especially Void Linux.
---

# Termux — installing Linux distros with proot-distro

## When to use
- User wants to run a full Linux distro inside Termux (Android): Void, Ubuntu, Debian, Alpine, Arch, etc.
- Any `proot-distro install|login|remove|list` work.
- Errors during install/login of a Termux container.

## KEY FACT (do not misdiagnose)
The current official `proot-distro` in Termux's `termux-main` repo is **v5.x, a Python rewrite**. It pulls **Docker/OCI images** (from Docker Hub, ghcr.io, quay.io, …) instead of the old shell-script rootfs tarballs. Symptoms that look "modded/forked" but are **NORMAL**:
- `pkg install proot-distro` shows `Installing dependencies for proot-distro through pip...` and pulls a pip package — this is expected.
- `apt-cache policy proot-distro` shows a 5.x version from grimler.se — official.
- `install void` fails with `Unauthorized: 'void' does not exist or is a private image. Set PD_DOCKER_AUTH=...` — this is NOT a bad mirror or a modded app; it means the bare name `void` is not a valid OCI image reference.

Do NOT tell the user to reinstall Termux from F-Droid or that their app is compromised — that was a wrong hypothesis in one session and wastes the user's time.

## Correct install commands
Bare distribution *aliases* only work when they are valid Docker image references. Use the **full image reference**:

```sh
# Void Linux (glibc, full) — the one most people want:
proot-distro install ghcr.io/void-linux/void-glibc-full:latest --name void

# Other Void images (confirmed namespace ghcr.io/void-linux):
#   void-glibc:latest        (base/minimal glibc)
#   void-musl-full:latest    (musl variant)
#   void-glibc-full:latest   (full glibc, recommended)

# Standard distros still work with short names (official Docker images):
proot-distro install ubuntu:24.04
proot-distro install alpine:3.21
proot-distro install debian:bookworm
```

`--name <x>` sets the local container name (used by `login <x>`). If omitted it defaults to the image name without tag/registry.

## Login / usage
```sh
proot-distro login void
# inside Void, package manager is xbps:
xbps-install -Su            # update
xbps-install -S nano git python3
exit                        # leave container
```

## Pitfalls & fixes

### 1. "Unauthorized: 'void' does not exist or is a private image"
You ran `proot-distro install void`. `void` alone is not an OCI image reference. Use the full `ghcr.io/void-linux/void-glibc-full:latest --name void` (see above).

### 2. "Layer integrity check failed for digest ... expected X, got Y"
The downloaded layer was corrupted in transit (very common on flaky 4G). Fix:
```sh
proot-distro clear-cache
proot-distro install ghcr.io/void-linux/void-glibc-full:latest --name void
```
Prefer a stable Wi-Fi connection for the ~70 MB download. This is a network-corruption issue, NOT a mirror or app problem.

### 3. Login: "shell '/bin/bash' is not available in container 'void'. The image defines an Entrypoint or Cmd; use 'proot-distro run void' instead"
See `references/login-shell.md` — unresolved in the originating session; diagnostic commands and hypotheses are documented there. The short form: the Void image's shell resolution points at a non-existent `/bin/bash` (often `/bin/sh` is a dangling symlink to bash when bash isn't in the image); `login` refuses to start. Diagnose with the commands in that reference and try `proot-distro run void`, or install bash inside the image once a shell is reachable.

## Workflow preference (EMBED — this user)
When driving Termux for this user: **send ONE command at a time**. Give a single command, then WAIT for the user's screenshot/output before giving the next step. Do NOT batch a numbered list of sequential commands or say "run these then tell me". If you slip into listing multiple commands, the user will correct you — self-correct immediately. The user is on a phone with an on-screen keyboard taking screenshots of Termux, so each step must be atomic and verifiable.

Respond to this user in **French** (their standing preference).

## References
- `references/void-images.md` — confirmed Void OCI image references on ghcr.io.
- `references/login-shell.md` — the `/bin/bash` login error: diagnosis commands + open hypotheses.
