#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Drive the real SDDM greeter via QEMU keyboard input, including failed login."""
import json,socket,sys,time
from pathlib import Path
out=Path(sys.argv[1]);sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
for _ in range(180):
 try:sock.connect(str(out/'qmp.sock'));break
 except (FileNotFoundError,ConnectionRefusedError):time.sleep(1)
f=sock.makefile('rwb')
def call(command,arguments=None):
 f.write((json.dumps({'execute':command,'arguments':arguments or {}})+'\n').encode());f.flush()
 while True:
  data=json.loads(f.readline())
  if 'error' in data:raise RuntimeError(data['error'])
  if 'return' in data:return data['return']
f.readline();call('qmp_capabilities')
def key(code):
 call('send-key',{'keys':[{'type':'qcode','data':code}]});time.sleep(.12)
def text(value):
 for c in value:key(c)
def screenshot(name):call('screendump',{'filename':str(out/name.replace('.ppm','.png')),'format':'png'})
# Keep boot-stage evidence without modifying boot timing or disabling the splash.
for n in range(1,145):
 time.sleep(1)
 if n % 2 == 0 and n <= 60:screenshot(f'boot-{n}.png')
 if (out/'greeter-ready').exists():break
screenshot('login-wait.ppm')
assert (out/'greeter-ready').exists(), 'SDDM greeter did not start'
time.sleep(4);screenshot('login.ppm')
text('stratagem');key('tab');text('wrong');key('ret')
time.sleep(4);screenshot('login-rejected.ppm')
assert not (out/'desktop-started').exists(), 'Invalid password entered desktop'
text('stratagem');key('ret')
for _ in range(120):
 if (out/'desktop-started').exists():break
 time.sleep(1)
assert (out/'desktop-started').exists(), 'Valid login did not enter desktop'
(out/'login-result.txt').write_text('Real SDDM: incorrect password rejected; stratagem login entered desktop.\n')
f.close();sock.close()
