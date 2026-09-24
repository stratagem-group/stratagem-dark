# SPDX-License-Identifier: MIT
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stratagem_dark.desktop import create_engagement, launch_agent

class DesktopTests(unittest.TestCase):
    def test_engagement_preserves_existing_directory(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError): create_engagement(t,'Own lab',{})
            self.assertEqual(list(Path(t).iterdir()),[])
    def test_engagement_requires_scope(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError): create_engagement(Path(t)/'empty',' ',{})
            self.assertFalse((Path(t)/'empty').exists())
    def test_engagement_inventory_and_permissions(self):
        with tempfile.TemporaryDirectory() as t, patch('shutil.which',side_effect=lambda x:'/bin/'+x if x=='nmap' else None):
            p=create_engagement(Path(t)/'review','My isolated lab only',{'nmap':['nmap','--help'],'missing':['missing']})
            self.assertEqual(json.loads((p/'TOOLS.json').read_text()),{'nmap':'nmap'})
            self.assertIn('My isolated lab only',(p/'SCOPE.md').read_text())
            self.assertEqual(p.stat().st_mode & 0o777,0o700)
            self.assertEqual(json.loads((p/'opencode.json').read_text())['permission']['bash'],'ask')
    def test_agent_launch_uses_argv_and_retains_permission_prompts(self):
        with tempfile.TemporaryDirectory(prefix='work space ') as t, patch('os.geteuid',return_value=1000), patch('shutil.which',return_value='/bin/opencode'), patch('subprocess.call',return_value=0) as call:
            launch_agent('opencode',t)
            call.assert_called_once_with(['opencode'],cwd=Path(t).resolve())
    def test_agent_rejects_root_and_unknown_commands(self):
        with patch('os.geteuid',return_value=0),patch('shutil.which',return_value='/bin/opencode'):
            with self.assertRaises(ValueError):launch_agent('opencode','/tmp')
            with self.assertRaises(ValueError):launch_agent('sh','/tmp')

class OptionalInstallerTests(unittest.TestCase):
    def test_only_catalog_packages_reach_package_manager(self):
        from stratagem_dark import optional_tools
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'catalog').mkdir()
            (root/'catalog/optional-tools.json').write_text(json.dumps({'socat':{'package':'socat'},'bad':{'package':'--config=/tmp/evil'}}))
            with patch.object(optional_tools,'ROOT',root),patch('os.geteuid',return_value=0),patch('subprocess.call',return_value=0) as call:
                for name in ['../../bin/sh','--noconfirm','bad']:
                    with self.assertRaises(ValueError):optional_tools.install(name)
                call.assert_not_called()
                optional_tools.install('socat')
                argv=call.call_args.args[0]
                self.assertEqual(argv[-1],'extra/socat')
                self.assertIn('-Syu',argv)
                self.assertEqual(call.call_args.kwargs['cwd'],'/')
    def test_nonroot_install_rejected(self):
        from stratagem_dark import optional_tools
        with patch('os.geteuid',return_value=1000),patch('subprocess.call') as call:
            with self.assertRaises(ValueError):optional_tools.install('socat')
            call.assert_not_called()
