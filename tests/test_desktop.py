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
            policy=json.loads((p/'opencode.json').read_text())['permission']
            self.assertEqual(policy['bash'],'ask')
            self.assertEqual(policy['edit'],'ask')
            self.assertEqual(policy['read']['*.env'],'deny')
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
            (root/'catalog/optional-tools.json').write_text(json.dumps({'socat':{'package':'socat','repository':'arch'},'bad':{'package':'--config=/tmp/evil','repository':'arch'}}))
            with patch.object(optional_tools,'ROOT',root),patch('os.geteuid',return_value=0),patch('subprocess.call',return_value=0) as call, patch('subprocess.run'):
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

class ModelSelectionTests(unittest.TestCase):
    def test_model_is_an_argument_not_a_shell_command(self):
        from stratagem_dark.desktop import launch_agent
        with tempfile.TemporaryDirectory() as t,patch('os.geteuid',return_value=1000),patch('shutil.which',return_value='/bin/opencode'),patch('subprocess.call',return_value=0) as call:
            launch_agent('opencode',t,model='provider/model-v1')
            self.assertEqual(call.call_args.args[0],['opencode','--model','provider/model-v1'])
            with self.assertRaises(ValueError):launch_agent('opencode',t,model='provider/model;sh')
    def test_model_catalog_ignores_logs_and_unknown_selection(self):
        from stratagem_dark.desktop import select_model
        from subprocess import CompletedProcess
        with patch('subprocess.run',side_effect=[CompletedProcess([],0,'INFO loading\nprovider/model-one\nother/model-two\n'),CompletedProcess([],0,'provider/model-one\n')]),patch('stratagem_dark.desktop.choose',return_value='provider'):
            self.assertEqual(select_model(),'provider/model-one')

class AgentOnboardingTests(unittest.TestCase):
    def test_saved_agent_launch_has_no_setup_prompts(self):
        from stratagem_dark.desktop import agents
        with tempfile.TemporaryDirectory() as t, patch('pathlib.Path.home',return_value=Path(t)), patch('shutil.which',return_value='/usr/bin/opencode'), patch('stratagem_dark.desktop.choose') as choose, patch('stratagem_dark.desktop.launch_agent',return_value=0) as launch:
            config=Path(t)/'.config/stratagem/agent.json';config.parent.mkdir(parents=True)
            config.write_text(json.dumps({'agent':'opencode','workspace':t,'models':{'opencode':'provider/model'}}))
            self.assertEqual(agents(),0)
            choose.assert_not_called()
            launch.assert_called_once_with('opencode',Path(t),model='provider/model')
    def test_first_signin_native_and_only_success_saves_default(self):
        from stratagem_dark.desktop import agents
        for status in (0,1):
            with tempfile.TemporaryDirectory() as t, patch('pathlib.Path.home',return_value=Path(t)), patch('shutil.which',side_effect=lambda x:'/bin/opencode' if x=='opencode' else None), patch('stratagem_dark.desktop.choose',side_effect=['opencode','Sign in and start']), patch('subprocess.call',return_value=status) as call, patch('stratagem_dark.desktop.launch_agent',return_value=0) as launch:
                self.assertEqual(agents(),status)
                call.assert_called_once_with(['opencode','auth','login'])
                self.assertEqual((Path(t)/'.config/stratagem/agent.json').exists(),status==0)
                self.assertEqual(launch.called,status==0)
    def test_cancel_does_not_select_or_launch_agent(self):
        from stratagem_dark.desktop import agents
        with tempfile.TemporaryDirectory() as t, patch('pathlib.Path.home',return_value=Path(t)), patch('shutil.which',return_value='/bin/opencode'), patch('stratagem_dark.desktop.choose',side_effect=['opencode','Cancel']), patch('stratagem_dark.desktop.launch_agent') as launch:
            self.assertEqual(agents(),0)
            launch.assert_not_called()
            self.assertFalse((Path(t)/'.config/stratagem/agent.json').exists())

class DefaultAgentPolicyTests(unittest.TestCase):
    def test_plain_workspace_has_approval_and_secret_file_defaults(self):
        policy=json.loads((ROOT/'desktop/runtime/config/opencode/opencode.json').read_text())['permission']
        self.assertEqual(policy['bash'],'ask')
        self.assertEqual(policy['edit'],'ask')
        self.assertEqual(policy['external_directory'],'ask')
        self.assertEqual(policy['read']['*.env'],'deny')
        self.assertEqual(policy['read']['*.env.*'],'deny')
        self.assertEqual(policy['read']['*.env.example'],'allow')
