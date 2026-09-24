#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Assemble an original package layout around the attributed upstream desktop."""
from pathlib import Path
import shutil,sys
repo=Path(__file__).resolve().parents[1]
root=Path(sys.argv[1]); root.mkdir(parents=True,exist_ok=True)
def copy(src,dest):
 target=root/dest;target.parent.mkdir(parents=True,exist_ok=True)
 if src.is_dir():shutil.copytree(src,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
 else:shutil.copy2(src,target)
def write(dest,text,mode=0o644):
 p=root/dest;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);p.chmod(mode)
copy(repo/'desktop/runtime','usr/share/stratagem')
for p in (repo/'desktop/runtime/bin').iterdir():copy(p,'usr/bin/'+p.name)
for directory in ('bin','src','profiles','catalog','schemas','bootstrap','desktop','config','branding'):
 copy(repo/directory,'usr/lib/stratagem-dark/'+directory)
for name in ('VERSION','LICENSE','THIRD_PARTY_NOTICES.md','LEGAL.md'):
 copy(repo/name,'usr/lib/stratagem-dark/'+name)
copy(repo/'branding','usr/share/stratagem-dark/branding')
copy(repo/'LICENSE','usr/share/licenses/stratagem-dark/LICENSE')
copy(repo/'LICENSES','usr/share/licenses/stratagem-dark/third-party')
write('usr/bin/dark','#!/bin/sh\nexec /usr/lib/stratagem-dark/bin/dark "$@"\n',0o755)
write('etc/profile.d/stratagem-dark.sh','export STRATAGEM_DARK_PATH=/usr/share/stratagem\n')
write('usr/share/uwsm/env.d/10-stratagem-dark','export STRATAGEM_DARK_PATH=/usr/share/stratagem\nexport TERMINAL=foot\nexport EDITOR=nano\n')
write('usr/share/wayland-sessions/stratagem-dark.desktop','[Desktop Entry]\nName=STRATAGEM DARK\nComment=STRATAGEM DARK security workstation\nExec=/usr/bin/stratagem-dark-session\nType=Application\nDesktopNames=Hyprland\n')
write('usr/bin/stratagem-dark-session','''#!/bin/bash
set -euo pipefail
export STRATAGEM_DARK_PATH=/usr/share/stratagem
export XDG_CURRENT_DESKTOP=Hyprland
export XDG_SESSION_DESKTOP=Hyprland
export XDG_SESSION_TYPE=wayland
dark setup --apply
exec uwsm start -g -1 -e -D Hyprland hyprland.desktop
''',0o755)
write('usr/share/applications/stratagem-dark-tools.desktop','[Desktop Entry]\nType=Application\nName=STRATAGEM DARK Tools\nExec=foot dark desktop tool nmap\nIcon=utilities-terminal\nCategories=System;\n')

copy(repo/'config/firewall.nft','usr/share/stratagem-dark/firewall.nft')
write('etc/systemd/resolved.conf.d/90-stratagem-dark.conf','[Resolve]\nLLMNR=no\nMulticastDNS=no\n')
write('usr/lib/systemd/system/stratagem-dark-firewall.service','''[Unit]
Description=STRATAGEM DARK inbound firewall
DefaultDependencies=no
Before=network-pre.target
Wants=network-pre.target
After=systemd-modules-load.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/nft -f /usr/share/stratagem-dark/firewall.nft
ExecStop=/usr/bin/nft delete table inet stratagem_dark
[Install]
WantedBy=multi-user.target
''')

copy(repo/'LEGAL.md','usr/share/doc/stratagem-dark/LEGAL.md')

write('etc/NetworkManager/conf.d/90-stratagem-dark.conf','[connection]\nconnection.mdns=0\nconnection.llmnr=0\n')

write('usr/share/applications/stratagem-dark-setup.desktop','[Desktop Entry]\nType=Application\nName=STRATAGEM DARK Setup\nExec=foot dark desktop welcome\nIcon=preferences-system\nCategories=Settings;\n')

write('usr/share/stratagem-dark/optional-pacman.conf','[options]\nArchitecture = x86_64\nCheckSpace\nSigLevel = Required DatabaseOptional\nLocalFileSigLevel = Required\n[core]\nServer = https://archive.archlinux.org/repos/2026/09/23/$repo/os/$arch\n[extra]\nServer = https://archive.archlinux.org/repos/2026/09/23/$repo/os/$arch\n[blackarch]\nServer = https://ftp.halifax.rwth-aachen.de/blackarch/$repo/os/$arch\n')
write('usr/lib/stratagem-dark/install-optional-tool','''#!/usr/bin/python3 -I
import sys
sys.path.insert(0, '/usr/lib/stratagem-dark/src')
from stratagem_dark.optional_tools import install
if len(sys.argv) != 2: raise SystemExit('One catalog tool ID required')
try: raise SystemExit(install(sys.argv[1]))
except (ValueError, OSError) as error: raise SystemExit(str(error))
''',0o755)
write('usr/share/polkit-1/actions/org.stratagem.dark.install-tool.policy','''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN" "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig><action id="org.stratagem.dark.install-tool">
<description>Install a supported STRATAGEM DARK tool</description>
<message>Authenticate to install this signed tool and its dependencies.</message>
<defaults><allow_any>no</allow_any><allow_inactive>no</allow_inactive><allow_active>auth_self</allow_active></defaults>
<annotate key="org.freedesktop.policykit.exec.path">/usr/lib/stratagem-dark/install-optional-tool</annotate>
</action></policyconfig>
''')
