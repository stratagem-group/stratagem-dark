#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json,subprocess,sys
from pathlib import Path
commands=json.load(open('/usr/lib/stratagem-dark/catalog/launchers.json'))
report={}
for name,argv in commands.items():
    if name=='wireshark':argv=['wireshark','--version']
    result=subprocess.run(['unshare','--net','--',*argv],capture_output=True,text=True,timeout=30)
    output=result.stdout+result.stderr
    assert result.returncode in (0,1), (name,result.returncode,output)
    assert len(output.strip())>0, (name,output)
    assert not any(s in output for s in ('error while loading shared libraries','ModuleNotFoundError','Traceback (most recent call last)')), (name,output)
    report[name]={'returncode':result.returncode,'output':output[:3000]}
Path(sys.argv[1]).write_text(json.dumps(report,indent=2))
