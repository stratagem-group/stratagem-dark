# Bootstrap contract

## Implemented now

`bootstrap/install.sh` forwards to `dark bootstrap`. Default behavior is dry-run.
`--stage NEW_DIRECTORY` writes only to an absent destination under an existing,
user-owned parent. It refuses root execution, existing paths and symlink parents;
on error it removes only the staging tree it created. Staging is designed for a
trusted local workspace, not a directory writable by another user. Output includes
original defaults, `plan.json`, and a checksum/mode manifest. No commands from the
plan are executed. `--apply` always returns an error, on every host.

`dark doctor` is read-only. Its host check is diagnostic, not proof of clean Arch
or installation readiness. JSON output exposes checks separately from the overall
`ready_for_live_apply: false` result.

## Target prerequisites for milestone 0.2

Fresh, fully booted Arch Linux x86_64, systemd, working pacman trust, network and
DNS, synchronized clock, a normal user with narrowly scoped sudo, and sufficient
free disk. Python must already be installed to run the bootstrap. Hardware/GPU,
firmware, filesystem, encryption, and bootloader choices belong to the base
installation. Initially validate on disposable UEFI QEMU VMs; no dual-boot support.

## Planned phase order (not executable yet)

1. **Preflight:** verify host identity, architecture, clean baseline, user, disk,
   pacman lock, trust and release compatibility. Reject unsupported states.
2. **Resolve:** expand the selected profile against a signed release lock including
   all dependencies and a consistent Arch snapshot.
3. **Fetch/verify:** obtain immutable archives, verify hashes and package signatures
   against independently recorded fingerprints. Fail on missing/changed artifacts.
4. **Packages:** perform a consistent full-system transaction with pacman. Never
   perform a partial `-Sy` upgrade or resolve unspecified packages from live mirrors.
5. **System config:** install STRATAGEM DARK packages and minimal drop-ins. Record
   the transaction and file hashes; do not replace Arch's identity files wholesale.
6. **User config:** preview diffs; preserve existing files with conflict detection
   and backups. Install includes as the target user, never blanket-copy a home tree.
7. **Verify:** check session startup, portal/audio health, expected packages, enabled
   services, and file ownership. Reboot in the VM and verify again.

## Failure and repeatability

Package phase failure stops subsequent work. Configuration writes are atomic and
journaled. A second run must converge without duplicate repositories, services,
includes, or changed user customizations. Recovery cannot promise reversal of
package scripts or arbitrary upgrades; capture a VM/filesystem snapshot first.

## Acceptance gate

Before implementing a usable `--apply`, add a populated signed lock, artifact cache,
privilege boundary, real transaction journal, failure injection and two-run VM tests.
Tests must also cover mirror failure, bad signatures, missing packages, interrupted
phases, and user config conflicts. ISO work follows this gate, using the same engine.
