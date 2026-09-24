# SPDX-License-Identifier: MIT
"""Exercise profile composition with dangling live-root links, without root."""
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class IsoCompositionTests(unittest.TestCase):
    def test_live_links_are_preserved_and_identity_does_not_follow_host_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / 'releng'
            etc = template / 'airootfs/etc'
            units = etc / 'systemd/system/multi-user.target.wants'
            units.mkdir(parents=True)
            (units / 'missing.service').symlink_to('/usr/lib/systemd/system/missing.service')
            (units / 'sshd.service').symlink_to('/usr/lib/systemd/system/sshd.service')
            host_identity = root / 'host-os-release'
            host_identity.write_text('ID=host\n')
            (etc / 'os-release').symlink_to(host_identity)
            bundle = root / 'bundle'
            bundle.mkdir()
            (bundle / 'manifest.json').write_text(json.dumps({'packages': [{'name': 'base'}]}))
            profile = root / 'profile'
            original_copy = shutil.copytree

            def copy_template(source, destination, **kwargs):
                self.assertEqual(source, '/usr/share/archiso/configs/releng')
                return original_copy(template, destination, **kwargs)

            def recursive_copy(source, destination, **kwargs):
                with patch('shutil.copytree', original_copy):
                    return copy_template(source, destination, **kwargs)

            with patch('sys.argv', ['assemble-iso.py', str(bundle), str(profile), 'A' * 40]), \
                 patch('shutil.copytree', side_effect=recursive_copy), \
                 patch('subprocess.check_output', return_value='$6$testhash\n'):
                runpy.run_path(str(ROOT / 'scripts/assemble-iso.py'), run_name='__main__')
            live = profile / 'airootfs'
            self.assertEqual(host_identity.read_text(), 'ID=host\n')
            self.assertFalse((live / 'etc/os-release').is_symlink())
            self.assertIn('ID=stratagem-dark', (live / 'etc/os-release').read_text())
            self.assertTrue((live / 'etc/systemd/system/multi-user.target.wants/missing.service').is_symlink())
            self.assertFalse((live / 'etc/systemd/system/multi-user.target.wants/sshd.service').is_symlink())
            self.assertIn('root:!*:', (live / 'etc/shadow').read_text())
            self.assertTrue((live / 'home/stratagem').is_dir())
            self.assertIn('["/home/stratagem"]="1000:1000:750"', (profile / 'profiledef.sh').read_text())
