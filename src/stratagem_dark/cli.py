# SPDX-License-Identifier: MIT
"""Source-checkout command line interface for STRATAGEM DARK."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import subprocess
from .install import verify_bundle, setup_user, install_bundle

from .core import Project, ValidationError, canonical


def host_checks():
    release = {}
    path = Path('/etc/os-release')
    if path.is_file():
        for line in path.read_text().splitlines():
            key, separator, value = line.partition('=')
            if separator:
                release[key] = value.strip('"')
    checks = {
        'linux': platform.system() == 'Linux',
        'arch_linux': release.get('ID') == 'arch',
        'x86_64': platform.machine() == 'x86_64',
        'pacman_available': shutil.which('pacman') is not None,
        'systemd_running': Path('/run/systemd/system').is_dir(),
        'unprivileged_user': os.geteuid() != 0,
    }
    return {'product': 'STRATAGEM DARK', 'checks': checks,
            'ready_for_live_apply': False, 'reason': 'Live apply is not implemented.'}


def main(argv=None, root=None):
    parser = argparse.ArgumentParser(prog='dark', description='STRATAGEM DARK developer CLI')
    parser.add_argument('--version', action='version', version='STRATAGEM DARK 0.2.0-alpha1')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('about', help='product and attribution')
    setup = sub.add_parser('setup', help='seed missing desktop defaults without overwriting user files')
    setup.add_argument('--apply', action='store_true')
    for action in ('verify-bundle', 'install'):
        command = sub.add_parser(action, help='verify or install an explicitly trusted offline testing bundle')
        command.add_argument('--bundle', required=True)
        command.add_argument('--key-fingerprint', required=True)
        if action == 'install':
            command.add_argument('--user', required=True)
            command.add_argument('--apply', action='store_true')
    sub.add_parser('validate', help='validate catalog and profile graph')
    profile = sub.add_parser('profile', help='inspect profiles')
    profile.add_argument('action', choices=['list', 'show'])
    profile.add_argument('name', nargs='?')
    tools = sub.add_parser('tools', help='list candidate tools; never execute them')
    tools.add_argument('--profile', default='full')
    tools.add_argument('--json', action='store_true')
    doctor = sub.add_parser('doctor', help='read-only host diagnostics')
    doctor.add_argument('--json', action='store_true')
    for command in ('plan', 'bootstrap'):
        p = sub.add_parser(command, help='produce a deterministic development plan')
        p.add_argument('--profile', default='core')
        p.add_argument('--json', action='store_true')
        if command == 'bootstrap':
            group = p.add_mutually_exclusive_group()
            group.add_argument('--dry-run', action='store_true')
            group.add_argument('--stage', metavar='NEW_DIRECTORY')
            group.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'about':
            print('STRATAGEM DARK 0.2.0-alpha1\nOpen security workstation.\nDesktop derived from Omarchy (MIT), copyright David Heinemeier Hansson.\nIncludes separately licensed Arch and selected BlackArch packages.\nhttps://github.com/stratagem-group/stratagem-dark')
            return 0
        if args.command == 'setup':
            print(canonical(setup_user(apply=args.apply)), end='')
            return 0
        if args.command == 'verify-bundle':
            _, manifest = verify_bundle(args.bundle, args.key_fingerprint)
            print(f"Verified STRATAGEM DARK {manifest['version']}: {len(manifest['packages'])} packages")
            return 0
        if args.command == 'install':
            print(canonical(install_bundle(args.bundle, args.key_fingerprint, args.user, args.apply)), end='')
            return 0
        if args.command == 'bootstrap' and args.apply:
            raise ValidationError('Live apply is not implemented. Use --dry-run or --stage; see docs/bootstrap.md.')
        if args.command == 'doctor':
            report = host_checks()
            print(canonical(report) if args.json else '\n'.join(
                ['STRATAGEM DARK host diagnostics'] +
                [f"{k}: {'yes' if v else 'no'}" for k, v in report['checks'].items()] +
                [report['reason']]), end='\n' if not args.json else '')
            return 1  # Not ready, even on a valid Arch machine.
        project = Project(root or Path(__file__).resolve().parents[2])
        if args.command == 'validate':
            print(f'STRATAGEM DARK: valid ({len(project.tools)} tools, {len(project.profiles)} profiles)')
        elif args.command == 'profile':
            if args.action == 'list':
                if args.name:
                    raise ValidationError('profile list takes no name')
                print('\n'.join(sorted(project.profiles)))
            else:
                if not args.name:
                    raise ValidationError('profile show requires a name')
                print(canonical({'profile': args.name, 'tools': project.resolve(args.name)}), end='')
        elif args.command == 'tools':
            selected = project.resolve(args.profile)
            print(canonical(selected) if args.json else '\n'.join(
                f"{t['id']}: {t['repository']}/{t['package']} [{t['license_review']}]" for t in selected),
                end='' if args.json else '\n')
        else:
            plan = project.stage(args.profile, args.stage) if args.command == 'bootstrap' and args.stage else project.plan(args.profile)
            if args.json:
                print(canonical(plan), end='')
            else:
                print(f"STRATAGEM DARK — {args.profile} — plan only")
                print(f"Plan SHA-256: {plan['plan_sha256']}")
                print('Packages: ' + ', '.join(t['repository'] + '/' + t['package'] for t in plan['tools']))
                print('Package artifacts are not locked; live installation is disabled.')
                if args.command == 'bootstrap' and args.stage:
                    print(f'Staged review files: {args.stage}')
        return 0
    except (ValidationError, OSError, json.JSONDecodeError, subprocess.CalledProcessError, KeyError) as error:
        print(f'dark: {error}', file=sys.stderr)
        return 2
