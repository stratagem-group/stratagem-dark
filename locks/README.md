# Release locks — not yet generated

There is deliberately no pretend package lock. A release lock must contain format
version, STRATAGEM DARK source commit, baseline image digest, architecture, repository
snapshot/DB digests, keyring artifacts and verified signer fingerprints, and every
package including transitive dependencies (name, exact version, repository, URL,
SHA-256, detached signature, license evidence). Sign the canonical lock itself.

Arch rolling mirrors and BlackArch current package names are not sufficient for
reproducibility. Establish a retained immutable artifact cache before live apply.
Plans hash source inputs for repeatability but do not pin package binaries.
