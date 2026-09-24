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
    import re
    if not re.fullmatch(r'[a-z0-9][a-z0-9+._-]*',package): raise ValueError('Invalid catalog package.')
    # Fixed root-owned config; official signed snapshot only, no arbitrary URLs or commands.
    # Full synchronization avoids unsupported partial upgrades.
    return subprocess.call(['/usr/bin/pacman','--config',str(CONFIG),'-Syu','--needed','--noconfirm','extra/'+package],cwd='/',env={'PATH':'/usr/bin','LANG':'C.UTF-8'})
