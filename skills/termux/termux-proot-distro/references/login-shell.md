# Login error: shell '/bin/bash' is not available in container 'void'

## Symptom
```
$ proot-distro login void
Error: shell '/bin/bash' is not available in container 'void'. The image defines an Entrypoint or Cmd; use 'proot-distro run void' instead.
```
Also fails with explicit shell: `proot-distro login void -- /bin/sh` → same error.

## Root cause (code analysis, proot-distro 5.x)
In `proot_distro/commands/login/__init__.py`:
- `_check_shell_available(rootfs, container_path, login_shell, container_name)`:
  - If `os.path.isfile(resolve_rootfs_path(rootfs, login_shell))` is False AND the image's `manifest.json` has an `Entrypoint` or `Cmd`, it raises the "image defines an Entrypoint or Cmd; use 'proot-distro run ...'" error.
- `login_shell` comes from `/etc/passwd` field 6 (root's shell), defaulting to `/bin/sh`.

So the error means: the resolved login shell (reported as `/bin/bash` in the message) does not exist as a real file in the rootfs. In Void glibc images, `/bin/sh` is frequently a **symlink to `bash`**; if the `bash` binary is absent from the image, the symlink is dangling and `isfile()` returns False → error.

## Diagnostic commands (run from Termux, NOT inside the container)
```sh
# 1. Check what root's shell is set to:
grep '^root:' $PREFIX/var/lib/proot-distro/installed-rootfs/void/etc/passwd

# 2. Check whether /bin/sh, /bin/bash, /bin/dash exist and what /bin/sh points to:
ls -l $PREFIX/var/lib/proot-distro/installed-rootfs/void/usr/bin/sh \
      $PREFIX/var/lib/proot-distro/installed-rootfs/void/usr/bin/bash \
      $PREFIX/var/lib/proot-distro/installed-rootfs/void/usr/bin/dash 2>&1

# 3. Inspect the image manifest for Entrypoint/Cmd:
grep -i -A3 -B1 'entrypoint\|cmd' $PREFIX/var/lib/proot-distro/installed-rootfs/void/manifest.json
```
Rootfs base path: `$PREFIX/var/lib/proot-distro/installed-rootfs/void/` (PREFIX = Termux prefix, e.g. `/data/data/com.termux/files/usr`).

## Hypotheses / fix paths (NOT yet confirmed in originating session)
- **If `/bin/sh` is a dangling symlink to `bash` and `bash` is missing**: the image is missing the bash package. Fix options:
  - Install bash into the image: get a shell another way (see below) then `xbps-install -S bash`.
  - Or rewrite root's shell in `etc/passwd` to a shell that exists (e.g. `/bin/dash` if dash is present) — edit the file from Termux with a patch/text edit, then `proot-distro login void`.
- **Try `proot-distro run void`** — runs the image-defined Entrypoint/Cmd (equivalent to `docker run`); may drop you into a working shell or run a default command. From there you can `xbps-install -S bash` and the subsequent `login` may then succeed.
- **`proot-distro login void -- /bin/dash`** (or any shell that actually exists) — if the shell binary exists, `login` may still wrap it; worth trying once you've confirmed which shell binaries are present.

## Status
Unresolved at end of originating session (the `ls -l`/manifest diagnostics above had not been run yet). Capture here so the next session continues from the diagnosis rather than re-deriving.
