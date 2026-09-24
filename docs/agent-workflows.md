# Agent-assisted assessments

STRATAGEM DARK's alpha3 candidate includes OpenCode, an interactive agent with
terminal tools. Super+Shift+A chooses a default client on first use and offers native
provider sign-in, then opens that client directly on later launches. Setup > Default
agent / provider / model offers sign-in, a searchable model picker and workspace
settings without repeating onboarding. No paid model access
or API credentials are bundled. Codex and Claude can be selected when installed
separately. The original Omarchy agent usage panel is not yet restored.

- **Super+K**: shortcut help.
- **Super+T**: installed-tool cheat sheet and optional signed package installation.
- **Super+A**: create a new authorized engagement.
- **Super+Shift+A**: launch the saved agent (first use opens onboarding).
- **Super+Space**: applications, setup, security tools and system menu.

New engagements have a scope document, agent instructions, an inventory of
installed command-line tools, and private evidence/notes/reports directories.
OpenCode can discover tools, propose commands, run commands after approval,
interpret output and draft findings. The initial prompt asks it to clarify missing
scope before active testing. For example, give it an owned lab and ask for an
inventory and report; no target or authorization is assumed by the distribution.

This is integration with the agent's existing terminal execution, not a separate
custom MCP service. Approval prompts remain on; no automatic root access, permission
bypass flags or public network agent server are enabled. Agent instructions are not
a sandbox or technical target allowlist. Tools requiring root, capture permissions,
wireless monitor support or a GPU need those prerequisites supplied separately.

A live session loses credentials and evidence on reboot. Persistent installation is
still a separate work item. Authentication and end-to-end model/tool calls require
a user account and lab test: the build checks binaries, local workspace generation
and permission-preserving launch arguments without using paid APIs or credentials.

Upstream interface references: [OpenCode CLI](https://opencode.ai/docs/cli/) and
[permissions](https://opencode.ai/docs/permissions/). Imported Omarchy code keeps
its MIT notice; engagement scaffolding and launcher integration are Stratagem-owned.


The cheat sheet includes the full captured BlackArch repository catalog (5,050 packages, including dependencies, across 53 groups), plus Arch add-ons. Its date and database hash are recorded in catalog/optional-tools-source.json. Category browsing and search separate installed packages from available packages.

Optional installs use the pinned Arch snapshot plus the current BlackArch mirror and system authentication. The narrow
polkit action permits an active local user to authenticate as themselves for catalog
installs only; it is not a general sudo grant. On the live image that credential is
the documented testing password. Changes disappear on live reboot. Installation can
need significant disk space and downloads. Optional tools are not all exercised by
the ISO smoke tests, and adding them changes the tested package set. The installer
uses full package synchronization instead of a partial upgrade; review its output.

BlackArch is rolling; catalog versions describe the captured metadata, while optional
installation resolves the mirror's currently available signed version. Thus optional
installs are not reproducible in the same way as the locked base bundle. Dependency
conflicts or missing archives fail without forced overwrites. Package availability
is not a compatibility, safety or legal certification. Review the installed version
and resulting package-manager output before using a newly added tool.

The model picker reads OpenCode’s live model catalog rather than hardcoding model names. A listed model may still require provider access, billing, or credentials. New engagements reuse the selected agent and its saved OpenCode model. Codex/Claude model selection remains in their native interface when separately installed.
