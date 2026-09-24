# Verification scope

## Automated checks

`python3 -m unittest discover -s tests -v` runs 45 tests covering profile resolution,
metadata validation, reproducible plans, staging guards, imported-source hashes,
configuration preservation, and signed-bundle verification. Seven signature tests
require GnuPG and skip when it is unavailable. All 45 passed in
[Linux CI](https://github.com/stratagem-group/stratagem-dark/actions/runs/36046038022).
Local macOS checks pass 38 with those seven skipped.

CI also validates JSON schemas, Bash syntax, deterministic plans and core staging.
These checks do not establish that the workstation boots successfully.

## Full testing build

The manually dispatched testing build verifies upstream package signatures, records
exact archive hashes and versions, creates a signed offline bundle and composes a
UEFI live ISO from the pinned Arch snapshot. `tests/integration-install.sh` installs
that actual bundle twice into a disposable fresh Arch chroot and checks configuration
preservation. `tests/vm/boot.sh` boots the actual ISO and checks the desktop, shell,
selected security tools and absence of SSH access; it captures logs and screenshots.

These integration checks are acceptance gates, not claims of completed validation.
The current build is still being debugged. No ISO has passed the complete acceptance
sequence yet. Installed-disk reboot, physical hardware, every profile combination,
audio/portal behavior and interrupted-transaction recovery remain separate work.

The live ISO and clean-Arch bundle paths do not implement a disk-wiping installer.
