# Future executable phases

Preflight → resolve → verify artifacts → packages → system config → user config →
verify. Contracts, resume semantics and acceptance gates are in `docs/bootstrap.md`.
The current installer only resolves plans and stages defaults. Avoid empty executable
phase scripts that could falsely report a successful installation.
