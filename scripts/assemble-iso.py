#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compose the pinned archiso releng profile with STRATAGEM DARK live defaults."""
from pathlib import Path
import json,shutil,subprocess,sys
bundle=Path(sys.argv[1]); profile=Path(sys.argv[2]); signer=sys.argv[3]
repo=Path(__file__).resolve().parents[1]
shutil.copytree('/usr/share/archiso/configs/releng',profile,symlinks=True)
airoot=profile/'airootfs'
def write(path,text,mode=0o644):
 p=airoot/path;p.parent.mkdir(parents=True,exist_ok=True)
 if p.is_symlink():p.unlink()
 p.write_text(text);p.chmod(mode)
# Keep Arch boot machinery; replace the visible identity and remove its live-root login.
for p in profile.rglob('*'):
 if p.is_file() and not p.is_symlink():
  try:s=p.read_text()
  except UnicodeDecodeError:continue
  s=s.replace('Arch Linux','STRATAGEM DARK').replace('archlinux.org','github.com/stratagem-group/stratagem-dark')
  p.write_text(s)
for relative in ['etc/systemd/system/getty@tty1.service.d','etc/systemd/system/multi-user.target.wants/sshd.service','root/.automated_script.sh','root/.zlogin','etc/systemd/system/multi-user.target.wants/systemd-networkd.service','etc/systemd/system/multi-user.target.wants/iwd.service']:
 p=airoot/relative
 if p.is_dir() and not p.is_symlink():shutil.rmtree(p)
 elif p.exists() or p.is_symlink():p.unlink()
for p in (airoot/'etc/systemd/system').rglob('*'):
 if p.is_symlink() and any(x in p.name for x in ['reflector','sshd','cloud-init','cloud-config','cloud-final']):p.unlink()
packages=json.loads((bundle/'manifest.json').read_text())['packages']
(profile/'packages.x86_64').write_text('\n'.join(sorted(p['name'] for p in packages))+'\n')
# Using only the offline repository makes missing dependencies fail instead of drifting.
(profile/'pacman.conf').write_text(f'''[options]
Architecture = x86_64
SigLevel = Required DatabaseOptional
LocalFileSigLevel = Required
[stratagem-dark]
Server = file://{bundle}/repository
''')
(profile/'profiledef.sh').write_text('''#!/usr/bin/env bash
iso_name="stratagem-dark"
iso_label="STRATAGEM_020"
iso_publisher="STRATAGEM DARK"
iso_application="STRATAGEM DARK Testing Workstation"
iso_version="0.2.0-alpha1"
install_dir="arch"
buildmodes=('iso')
bootmodes=('uefi.systemd-boot')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '6' '-b' '1M')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:700"
  ["/usr/local/bin/stratagem-vm-check"]="0:0:755"
)
''')
# Explicit local-only test account. No remote login service, sudo grant or default root password.
password=subprocess.check_output(['openssl','passwd','-6','-salt','stratagem','stratagem'],text=True).strip()
write('etc/passwd','root:x:0:0:root:/root:/bin/bash\nstratagem:x:1000:1000:STRATAGEM DARK tester:/home/stratagem:/bin/bash\n')
write('etc/group','root:x:0:\nstratagem:x:1000:\n')
write('etc/shadow',f'root:!*:20000:0:99999:7:::\nstratagem:{password}:20000:0:99999:7:::\n',0o400)
write('etc/hostname','stratagem-dark\n')
write('etc/os-release','NAME="STRATAGEM DARK"\nPRETTY_NAME="STRATAGEM DARK 0.2.0-alpha1"\nID=stratagem-dark\nID_LIKE=arch\nVERSION_ID=0.2.0-alpha1\nHOME_URL="https://github.com/stratagem-group/stratagem-dark"\n')
write('etc/issue','STRATAGEM DARK 0.2.0-alpha1 — testing live system\\n\\l\n')
write('etc/motd','STRATAGEM DARK — testing release. Local login: stratagem / stratagem. No remote access enabled.\n')
write('etc/sddm.conf.d/stratagem-dark.conf','[Autologin]\nUser=stratagem\nSession=stratagem-dark.desktop\nRelogin=false\n')
write('etc/profile.d/stratagem-vm-rendering.sh','export AQ_ALLOW_SOFTWARE_RENDERER=1\n')
write('etc/modules-load.d/stratagem-vm.conf','qemu_fw_cfg\n9p\n9pnet_virtio\n')
write('etc/systemd/system/stratagem-vm-check.service','''[Unit]
Description=STRATAGEM DARK explicit QEMU testing harness
After=systemd-modules-load.service graphical.target
ConditionPathExists=/sys/firmware/qemu_fw_cfg/by_name/opt/stratagem/test/raw
[Service]
Type=oneshot
ExecStart=/usr/local/bin/stratagem-vm-check
TimeoutStartSec=300
[Install]
WantedBy=graphical.target
''')
copy=airoot/'usr/local/bin/stratagem-vm-check';copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/'tests/vm/live-check.sh',copy);copy.chmod(0o755)
for name,target in {'NetworkManager.service':'/usr/lib/systemd/system/NetworkManager.service','sddm.service':'/usr/lib/systemd/system/sddm.service','stratagem-vm-check.service':'/etc/systemd/system/stratagem-vm-check.service'}.items():
 p=airoot/'etc/systemd/system/graphical.target.wants'/name;p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(target)
p=airoot/'etc/systemd/system/default.target'
if p.exists() or p.is_symlink():p.unlink()
p.symlink_to('/usr/lib/systemd/system/graphical.target')
# Original license notices ship with the test image.
for source in [repo/'THIRD_PARTY_NOTICES.md',repo/'LICENSES/Omarchy-MIT.txt']:
 dest=airoot/'usr/share/doc/stratagem-dark'/source.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
print('Assembled original branding + upstream desktop +',len(packages),'locked packages')
