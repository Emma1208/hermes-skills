---
name: ds-stack-venv-setup
description: Install a Data Science stack (numpy -> pandas -> matplotlib -> ta) in an isolated venv via the Aliyun PyPI mirror, verifying each import immediately. Reusable across sessions; also documents the rules for handing off to another Hermes instance.
---

# DS Stack Venv Setup

Install a Data Science Python stack in an isolated virtual environment, using the
Aliyun PyPI mirror, in the correct dependency order, and verify every import.

## Key rules (transmit these to any other Hermes / user)

1. **NEVER install into the system environment** — always use a dedicated venv.
2. **Install numpy FIRST.** pandas and matplotlib both depend on numpy; installing
   numpy ahead avoids ABI/version conflicts.
3. **Verify each import immediately** after installing it (don't batch all installs
   then check at the end — a failure is caught at the offending package).
4. Use the Aliyun mirror for speed/reliability:
   `https://mirrors.aliyun.com/pypi/simple/`

## Package install order

1. numpy
2. pandas (depends on numpy)
3. matplotlib (depends on numpy)
4. ta (technical analysis; depends on numpy + pandas)

## One-shot script

The ready-to-run script lives at `/root/setup_ds_stack.sh`. To set up the stack:

```bash
bash /root/setup_ds_stack.sh
```

Then use the venv's python directly:

```bash
/root/numpy-venv/bin/python
```

## What the script does

- Creates `/root/numpy-venv` with `python3 -m venv` (isolated, not system-wide).
- Upgrades pip via the Aliyun mirror.
- Defines `install_and_verify()`: installs a package, then runs
  `python -c "import <pkg>"` and prints its version. This guarantees immediate
  import verification per package.
- Installs in order numpy → pandas → matplotlib → ta, verifying each.

## Full script content (for reference / regeneration)

```bash
#!/usr/bin/env bash
set -euo pipefail
VENV="/root/numpy-venv"
MIRROR="https://mirrors.aliyun.com/pypi/simple/"

echo "==> [1/4] Création du venv isolé : $VENV"
python3 -m venv "$VENV"

echo "==> Upgrade pip via le miroir Aliyun"
"$VENV/bin/python" -m pip install --upgrade pip -i "$MIRROR"

install_and_verify() {
  local pkg="$1"
  echo "==> Installation : $pkg"
  "$VENV/bin/python" -m pip install "$pkg" -i "$MIRROR"
  echo "    Vérification de l'import : $pkg"
  "$VENV/bin/python" -c "import $pkg; print('    OK ->', '$pkg', getattr($pkg, '__version__', '?'))"
}

install_and_verify numpy
install_and_verify pandas
install_and_verify matplotlib
install_and_verify ta

echo ""
echo "==> Tous les imports sont vérifiés. Stack prête."
echo "    Utilisez : /root/numpy-venv/bin/python"
```

## Verification

After running, confirm with:

```bash
/root/numpy-venv/bin/python -c "import numpy, pandas, matplotlib, ta; print('numpy', numpy.__version__); print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__); print('ta', getattr(ta,'__version__','?'))"
```

Note: the `ta` package has no `__version__` attribute, so the version prints as `?`
— that is expected and the import itself succeeding is the real check.

## Pitfalls

- Running the installs on the system python (e.g. `pip install ...` without the venv
  activated) pollutes the system env. Always call `"$VENV/bin/python" -m pip ...`.
- `ta` is a source tarball (sdist) — it builds a wheel on install, so it needs build
  deps; the venv's pip handles this automatically.
- If `python3 -m venv` is missing the `venv` module, install it first
  (`apt-get install python3-venv` on Debian/Ubuntu).
