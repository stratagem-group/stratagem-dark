# Agent-assisted assessments

STRATAGEM DARK's alpha2 candidate includes OpenCode, an interactive agent with
terminal tools. Sign in to a model provider inside OpenCode; no paid model access
or API credentials are bundled. Codex and Claude can be selected when installed
separately. The original Omarchy agent usage panel is not yet restored.

- **Super+K**: shortcut help.
- **Super+A**: create a new authorized engagement.
- **Super+Shift+A**: choose an installed agent and open an existing workspace.
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
