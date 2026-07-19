# Void Linux OCI image references (ghcr.io/void-linux)

Confirmed working with `proot-distro install <ref> --name void` (proot-distro 5.x, Termux).

| Image reference | Notes |
|---|---|
| `ghcr.io/void-linux/void-glibc-full:latest` | **Recommended** — full glibc Void. ~70 MB layer + small config layer. |
| `ghcr.io/void-linux/void-glibc:latest` | Base/minimal glibc Void. |
| `ghcr.io/void-linux/void-musl-full:latest` | musl libc variant. |
| `ghcr.io/void-linux/void-musl:latest` | Base musl variant. |

Pulled anonymously (no `PD_DOCKER_AUTH` needed) because ghcr.io public images use an anonymous Bearer token from the registry's `/v2/` challenge.

Related/legacy note: older proot-distro (4.x, shell script) used prebuilt rootfs tarballs and DID accept `proot-distro install void`. The 5.x Python rewrite does NOT — it requires the full OCI reference above.

Package manager inside Void: **xbps** (`xbps-install`, `xbps-query`, `xbps-remove`). First run after install: `xbps-install -Su`.
