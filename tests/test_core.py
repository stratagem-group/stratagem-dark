# SPDX-License-Identifier: MIT
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from stratagem_dark.core import Project, ValidationError, canonical, sha256
from stratagem_dark.cli import main, host_checks


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name).resolve()
        self.root = self.parent / 'project'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', '.venv', 'build'))

    def tearDown(self):
        self.temp.cleanup()

    def edit(self, relative, transform):
        path = self.root / relative
        data = json.loads(path.read_text())
        transform(data)
        path.write_text(canonical(data))

    def test_full_is_union_without_duplicates(self):
        p = Project(self.root)
        expected = {t['id'] for name in ('operator', 'defender', 'research') for t in p.resolve(name)}
        self.assertEqual([t['id'] for t in p.resolve('full')], sorted(expected))

    def test_core_does_not_require_blackarch(self):
        self.assertEqual({t['repository'] for t in Project(self.root).resolve('core')}, {'arch'})

    def test_cycle_rejected(self):
        self.edit('profiles/core.json', lambda p: p.update(extends=['full']))
        with self.assertRaisesRegex(ValidationError, 'cycle'):
            Project(self.root)

    def test_unknown_parent_rejected(self):
        self.edit('profiles/core.json', lambda p: p.update(extends=['missing']))
        with self.assertRaisesRegex(ValidationError, 'unknown profile'):
            Project(self.root)

    def test_unknown_tool_rejected(self):
        self.edit('profiles/core.json', lambda p: p['tools'].append('missing'))
        with self.assertRaisesRegex(ValidationError, 'unknown tool'):
            Project(self.root)

    def test_duplicate_tool_rejected(self):
        self.edit('catalog/tools.json', lambda c: c['tools'].append(c['tools'][0].copy()))
        with self.assertRaisesRegex(ValidationError, 'duplicate tool'):
            Project(self.root)

    def test_duplicate_package_rejected(self):
        self.edit('catalog/tools.json', lambda c: c['tools'].append({**c['tools'][0], 'id': 'other'}))
        with self.assertRaisesRegex(ValidationError, 'duplicate package'):
            Project(self.root)

    def test_cross_repository_conflict_rejected(self):
        self.edit('catalog/tools.json', lambda c: c['tools'][-1].update(package='python'))
        with self.assertRaisesRegex(ValidationError, 'conflicting repositories'):
            Project(self.root)

    def test_untrusted_package_syntax_rejected(self):
        for package in ('--root=/tmp', 'git;touch /tmp/pwned', '../escape', '$(id)'):
            with self.subTest(package=package):
                self.edit('catalog/tools.json', lambda c: c['tools'][0].update(package=package))
                with self.assertRaises(ValidationError):
                    Project(self.root)

    def test_bad_shape_unknown_fields_and_types(self):
        original = (self.root / 'catalog/tools.json').read_text()
        for change in (lambda c: c.update(extra=True), lambda c: c.update(schema_version=True),
                       lambda c: c['tools'][0].update(description=[]),
                       lambda c: c['tools'][0].update(repository='aur'),
                       lambda c: c['tools'][0].update(license_review='approved')):
            (self.root / 'catalog/tools.json').write_text(original)
            self.edit('catalog/tools.json', change)
            with self.assertRaises(ValidationError):
                Project(self.root)

    def test_duplicate_json_keys_rejected(self):
        (self.root / 'profiles/core.json').write_text('{"id":"core","id":"full"}')
        with self.assertRaisesRegex(ValidationError, 'duplicate JSON'):
            Project(self.root)

    def test_duplicate_profile_selection_rejected(self):
        self.edit('profiles/core.json', lambda p: p['tools'].append('python'))
        with self.assertRaises(ValidationError):
            Project(self.root)

    def test_plan_is_identical_across_paths(self):
        p = Project(self.root).plan('full')
        self.assertEqual(p, Project(ROOT).plan('full'))
        expected = p.pop('plan_sha256')
        self.assertEqual(expected, sha256(canonical(p).encode()))
        self.assertFalse(p['packages_locked'])
        self.assertTrue(p['blockers'])

    def test_default_change_invalidates_plan(self):
        before = Project(self.root).plan('core')['plan_sha256']
        with (self.root / 'config/foot/foot.ini').open('a') as stream:
            stream.write('# changed\n')
        self.assertNotEqual(before, Project(self.root).plan('core')['plan_sha256'])

    def test_symlink_input_rejected(self):
        path = self.root / 'config/foot/foot.ini'
        path.unlink()
        path.symlink_to(ROOT / 'config/foot/foot.ini')
        with self.assertRaisesRegex(ValidationError, 'symlink'):
            Project(self.root).plan('core')

    def test_stage_hashes_modes_and_repeatability(self):
        p = Project(self.root)
        a, b = self.parent / 'a', self.parent / 'b'
        p.stage('core', a)
        p.stage('core', b)
        manifest = json.loads((a / 'manifest.json').read_text())
        self.assertEqual((a / 'manifest.json').read_bytes(), (b / 'manifest.json').read_bytes())
        for relative, entry in manifest['files'].items():
            path = a / relative
            self.assertEqual(sha256(path.read_bytes()), entry['sha256'])
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)
            self.assertEqual(path.read_bytes(), (b / relative).read_bytes())

    def test_existing_stage_is_never_overwritten(self):
        dest = self.parent / 'existing'
        dest.mkdir()
        (dest / 'precious').write_text('keep')
        with self.assertRaisesRegex(ValidationError, 'must not exist'):
            Project(self.root).stage('core', dest)
        self.assertEqual((dest / 'precious').read_text(), 'keep')

    def test_symlink_destination_and_parent_rejected(self):
        dest = self.parent / 'link'
        dest.symlink_to(self.parent / 'missing')
        with self.assertRaises(ValidationError):
            Project(self.root).stage('core', dest)
        linked_parent = self.parent / 'linked-parent'
        linked_parent.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValidationError, 'symlink'):
            Project(self.root).stage('core', linked_parent / 'stage')

    def test_root_execution_rejected(self):
        with patch('os.geteuid', return_value=0):
            with self.assertRaisesRegex(ValidationError, 'unprivileged'):
                Project(self.root).stage('core', self.parent / 'root-stage')

    def test_failed_stage_cleans_its_own_tree(self):
        dest = self.parent / 'failed'
        with patch.object(Path, 'write_bytes', side_effect=OSError('injected failure')):
            with self.assertRaisesRegex(OSError, 'injected'):
                Project(self.root).stage('core', dest)
        self.assertFalse(dest.exists())
        self.assertTrue(self.root.exists())

    def test_missing_parent_creates_nothing(self):
        dest = self.parent / 'absent' / 'stage'
        with self.assertRaisesRegex(ValidationError, 'parent must'):
            Project(self.root).stage('core', dest)
        self.assertFalse(dest.parent.exists())


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([str(ROOT / 'bin/dark'), *args], capture_output=True, text=True)

    def test_validate_and_json_plan(self):
        self.assertEqual(self.run_cli('validate').returncode, 0)
        result = self.run_cli('plan', '--profile', 'operator', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['profile'], 'operator')

    def test_profile_and_tools_commands(self):
        self.assertEqual(len(self.run_cli('profile', 'list').stdout.splitlines()), 5)
        result = self.run_cli('profile', 'show', 'research')
        self.assertEqual(json.loads(result.stdout)['profile'], 'research')
        self.assertEqual(self.run_cli('tools', '--profile', 'full').returncode, 0)
        self.assertNotEqual(self.run_cli('profile', 'show').returncode, 0)

    def test_unknown_profile_and_option_fail(self):
        self.assertEqual(self.run_cli('plan', '--profile', '../../etc').returncode, 2)
        self.assertEqual(self.run_cli('bootstrap', '--unknown').returncode, 2)

    def test_apply_fails_on_every_host(self):
        result = self.run_cli('bootstrap', '--apply')
        self.assertEqual(result.returncode, 2)
        self.assertIn('not implemented', result.stderr)

    def test_bootstrap_default_is_dry_run_from_arbitrary_cwd(self):
        result = subprocess.run([str(ROOT / 'bootstrap/install.sh'), '--json'],
                                cwd='/', text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['live_apply_supported'])

    def test_doctor_never_claims_readiness(self):
        self.assertFalse(host_checks()['ready_for_live_apply'])
        result = self.run_cli('doctor', '--json')
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['ready_for_live_apply'])

    def test_iso_builder_fails_closed(self):
        result = subprocess.run([str(ROOT / 'iso/build.sh')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_brand_surfaces_have_no_upstream_brand(self):
        for directory in ('branding', 'desktop', 'config'):
            for path in (ROOT / directory).rglob('*'):
                if path.is_file():
                    self.assertNotIn('omarchy', path.read_text().lower(), str(path))

    def test_import_register_is_explicit(self):
        data = json.loads((ROOT / 'provenance/imports.json').read_text())
        self.assertEqual(data['imports'], [])


if __name__ == '__main__':
    unittest.main()
