#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline functional checks against generated local fixtures, as a normal user."""
import json,subprocess,tempfile,sys,http.server,threading
from pathlib import Path
results={}
def run(name,argv,expected):
 result=subprocess.run(argv,capture_output=True,text=True,timeout=60)
 assert result.returncode==0,(name,result.stderr)
 assert expected in result.stdout,(name,result.stdout)
 results[name]={'passed':True,'output':result.stdout[:2000]}
with tempfile.TemporaryDirectory() as d:
 p=Path(d);sample=p/'sample';sample.write_bytes(b'STRATAGEM_TEST_FIXTURE\n')
 rule=p/'rule.yar';rule.write_text('rule Fixture { strings: $a="STRATAGEM_TEST_FIXTURE" condition: $a }')
 run('yara',[ 'yara',str(rule),str(sample)],'Fixture')
 run('exiftool',['/usr/bin/vendor_perl/exiftool',str(sample)],'File Size')
 run('radare2',['r2','-q','-c','ps 22',str(sample)],'STRATAGEM_TEST_FIXTURE')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),http.server.BaseHTTPRequestHandler)
 threading.Thread(target=server.serve_forever,daemon=True).start()
 try:run('nmap',['nmap','-sT','-Pn','-p',str(server.server_port),'127.0.0.1'],'open')
 finally:server.shutdown();server.server_close()
Path(sys.argv[1]).write_text(json.dumps(results,indent=2)+'\n')
