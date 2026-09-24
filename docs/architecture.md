# STRATAGEM DARK architecture

## Boundaries

```text
Clean Arch x86_64 (systemd, pacman, networking, normal user)
  └─ STRATAGEM DARK release manifest
      ├─ core workstation → Hyprland + Foot + optional Quickshell surface
      ├─ security profiles → explicit catalog IDs → repository/package pairs
      ├─ configuration → packaged defaults + separate user overrides
      └─ dark CLI → validate → resolve → plan → stage → [future apply]
Later: archiso frontend → the same release manifest and bootstrap engine
```

Arch owns the kernel, init, package manager, drivers, and base lifecycle. STRATAGEM
DARK owns profile policy, orchestration, desktop defaults, catalog metadata, and
branding. Upstream projects continue to own their programs and package licenses.
No forked package manager, compositor, or security-tool collection.

The Python standard-library core is shared by all entry points. JSON manifests are
data, never sourced as shell. Profiles form an acyclic graph. The resolver rejects
unknown references, duplicate IDs and package targets, invalid identifiers, and
cycles, then returns sorted unique tools. `full` is a curated union.

Core has no BlackArch dependency. Arch packages are preferred where available.
BlackArch additions are opt-in candidates: their repository, signing trust,
license evidence, dependency closure, and artifact availability must be reviewed
before enabling the adapter. No implicit group expansion or repository precedence.

## Desktop and configuration ownership

Hyprland handles windows and input. Foot is the initial terminal. Quickshell is the
intended shell layer; its current directory is a prototype contract, not a working
panel. User home directories are never overwritten. Defaults are staged under
`/usr/share/stratagem-dark/defaults`; a later migration engine will generate small
user includes, save backups, and record old/new hashes before changes.

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
