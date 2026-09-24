# License and provenance strategy

Original STRATAGEM DARK code, documentation, schemas, and artwork in this initial
revision use the root MIT license. Contributor copyright remains with contributors;
there is no assignment requirement. New source files should carry `SPDX-License-Identifier: MIT`.

Dependency packages are not covered by the root license. Verify the actual selected
version's license files and redistribution obligations before bundling. GPL-family
source offers/corresponding source, notices, non-code assets, firmware, and mixed
license packages need separate handling. Only verified open-source software is
eligible for the curated project profiles. Hardware firmware exceptions, if ever
needed, require explicit documentation and must not be described as open-source.

Names and logos are a separate identity policy: do not imply upstream endorsement.
STRATAGEM DARK uses original visual assets. Preserve upstream names inside required
legal notices even though they are not product branding. This policy does not assert
registered trademark status or completed name clearance.

## Import checklist

1. Pin upstream URL, commit and file paths; inspect file headers and license scope.
2. Record imported destination paths and modifications in `provenance/imports.json`.
3. Preserve copyrights and full applicable license text under `LICENSES/`.
4. Update `THIRD_PARTY_NOTICES.md`; include any binary distribution obligations.
5. Test the adaptation and explain why a dependency or upstream fix was insufficient.

No third-party source is imported in the scaffold. Package metadata is a curated
reference, not a copied package recipe or a claim of license clearance. All entries
start with `license_review: pending`; a release resolver must refuse pending entries.
