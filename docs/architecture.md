# STRATAGEM DARK architecture

## Boundaries

```text
Clean Arch x86_64 (systemd, pacman, networking, normal user)
  └─ STRATAGEM DARK release manifest
      ├─ core workstation → Hyprland + Foot + adapted Omarchy Quickshell desktop
      ├─ security profiles → explicit catalog IDs → repository/package pairs
      ├─ configuration → packaged defaults + separate user overrides
      └─ dark CLI → validate → resolve → plan / stage / signed bundle install
Testing ISO: archiso frontend → the same signed package bundle
```

Arch owns the kernel, init, package manager, drivers, and base lifecycle. STRATAGEM
DARK owns profile policy, orchestration, desktop defaults, catalog metadata, and
branding. Upstream projects continue to own their programs and package licenses.
No forked package manager, compositor, or security-tool collection.

The Python standard-library core is shared by all entry points. JSON manifests are
data, never sourced as shell. Profiles form an acyclic graph. The resolver rejects
unknown references, duplicate IDs and package targets, invalid identifiers, and
cycles, then returns sorted unique tools. `full` is a curated union.

The core profile has no BlackArch dependency. Arch packages are preferred where
available. Testing security selections include explicit BlackArch packages with
verified build inputs; optional installation uses a root-owned catalog and signed
package transactions. Catalog coverage is not a claim that every tool was tested.

## Desktop and configuration ownership

The desktop is an Omarchy derivative: Hyprland, Foot and its adapted Quickshell
shell are working components in the testing ISO. Preserve upstream interaction
patterns and integrate BlackArch through profiles, discovery and agent workflows.
Keep the local desktop changes small and attributable. Independent STRATAGEM DARK
branding does not require independently rebuilding every settings screen.

Alpha2 still diverges materially: Wi-Fi redirects into a terminal wizard, agent
launch repeats setup, and the theme picker is absent. The source comparison and
pending acceptance requirements are in [Desktop parity review](desktop-parity-review.md).
This is the governing direction for the next desktop iteration, not a claim those
gaps have already been fixed.

Defaults are packaged under `/usr/share/stratagem-dark`; user setup preserves
existing configuration. A complete migration/rollback engine remains outstanding.

Prefer systemd drop-ins and supported upstream configuration interfaces. Services,
telemetry, remote access, packet-capture capabilities, and container privileges
must each be an explicit policy decision, not side effects of profile selection.

## Release model

Pin source commit, base-image digest, repository database digests, signing-key
fingerprints, every package version/architecture/hash/signature, and the transitive
dependency closure. Store immutable artifacts in an owned release cache. A mutable
rolling mirror plus a package-name list is not deterministic installation.

Each future phase records started/succeeded/failed state, input hashes, and output
checksums. Resume rechecks actual state and never trusts a checkpoint alone.
Pacman transactions are not a full-system rollback; VM/filesystem snapshots and
configuration backups are separate recovery mechanisms.

## Upstream policy

Fix generic bugs upstream first. Avoid patching upstream names out of copyright
notices. An imported file needs a pinned source, full license text, attribution,
local change record, and tests. Public product identity remains STRATAGEM DARK.
See the audit for evaluated reuse opportunities and explicit non-reuse decisions.

## Testing-alpha implementation

The current release builder lives in scripts/build-alpha.sh. It packages the adapted
upstream desktop, freezes a complete package archive/signature set, tests offline
installation twice in a clean Arch chroot, and composes an archiso live image.
The workflow then boots the ISO in a UEFI QEMU VM. See docs/testing-release.md for
the executable commands and verification boundaries; earlier phase descriptions
in this document are design goals rather than claims that every gate has passed.
