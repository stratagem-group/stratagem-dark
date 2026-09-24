# SPDX-License-Identifier: MIT
import hashlib
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
from stratagem_dark.install import safe_file, setup_user, verify_bundle
from stratagem_dark.core import ValidationError


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.runtime = self.root / 'runtime'
        self.home = self.root / 'home'
        self.home.mkdir()
        config = self.runtime / 'config/foot'
        config.mkdir(parents=True)
        (config / 'foot.ini').write_text('original default')

    def tearDown(self):
        self.temp.cleanup()

    def test_preview_never_writes(self):
        report = setup_user(self.runtime, self.home)
        self.assertEqual(len(report['would_create']), 1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_second_apply_is_idempotent(self):
        first = setup_user(self.runtime, self.home, True)
        second = setup_user(self.runtime, self.home, True)
        self.assertEqual(len(first['created']), 1)
        self.assertEqual(second['created'], [])
        self.assertEqual(second['preserved_existing'], [])

    def test_user_edits_preserved(self):
        setup_user(self.runtime, self.home, True)
        target = self.home / '.config/foot/foot.ini'
        target.write_text('user customization')
        result = setup_user(self.runtime, self.home, True)
        self.assertEqual(target.read_text(), 'user customization')
        self.assertEqual(result['preserved_existing'], [str(target)])

    def test_symlink_configuration_rejected(self):
        (self.home / '.config').symlink_to(self.root)
        with self.assertRaisesRegex(ValidationError, 'symlink'):
            setup_user(self.runtime, self.home, True)

    def test_root_setup_rejected(self):
        with patch('os.geteuid', return_value=0):
            with self.assertRaises(ValidationError):
                setup_user(self.runtime, self.home, True)

    def test_manifest_traversal_and_absolute_paths_rejected(self):
        for name in ('../outside', '/etc/passwd', 'repo/../../etc/passwd'):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                safe_file(self.root, name)

    def test_bundle_symlink_rejected(self):
        (self.root / 'link').symlink_to(ROOT / 'LICENSE')
        with self.assertRaisesRegex(ValidationError, 'symlink'):
            safe_file(self.root, 'link')


@unittest.skipUnless(shutil.which('gpg'), 'GnuPG signature checks run on Linux CI')
class SignatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name).resolve()
        cls.keyhome = cls.root / 'keys'
        cls.keyhome.mkdir(mode=0o700)
        cls.command = ['gpg', '--homedir', str(cls.keyhome), '--batch']
        subprocess.run(cls.command + ['--pinentry-mode', 'loopback', '--passphrase', '', '--quick-gen-key',
                       'STRATAGEM DARK unit fixture', 'ed25519', 'sign', '0'], check=True, capture_output=True)
        listing = subprocess.check_output(cls.command + ['--with-colons', '--list-keys'], text=True)
        cls.fingerprint = next(line.split(':')[9] for line in listing.splitlines() if line.startswith('fpr:'))
        cls.public = subprocess.check_output(cls.command + ['--armor', '--export', cls.fingerprint])

    @classmethod
    def tearDownClass(cls):
        subprocess.run(['gpgconf', '--homedir', str(cls.keyhome), '--kill', 'gpg-agent'], capture_output=True)
        cls.temp.cleanup()

    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(dir=self.root)
        self.bundle = Path(self.fixture.name)
        (self.bundle / 'repository').mkdir()
        (self.bundle / 'repository/example.pkg.tar.zst').write_bytes(b'unit-test package bytes')
        (self.bundle / 'repository/example.pkg.tar.zst.sig').write_bytes(b'signature-byte fixture')
        (self.bundle / 'release-key.asc').write_bytes(self.public)
        files = {p.relative_to(self.bundle).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.bundle.rglob('*') if p.is_file()}
        self.manifest = {'schema_version': 1, 'product': 'STRATAGEM DARK', 'architecture': 'x86_64',
                         'release_class': 'testing', 'files': files,
                         'packages': [{'name': 'example', 'file': 'repository/example.pkg.tar.zst',
                                       'signature': 'repository/example.pkg.tar.zst.sig',
                                       'sha256': files['repository/example.pkg.tar.zst']}]}
        self.sign()

    def tearDown(self):
        self.fixture.cleanup()

    def sign(self):
        path = self.bundle / 'manifest.json'
        path.write_text(json.dumps(self.manifest))
        subprocess.run(self.command + ['--yes', '--armor', '--detach-sign', str(path)], check=True, capture_output=True)

    def test_valid_signature_and_hashes(self):
        root, manifest = verify_bundle(self.bundle, self.fingerprint)
        self.assertEqual(root, self.bundle)
        self.assertEqual(manifest['product'], 'STRATAGEM DARK')

    def test_untrusted_fingerprint_rejected(self):
        with self.assertRaisesRegex(ValidationError, 'fingerprint mismatch'):
            verify_bundle(self.bundle, '0' * 40)

    def test_tampered_manifest_rejected(self):
        with (self.bundle / 'manifest.json').open('a') as stream:
            stream.write('tampered')
        with self.assertRaises(subprocess.CalledProcessError):
            verify_bundle(self.bundle, self.fingerprint)

    def test_tampered_archive_rejected(self):
        (self.bundle / 'repository/example.pkg.tar.zst').write_bytes(b'modified')
        with self.assertRaisesRegex(ValidationError, 'checksum mismatch'):
            verify_bundle(self.bundle, self.fingerprint)

    def test_signed_path_escape_rejected(self):
        self.manifest['files']['../escape'] = '0' * 64
        self.sign()
        with self.assertRaisesRegex(ValidationError, 'unsafe manifest'):
            verify_bundle(self.bundle, self.fingerprint)

    def test_missing_signature_coverage_rejected(self):
        del self.manifest['files']['repository/example.pkg.tar.zst.sig']
        self.sign()
        with self.assertRaisesRegex(ValidationError, 'unlocked'):
            verify_bundle(self.bundle, self.fingerprint)

    def test_missing_package_rejected(self):
        (self.bundle / 'repository/example.pkg.tar.zst').unlink()
        with self.assertRaisesRegex(ValidationError, 'missing bundle'):
            verify_bundle(self.bundle, self.fingerprint)
