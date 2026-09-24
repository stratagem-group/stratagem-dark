# Contributing to STRATAGEM DARK

Start with the roadmap and architecture. Keep changes small, modular, and suitable
for upstream contribution. Use the full product name in user-facing prose.

Run `./bin/dark validate` and `python3 -m unittest discover -s tests -v` before a PR.
CI also validates JSON Schema with `requirements-dev.txt`. No root or Arch host is
needed for these tests. Desktop session and package installation claims require
real Arch VM evidence, not a mocked package manager.

For a tool: add metadata with a stable ID, explicit repository/package, upstream URL,
license-review evidence, category and isolation policy; then reference it from a
profile. Do not import arbitrary package groups, execute PKGBUILDs during discovery,
or mark a license reviewed based solely on a repository label.

For copied code: follow `docs/licensing.md` and update the import register and notices.
Contributions use MIT for original work. Sign off commits (`git commit -s`) to affirm
you have the right to submit the work under the project's license. Retain all required
third-party notices. Never include credentials, real targets, or sensitive captures.

PRs should describe the problem, behavior change, tests, and any upstream relationship.
Report vulnerabilities using SECURITY.md. Be respectful and focus reviews on the work.

Contributions and examples should follow the [responsible-use notice](LEGAL.md). This
does not change contributor licensing or third-party license terms.
