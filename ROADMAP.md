# STRATAGEM DARK roadmap

## 0.1 — public foundation (this scaffold)

- [x] Independent identity, MIT strategy, contribution/security policies.
- [x] Commit-pinned upstream inspection and explicit import register.
- [x] Validated catalog, five profiles, deterministic plan resolver.
- [x] Unprivileged filesystem staging and CLI/installer skeleton.
- [x] Unit/contract tests and CI; disabled ISO structure.
- [x] Public repository publication and verified green hosted CI.

## 0.2 — deterministic clean Arch bootstrap (next priority)

- [x] Select and document a fixed Arch x86_64 baseline and builder image digest.
- [ ] Review candidate package licenses and freeze a full dependency closure.
- [x] Signed testing manifests, hash-locked package bundle and explicit key fingerprints.
- [ ] Transactional package adapter, checkpoints, failure recovery and resume.
- [x] Preserve existing configuration and verify repeat installation in a fresh Arch chroot.
- [ ] Snapshot/rollback tooling and installed-disk reboot acceptance.
- [ ] Real Hyprland/Foot session, portal/audio checks; Quickshell prototype.
- [ ] UEFI VM install/reboot/two-run tests for every profile.
- [ ] BlackArch adapter opt-in tests with pinned keyring and signed artifacts.

Exit: fresh Arch reaches a verified STRATAGEM DARK session reproducibly; missing or
invalid artifacts fail closed; a second run preserves user changes. Publish logs,
package manifests and limitations. Do not describe a deterministic plan as a fully
reproducible operating system.

## 0.3 — usable alpha

- [ ] Pacman packages for CLI, defaults and profiles; signed update channels.
- [ ] Shell/launcher, accessible CRT theme, tool search and isolated-lab guidance.
- [ ] Package-source/SBOM publication and update/rollback documentation.
- [ ] Selected hardware smoke tests and independent security review.

## 0.4 — ISO, after bootstrap acceptance

- [x] Pin archiso and reuse the signed package manifest for ISO composition.
- [ ] Original boot branding, UEFI VM tests and live-session policy.
- [ ] Signed ISO/checksums, source artifacts, SBOM and published build recipe.
- [ ] Installer disk/encryption review before supporting physical installs.

No release dates promised; acceptance evidence determines promotion.
