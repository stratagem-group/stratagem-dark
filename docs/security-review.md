# Pre-promotion security review

Status: in progress. No release is approved for promotion. Passing tests do not
establish that the workstation is fully secure or production hardened.

## Repository controls applied

- Main requires a pull request, current-base checks, resolved review threads and
  linear history. Force pushes and deletion are blocked; no bypass actors exist.
- Required GitHub Actions checks: validate, Analyze (python), Analyze
  (javascript-typescript), Analyze (actions). CodeQL uses its extended suite; medium-or-higher security findings and errors block merges.
- Release tags cannot be rewritten or deleted.
- Secret scanning and push protection, dependency alerts and automated security
  fixes are enabled. Workflow tokens default to read-only and cannot approve PRs.
- Only GitHub-owned actions are allowed; commit SHA pinning is required.
  All external contributors require workflow-run approval.
- Publication uses the testing-release environment with explicit maintainer review,
  protected-branch deployment policy and administrator bypass disabled.

Only ViralFawkes currently maintains the repository. Independent approving reviews
are not required until a second reviewer is designated. Pull requests and required
checks still apply. This is an explicit remaining governance gap. The organization does not currently
require two-factor authentication. The owner-only membership audit found no members with 2FA disabled. Enforcing
organization-wide 2FA is awaiting confirmation because it affects 28 repositories.

## Findings and evidence

The live VM exposed WhatWeb's installation hook downloading unpinned Ruby gems.
It is excluded from the binary selection pending deterministic packaging. Actual
package transactions and image composition now execute without network access.

CodeQL alert 1 (clear-text storage) was reviewed as a false positive: the value is
SHA-512 crypt output from `openssl passwd -6`, written to `/etc/shadow` mode 0400.
The published live-only test credential remains an intentional limitation, not a
production credential. Root is locked, SSH is disabled and no sudo grant is added.

## Gates still open

- Functional ISO acceptance passed in run 36048967952. Its service audit found
  multicast discovery listeners; the follow-up hardening candidate disables these
  and adds a default-drop inbound/forward firewall, with explicit VM assertions.
- Independent source and installer review, including privileged file operations,
  dependency scriptlets, network listeners and default service policy.
- Broader vulnerability coverage for BlackArch, embedded binaries and dependencies;
  the Arch tracker alone is incomplete and may be stale.
- Stable release-key custody, rotation/revocation and reproducible release procedure.
- Qualified legal review of LEGAL.md, publisher identity and applicable jurisdictions;
  corresponding-source/license distribution review for the complete binary bundle.
- Installed-disk reboot, hardware, update and interrupted-transaction recovery tests.
- Independent reviewer designation and organization/account access/2FA review.

Do not interpret an empty automated alert list as proof of no vulnerabilities.
