#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check all bundled tool entry points without network access; retain every failure."""
import json, subprocess, sys
from pathlib import Path
commands = json.load(open('/usr/lib/stratagem-dark/catalog/launchers.json'))
report = {}
for name, argv in commands.items():
    if name == 'wireshark':
        argv = ['wireshark', '--version']
    try:
        result = subprocess.run(['unshare', '--net', '--', *argv], capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        passed = result.returncode in (0, 1) and bool(output.strip()) and not any(
            s in output for s in ('error while loading shared libraries', 'ModuleNotFoundError', 'Traceback (most recent call last)'))
        report[name] = {'passed': passed, 'returncode': result.returncode, 'output': output[:3000]}
    except (OSError, subprocess.TimeoutExpired) as error:
        report[name] = {'passed': False, 'error': str(error)}
Path(sys.argv[1]).write_text(json.dumps(report, indent=2))
failed = {name: result for name, result in report.items() if not result['passed']}
if failed:
    print(json.dumps(failed, indent=2), file=sys.stderr)
    sys.exit(1)
