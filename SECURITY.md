# Security policy

STRATAGEM DARK is pre-alpha. There are no supported production releases yet.
The current planner and stager do not execute security tools or install packages.

Use the repository's **Security → Report a vulnerability** private reporting channel
when it is enabled. Publication maintainers must enable private vulnerability reporting
before promoting the project. Until then, do not place exploit details, credentials,
or sensitive logs in public issues; open a minimal request for a private contact path.
No security email address or response-time guarantee has been established yet.

Include affected commit/version, reproduction in an isolated environment, expected
behavior, impact, and redacted logs. Never test against a third party without permission.
Issues involving upstream tools should also be reported through their upstream policy.

Trust boundaries: catalog data is validated without execution; staging runs unprivileged;
package installation will require signed artifacts and explicit repository trust;
user configuration is separate from system configuration. No root remote-script piping,
disabled signature checks, default network listeners, or automatic privilege grants.

Research/malware labs must use isolated disposable VMs with restricted networking;
installing a tool or selecting `research` does not create containment. No claims of
anonymity, forensic soundness, certification, or production hardening are made.
