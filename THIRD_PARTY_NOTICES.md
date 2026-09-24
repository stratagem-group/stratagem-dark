# Third-party notices

STRATAGEM DARK now includes an adapted subset of the Omarchy desktop under MIT.
Copyright (c) David Heinemeier Hansson. The complete notice is preserved in
[LICENSES/Omarchy-MIT.txt](LICENSES/Omarchy-MIT.txt) and shipped in the desktop package.

`provenance/imports.json` records every imported source file, upstream commit,
original SHA-256, adapted destination/hash, and modifications. Imported shell,
Hyprland defaults and helpers live under `desktop/runtime/`. Plugin author credits
are retained. Product names, namespace, menu, startup policy and artwork are adapted.
Upstream logos, icon font, wallpapers, updater, provisioning and installer are not imported.

The remaining original code, configuration and artwork use the root MIT license.
This license does not replace the licenses of external packages.

Arch Linux packages, including Hyprland, Quickshell, Foot and archiso, retain their
own licenses. The build composes archiso's packaged releng profile under GPL-3.0-or-later;
it does not relicense archiso. The generated inventory records package versions,
checksums and declared licenses. Package-provided notices stay in the live filesystem.

BlackArch packages are separately licensed software; BlackArch's package repository
COPYING is BSD-3-Clause and is not a blanket software license. The testing selection
includes capa; WhatWeb is deferred pending deterministic offline packaging. The BlackArch keyring is retrieved and verified as a build
input; no strap script is executed. See the release trust documentation for limitations.

CI uses pinned GitHub Actions and a pinned Arch Linux build image as external build
dependencies. The STRATAGEM DARK source checkout and import provenance accompany testing
artifacts; this is not a complete corresponding-source archive for every package.
Version-specific source and notice obligations must be reviewed before release
promotion. A testing label does not waive any third-party license obligation.

See [LEGAL.md](LEGAL.md) for project warranty, liability and responsible-use disclosures.
