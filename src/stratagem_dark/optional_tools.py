# SPDX-License-Identifier: MIT
"""Narrow privileged install entry point for the reviewed Arch add-on catalog."""
import json
import os
from pathlib import Path
import subprocess

ROOT=Path('/usr/lib/stratagem-dark')
CONFIG=Path('/usr/share/stratagem-dark/optional-pacman.conf')

def install(name):
    if os.geteuid()!=0: raise ValueError('System authorization is required.')
    catalog=json.loads((ROOT/'catalog/optional-tools.json').read_text())
    if name not in catalog: raise ValueError('Tool is not in the supported installation catalog.')
    package=catalog[name]['package']
    repository=catalog[name]['repository']
    if repository not in ('arch','blackarch'): raise ValueError('Unsupported repository.')
    import re
    if not re.fullmatch(r'[a-z0-9][a-z0-9+._-]*',package): raise ValueError('Invalid catalog package.')
    subprocess.run(['/usr/bin/pacman-key','--populate','stratagem-blackarch'],check=True,env={'PATH':'/usr/bin','LANG':'C.UTF-8'})
    # Fixed root-owned config and signed packages; no arbitrary URLs or commands.
    # Full synchronization avoids unsupported partial upgrades.
    return subprocess.call(['/usr/bin/pacman','--config',str(CONFIG),'-Syu','--needed','--noconfirm',('extra' if repository=='arch' else 'blackarch')+'/'+package],cwd='/',env={'PATH':'/usr/bin','LANG':'C.UTF-8'})
