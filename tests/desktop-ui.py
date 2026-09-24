#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise real Gum dialogs in a controlling terminal without provider credentials."""
import fcntl,os,pty,select,signal,struct,sys,termios,time

def check(action, steps):
    pid,fd=pty.fork()
    if pid==0:
        os.environ['TERM']='xterm-256color'
        os.execvp('dark',['dark','desktop',action])
    fcntl.ioctl(fd,termios.TIOCSWINSZ,struct.pack('HHHH',40,140,0,0))
    transcript=b''
    try:
        for needle,keys in steps:
            deadline=time.monotonic()+30
            current=b''
            while needle.encode() not in current:
                if time.monotonic()>deadline:raise AssertionError((action,needle,current.decode(errors='replace')[-5000:]))
                if select.select([fd],[],[],1)[0]:
                    data=os.read(fd,65536)
                    if not data:raise AssertionError('Dialog exited before '+needle)
                    current+=data;transcript+=data
            os.write(fd,keys)
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            done,status=os.waitpid(pid,os.WNOHANG)
            if done:
                assert os.waitstatus_to_exitcode(status) in (0,130),status
                print(action+': interactive dialogs passed')
                return
            if select.select([fd],[],[],0.2)[0]:
                try:transcript+=os.read(fd,65536)
                except OSError:pass
        raise AssertionError('Dialog did not cancel cleanly')
    finally:
        try:os.killpg(pid,signal.SIGTERM)
        except ProcessLookupError:pass
        os.close(fd)
        print(transcript.decode(errors='replace'))

check('agents', [('Choose your coding agent',b'\r'),('Workspace directory',b'\r'),('Sign in to a provider',b'\x03')])
check('cheatsheet', [('BlackArch tool catalog',b'\r'),('Search tools',b'\x03')])
