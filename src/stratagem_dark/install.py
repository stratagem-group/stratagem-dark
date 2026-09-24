# SPDX-License-Identifier: MIT
"""Explicitly trusted offline testing-bundle installation; no remote script execution."""
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import shutil
import subprocess
import tempfile
from .core import ValidationError, require, canonical


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_file(root, relative):
    value = PurePosixPath(relative)
    require(not value.is_absolute() and '..' not in value.parts and value.parts,
            'unsafe manifest path')
    path = root.joinpath(*value.parts)
    require(all(not p.is_symlink() for p in (path, *path.parents)), 'symlink in bundle')
    require(path.is_file(), f'missing bundle file: {relative}')
    return path


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def verify_bundle(directory, fingerprint):
    require(re.fullmatch(r'[A-Fa-f0-9]{40}', fingerprint or '') is not None,
            'supply the independently obtained 40-character release key fingerprint')
    root = Path(directory).resolve()
    public = safe_file(root, 'release-key.asc')
    manifest_path = safe_file(root, 'manifest.json')
    signature = safe_file(root, 'manifest.json.asc')
    with tempfile.TemporaryDirectory(prefix='stratagem-verify-') as tmp:
        os.chmod(tmp, 0o700)
        command = ['gpg', '--homedir', tmp, '--batch']
        run(command + ['--import', str(public)], capture_output=True)
        keylist = run(command + ['--with-colons', '--list-keys'], capture_output=True, text=True).stdout
        primary = next((line.split(':')[9] for line in keylist.splitlines() if line.startswith('fpr:')), '')
        require(primary == fingerprint.upper(), 'release key fingerprint mismatch')
        status = run(command + ['--status-fd', '1', '--verify', str(signature), str(manifest_path)], capture_output=True, text=True).stdout
        require(any(line.startswith('[GNUPG:] VALIDSIG ' + primary + ' ') for line in status.splitlines()),
                'release manifest signature does not match trusted key')
    data = json.loads(manifest_path.read_text())
    require(data.get('schema_version') == 1 and data.get('product') == 'STRATAGEM DARK', 'unsupported bundle')
    require(data.get('architecture') == 'x86_64' and data.get('release_class') == 'testing', 'unsupported release class')
    require(isinstance(data.get('files'), dict) and isinstance(data.get('packages'), list) and data['packages'], 'invalid manifest')
    for name, checksum in data['files'].items():
        require(isinstance(checksum, str) and re.fullmatch('[a-f0-9]{64}', checksum), 'invalid digest')
        require(digest(safe_file(root, name)) == checksum, f'checksum mismatch: {name}')
    seen = set()
    for package in data['packages']:
        require(package['name'] not in seen, 'duplicate package')
        seen.add(package['name'])
        require(package['file'] in data['files'] and package['signature'] in data['files'], 'unlocked package or signature')
        require(package['sha256'] == data['files'][package['file']], 'package checksum mismatch')
    return root, data


def setup_user(runtime=Path('/usr/share/stratagem'), home=None, apply=False):
    require(os.geteuid() != 0, 'desktop setup must run as the target user, not root')
    home = Path(home or Path.home()).resolve()
    conflicts, added = [], []
    targets = []
    for p in sorted((runtime / 'config').rglob('*')):
        if p.is_file():
            targets.append((p, home / '.config' / p.relative_to(runtime / 'config')))
    selected = home / '.local/state/stratagem/current/theme.name'
    for p in sorted((runtime / 'themes/phosphor').rglob('*')):
        if p.is_file() and not selected.exists():
            targets.append((p, home / '.local/state/stratagem/current/theme' / p.relative_to(runtime / 'themes/phosphor')))
    for source, target in targets:
        require(all(not p.is_symlink() for p in (target, *target.parents)), 'symlink in user configuration path')
        if target.exists():
            if target.read_bytes() != source.read_bytes():
                conflicts.append(str(target))
            continue
        added.append(str(target))
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation, so racing edits are never overwritten.
            with target.open('xb') as stream:
                stream.write(source.read_bytes())
            target.chmod(0o600)
    return {'created' if apply else 'would_create': added, 'preserved_existing': conflicts}


def install_bundle(directory, fingerprint, username, apply=False):
    root, manifest = verify_bundle(directory, fingerprint)
    require(re.fullmatch(r'[a-z_][a-z0-9_-]*', username or '') is not None, 'valid existing username required')
    user = pwd.getpwnam(username)
    require(user.pw_uid >= 1000 and user.pw_dir.startswith('/home/'), 'target must be a normal /home user')
    result = {'product': 'STRATAGEM DARK', 'version': manifest['version'], 'packages': len(manifest['packages']),
              'user': username, 'apply': apply}
    if not apply:
        return result
    require(os.geteuid() == 0, 'installation requires root')
    import platform
    require(platform.system() == 'Linux' and platform.machine() == 'x86_64', 'Arch Linux x86_64 required')
    release = Path('/etc/os-release').read_text()
    require(re.search(r'^ID=[\"\']?arch[\"\']?$', release, re.M) is not None, 'clean Arch base required')
    require(not Path('/var/lib/pacman/db.lck').exists(), 'pacman is already running')
    require(shutil.disk_usage('/').free > 6 * 1024**3, 'at least 6 GiB free space required')
    # Copy verified inputs to root-owned storage before privileged consumption.
    state = Path('/var/lib/stratagem-dark'); state.mkdir(mode=0o700, exist_ok=True)
    require(not state.is_symlink() and state.stat().st_uid == 0
            and state.stat().st_mode & 0o077 == 0, 'unsafe state directory')
    with (state / 'install.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with tempfile.TemporaryDirectory(prefix='release-', dir=state) as temp:
            trusted = Path(temp)
            for relative in (*manifest['files'], 'manifest.json', 'manifest.json.asc'):
                source = safe_file(root, relative)
                dest = trusted / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
            trusted, manifest = verify_bundle(trusted, fingerprint)
            journal = {'version': manifest['version'], 'source_commit': manifest['source_commit'], 'phase': 'verified'}
            def checkpoint(phase):
                journal['phase'] = phase
                tmp = state / 'transaction.json.tmp'
                tmp.write_text(canonical(journal)); tmp.replace(state / 'transaction.json')
            checkpoint('verified')
            run(['pacman-key', '--add', str(trusted / 'release-key.asc')])
            run(['pacman-key', '--lsign-key', fingerprint.upper()])
            for name in ('blackarch.gpg', 'blackarch-trusted', 'blackarch-revoked'):
                relative = 'trust/keyrings/' + name
                require(relative in manifest['files'], 'BlackArch trust is not locked')
                shutil.copyfile(trusted / relative, Path('/usr/share/pacman/keyrings') / name)
            run(['pacman-key', '--populate', 'blackarch'])
            archives = [str(trusted / p['file']) for p in manifest['packages']]
            for p in manifest['packages']:
                run(['pacman-key', '--verify', str(trusted / p['signature']), str(trusted / p['file'])], capture_output=True)
            checkpoint('packages-started')
            config = trusted / 'offline-pacman.conf'
            config.write_text('[options]\nArchitecture = x86_64\nSigLevel = Required DatabaseOptional\nLocalFileSigLevel = Required\n')
            run(['unshare', '--net', '--', 'pacman', '--config', str(config), '-U', '--needed', '--noconfirm', *archives])
            installed = dict(line.split(' ', 1) for line in run(['pacman', '-Q'], capture_output=True, text=True).stdout.splitlines())
            require(all(installed.get(p['name']) == p['version'] for p in manifest['packages']), 'installed version mismatch')
            checkpoint('packages-verified')
            run(['runuser', '-u', username, '--', 'dark', 'setup', '--apply'])
            run(['systemctl', 'enable', 'NetworkManager.service', 'sddm.service', 'stratagem-dark-firewall.service'])
            checkpoint('complete')
            result['next'] = 'Reboot and select the STRATAGEM DARK session.'
    return result
