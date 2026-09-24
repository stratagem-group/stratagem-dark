# Omarchy desktop parity review — 2026-09-24

## Product decision

STRATAGEM DARK should preserve the Omarchy desktop experience, with independent
STRATAGEM DARK branding and an additive BlackArch security layer. Upstream menus,
shortcuts, theme switching, default-agent selection and everyday settings are the
baseline. A terminal wizard is not an adequate replacement for an existing panel.
Keep the Phosphor/CRT identity as the default, while supporting theme selection.

This is a source and issue review, not a claim that the corrections below are
implemented. The tested alpha2 ISO remains unchanged. Its successful VM checks did
not establish desktop parity or physical Wi-Fi usability.

## Exact sources reviewed

- Existing imported desktop: `28ceaae70ebac3a0edcc21f2faa77a90dc6d404c`.
- [Stable v4.0.4](https://github.com/omacom/omarchy/releases/tag/v4.0.4):
  `c668141e9c42b13c80c9ca4ea108e11708c5e8a5`.
- Default branch `quattro`, fetched during this review:
  `93e8cd56b19df756a6435b0c0e8ed5073d192c36`.
- STRATAGEM DARK alpha2 source: `494126043550c59c3ee8ded5d1e2f4c48e52bea0`.

Examined the stable and current agent launcher/default selection, theme engine and
picker, theme manual, shell configuration, and network panel, against our runtime
and Python desktop workflows. Existing imports remain at their recorded commit;
no upstream code was imported by this review. Use stable behavior as the comparison
baseline and review newer fixes individually, rather than silently updating the
entire desktop to a moving branch or downgrading the existing imported tree.

## Confirmed gaps and correction requirements

| Area | Upstream behavior / source | Current STRATAGEM DARK gap | Required correction |
| --- | --- | --- | --- |
| Wi-Fi | `shell/plugins/panels/network/Panel.qml`: inline password, direct connection and saved-network state | Our `openPasswordPrompt` and `connectDirectly` launch `foot dark desktop wifi`, close the panel and require another network selection | Keep selection and password entry inside the panel; connect/reconnect there; reserve diagnostics and advanced settings for separate actions |
| Default agent | `bin/omarchy-default-agent`, `bin/omarchy-agent`, `default/omarchy/omarchy-menu.jsonc`: select default once, then direct launch | `desktop.py:agents()` repeats agent/workspace/settings selection on every launch | Separate setup from launch; remember client and model; launch directly in the chosen workspace; use the client's native provider authentication |
| Provider/model choice | Agent clients own provider credentials and model access | Our provider/model menu sits behind repeated workspace setup | First-use flow: choose client, native sign-in, ready to use; keep model switching discoverable without repeating onboarding; cancellation must leave a usable desktop |
| Themes | `bin/omarchy-theme-switcher`, `bin/omarchy-theme-set`, `manual/06-themes.md`: visual picker and coordinated theme application | Only Phosphor is shipped; image picker/background plugins are disabled; no Style menu or theme shortcut | Restore the picker, theme application dependencies and supported app templates together; Style > Theme and Super+Ctrl+Shift+Space; preserve Phosphor as default |
| Shell integration | `config/omarchy/shell.json`: agent status, tray, indicators and settings form one desktop | Our configuration disables agent status and many other plugins; helpers were imported selectively | Audit each disabled plugin and its dependencies; restore useful desktop features with working actions, rather than merely displaying more icons |
| Keyboard workflow | Upstream keybindings and menu actions are coordinated | Local overrides diverged, with prior duplicate actions and incomplete discovery | Retain familiar upstream bindings where possible; explicitly document Stratagem additions and collisions; verify every advertised binding |
| Security tools | Separate BlackArch packages and groups | Alpha2 has 26 launchers and a much larger optional catalog, but catalog availability is not installed functionality | Keep comprehensive searchable discovery and optional installs; add curated working profiles without burying ordinary desktop settings |

The stable theme manual describes 22 themes. That does not mean 22 themes or their
artwork are currently shipped or cleared for redistribution in STRATAGEM DARK.
Review assets and notices individually, record imports, and generate independent
previews where appropriate. Theme support must include all shipped supported apps,
not promise applications we do not package.

## Feedback reviewed and acceptance consequences

These are upstream reports, not independently reproduced findings on our image.
They are selected regression cases, not a representative user-satisfaction survey.

| Report | Relevance and required check |
| --- | --- |
| [#11791: enterprise Wi-Fi profiles and errors](https://github.com/omacom/omarchy/issues/11791) | Reuse existing profiles, preserve certificate/domain settings, and distinguish timeout from bad credentials. Do not silently replace enterprise configuration with a minimal PEAP profile. |
| [#13054: network identity exposure](https://github.com/omacom/omarchy/issues/13054) | Review DHCP hostname and address privacy defaults separately from connection usability. The suggested drop-in is not yet adopted; test compatibility before changing identity behavior. |
| [#2595: opening Wi-Fi disconnects](https://github.com/omacom/omarchy/issues/2595) | Historical 3.1-era report, not proof of a current v4 defect. Opening/closing the panel and scanning must not interrupt an established connection. |
| [#13124: theme switching and tmux transparency](https://github.com/omacom/omarchy/issues/13124) | Verify theme changes in existing terminal windows and tmux panes, including transparency. |
| [#13125: wallpaper transition](https://github.com/omacom/omarchy/issues/13125) | Inspect real rendered transitions, not only theme-file output or animation timers. |
| [#13131: stale theme test expectation](https://github.com/omacom/omarchy/issues/13131) | Do not copy test assertions blindly: assert actual editor/theme reload behavior and configuration preservation. |
| [#13158: Codex status flicker](https://github.com/omacom/omarchy/issues/13158) | A status timeout must not be treated as signed-out state; preserve last-known data with a stale indicator and retry. |

Broadcom MacBook reports were also reviewed. They do not establish the cause of
Wi-Fi trouble on the user's Lenovo X1, i7 eighth generation. Verify the actual PCI
adapter, firmware and connection logs on that machine before applying a driver quirk.

## Deliberate differences from upstream

- Keep full STRATAGEM DARK product branding, original logo and default artwork;
  retain MIT notices and upstream attribution in legal/source documentation.
- Keep normal agent command approvals. Stable `bin/omarchy-agent` enables automatic
  approval modes for several clients; those flags are not part of our parity goal.
- Keep agent credentials in each client's native credential store; no credential
  collection in our settings or images. Sign-in and paid-model execution require
  real user-account testing; provider names alone do not establish working access.
- Resolve graphical Wi-Fi creation as a normal user's own connection. Our current
  `settings.modify.own` AUTH_SELF override adds a login-password prompt. Review it
  against the packaged NetworkManager policy and Quickshell connection ownership;
  do not grant blanket system-profile privileges to work around the GUI.
- Keep signed, version-recorded packages and our release verification. Upstream
  client installers, updater, custom kernel, external services and migrations need
  individual integration review; a branding substitution is not sufficient.
- Treat downloaded themes as untrusted inputs. Preserve upstream restrictions on
  executable configuration rather than allowing arbitrary theme code at login.

## Implementation order and evidence required

All items below are pending after this review.

1. **Native networking:** inline personal Wi-Fi connection; saved reconnect; wrong
   password and cancellation; scan without disconnection; normal-user permissions;
   no secrets in process arguments or logs. Exercise simulated wireless in Linux
   where possible, then physical Lenovo X1 Wi-Fi, suspend and reconnect.
2. **Agent setup/launch:** one-time default choice; native provider sign-in; model
   change; direct second launch; preserved approvals; cancellation and offline errors.
   Distinguish automated UI tests from real authenticated model execution.
3. **Themes and shell:** import/review the complete picker/application dependency
   chain, expose Style and shortcut, test several light/dark palettes, existing
   terminals, lock screen, menus and session restart. Preserve user overrides.
4. **BlackArch integration:** keep desktop settings familiar; test curated tools,
   optional install failures, catalog search, and scoped agent workspaces separately.
5. **Release gate:** refresh file-level provenance; source tests and UEFI graphical
   acceptance; produce a newly identified ISO and checksums only after those pass.
   A passing boot screenshot alone is insufficient. Persistent disk installation
   remains a separate outstanding requirement and must not be claimed complete.

For each restored feature, track upstream source paths, pinned commit, dependencies,
local patches and acceptance evidence. Prefer upstream fixes for generic defects.
An unresolved hardware/provider check must remain visible in release notes.
