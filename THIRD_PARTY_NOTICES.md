# Third-party notices

No third-party source code, logos, themes, fonts, or package binaries are bundled
in this initial scaffold. `provenance/imports.json` is the authoritative empty
source-import register. `docs/upstream-audit.md` records sources inspected before
implementation, with immutable commit links and file digests.

Omarchy (`omacom/omarchy` and `omacom/omarchy-iso`) was evaluated as an MIT-licensed
reference. No files were copied or adapted. Its name appears only in provenance,
legal discussion, and the upstream audit; its branding is not used by this product.

BlackArch's `blackarch` package repository was evaluated under its BSD-3-Clause
COPYING notice. No recipes or scripts were copied. Proposed external packages and
keyrings retain separate licenses; the repository license is not a blanket license
for the tools. The installer and ISO repositories were inspected but not reused;
no root license was found at the recorded revisions.

Arch Linux, Hyprland, Quickshell, Foot, and the tools in `catalog/tools.json` are
proposed external dependencies, not vendored code. Their own notices and licenses
will ship with their packages. Catalog entries are pending release review.

The CI checkout action is an external build service dependency, pinned by commit;
it is not distributed as part of STRATAGEM DARK. Python is a user-provided runtime.

Future copied code requires full upstream notices, license files, exact destinations,
and modification records before merge. Never remove attribution to enforce branding.
