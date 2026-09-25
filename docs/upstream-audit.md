# Upstream review — 2026-09-24

The initial decisions below are historical. The [desktop parity review](desktop-parity-review.md)
records the subsequent stable/current source comparison and the user-selected
Omarchy-first desktop direction. `provenance/imports.json` remains authoritative
for files actually imported; reviewed sources are not automatically shipped.

This review preceded implementation. GitHub default branches were resolved to the
immutable commits below; repository trees, root notices/READMEs and selected
installer/packaging files were inspected. This is a scoped reuse review, not a full
security audit of upstream. Machine-readable file SHA-256 digests are in
`provenance/upstream-audit.json`. Inspected source stays outside this repository.

| Repository | Commit | Root license observed | Code reused |
| --- | --- | --- | --- |
| [BlackArch/blackarch](https://github.com/BlackArch/blackarch/tree/b59e4b919e69b059a051a1c5db0489dd0eafd22c) | `b59e4b919e69b059a051a1c5db0489dd0eafd22c` | BSD-3-Clause | None |
| [BlackArch/blackarch-installer](https://github.com/BlackArch/blackarch-installer/tree/8ec29e00a7236244be434f072b4a2d8ff9ff5b0d) | `8ec29e00a7236244be434f072b4a2d8ff9ff5b0d` | No root license found; reuse blocked | None |
| [BlackArch/blackarch-iso](https://github.com/BlackArch/blackarch-iso/tree/55bd41df7b2517fdd38538a90a6ea584bdf9b2b8) | `55bd41df7b2517fdd38538a90a6ea584bdf9b2b8` | No root license found; reuse blocked | None |
| [omacom/omarchy](https://github.com/omacom/omarchy/tree/28ceaae70ebac3a0edcc21f2faa77a90dc6d404c) | `28ceaae70ebac3a0edcc21f2faa77a90dc6d404c` | MIT | None |
| [omacom/omarchy-iso](https://github.com/omacom/omarchy-iso/tree/86c07785cb0f63be78edb1349843d5817b5c0e66) | `86c07785cb0f63be78edb1349843d5817b5c0e66` | MIT | None |

## Omarchy main repository

Observed `bin/`, `config/`, `default/`, `install/`, `migrations/`, `shell/`, `themes/`
and `test/`. Examined `install/config/all.sh`, `install/user/all.sh`,
`install/helpers/logging.sh` and `install/omarchy-base.packages`. Installation is
split into configuration, hardware, login, user and post-install stages. The core
package list includes Hyprland, Quickshell and Foot alongside many opinionated apps.

Decision: reuse the architectural idea of separate stages and packaged defaults;
write the implementation independently. The logging and hardware helpers could be
future MIT imports after file-level review. Do not inherit the full package list,
brand assets, product-specific update logic, or assumptions about its base system.
The root notice credits David Heinemeier Hansson and requires preserved notices.

## Omarchy ISO repository

Observed `builder/`, `configs/`, `manifests/`, `bin/`, `test/`. Inspected the ISO
builder, local package builder and archiso profile. The builder composes an Arch
releng base, product packages, configuration overlays and an offline mirror. Its
README describes VM acceptance/integration flows. This supports keeping ISO as a
later frontend to the same package manifest. The root license is MIT.

Decision: no code copied. Build a STRATAGEM DARK bootstrap first. Do not adopt its
branding, signing keys, remote services, or local development signature/checksum
bypasses. Evaluate small VM-harness adaptations later with exact attribution.

## BlackArch package repository

Observed `packages/`, `scripts/`, `lists/`, `mirror/`, `docs/` and test tooling.
Read `COPYING`, README, `scripts/blackman`, and the keyring PKGBUILD. The repository
contains recipes and package tooling under BSD-3-Clause; this does not determine
every package's software license. The keyring recipe itself reports
`custom:unknown`, reinforcing the need for separate artifact/license review.

Decision: use curated external packages when trust and licensing are resolved;
never import the whole tool group or source PKGBUILDs to discover metadata. Prefer
Arch packages where already available. `capa` and `zeek` recipe paths were confirmed
in the inspected tree; their catalog records remain pending review. No recipe,
bootstrap script, mirror list or keyring is shipped here.

## BlackArch installer and ISO repositories

The installer is a large Bash entry point plus `data/` and `docs/`; it combines
partitioning, users, networking and tool setup. The ISO repository separates
`layers/base`, `graphical`, `full`, `slim`, `netinstall` and build/merge tools. Read
its merge script and profile template. No root LICENSE/COPYING was found in either
recorded tree; the inspected installer header did not establish a license grant.
That is an unresolved finding, not a claim that every file is unlicensed.

Decision: do not copy these sources until applicable licenses are established.
Independent profile composition is sufficient; no disk installer is needed for the
initial clean-Arch overlay path.

## Exact ownership boundary

The CLI, installer, tests, schemas, documentation and visual assets are authored for
STRATAGEM DARK under MIT. The desktop contains adapted MIT-licensed upstream files;
`provenance/imports.json` records each original and adapted file with its hash.
The initial scaffold imported no files; that historical decision was superseded by
the derivative implementation below. Arch, Hyprland, Quickshell, Foot and security
tools retain their upstream ownership and licenses. Required legal attribution is
separate from product branding.

## Derivative implementation update

The user selected an Omarchy-based derivative after the foundation review. The current
implementation reuses its Quickshell shell, Hyprland defaults and selected desktop
helpers at the recorded main-repository commit. The machine-readable import register
now supersedes the earlier no-import decision and lists exact destinations and hashes.
No package recipes or installer code are copied from the other inspected repositories.
