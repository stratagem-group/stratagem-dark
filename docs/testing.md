# Verification scope

## Automated checks

`python3 -m unittest discover -s tests -v` runs 30 tests covering graph resolution,
profile unions, invalid and conflicting metadata, reproducible plans, staged file
hashes/modes, overwrite and symlink guards, injected write failure cleanup, and CLI
contracts. Live apply and ISO builds are explicitly tested to fail closed.

For independent schema checks:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python tests/validate_schemas.py
```

CI runs these on Ubuntu 24.04, checks Bash syntax, compares two generated plans,
and stages a core overlay. GitHub-hosted checks do not prove Arch package installation
or desktop compatibility. Test fixtures never call a package manager or security tool.

## Evidence for the initial scaffold

Locally verified on macOS with Python 3.14: 30 passing tests, JSON Schema validation,
and shell syntax checks. This demonstrates the host-independent planning/staging
contract only. The [initial hosted CI run](https://github.com/stratagem-group/stratagem-dark/actions/runs/36043010829)
passed on Ubuntu 24.04, including schema validation, all 30 tests and the staging smoke test.

Not yet performed: a real Arch bootstrap, package availability/license review for the
candidate set, dependency locking, desktop session launch, hardware support, failure
recovery of a package transaction, or ISO boot. Those are milestone gates in ROADMAP.md.
