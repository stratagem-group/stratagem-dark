# SPDX-License-Identifier: MIT
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from stratagem_dark import network

class NetworkTests(unittest.TestCase):
    def test_private_profile_and_secret_never_spawn_process(self):
        dbus=MagicMock()
        dbus.Dictionary.side_effect=lambda data,**kw:data
        dbus.Array.side_effect=lambda data,**kw:data
        dbus.String.side_effect=lambda data:data
        manager,device,wireless,ap,settings,connection,state=[MagicMock() for _ in range(7)]
        manager.GetDevices.return_value=['/device']
        device.Get.return_value=2
        wireless.GetAllAccessPoints.return_value=['/ap']
        ap.GetAll.return_value={'Ssid':b'Lab','Strength':80}
        settings.ListConnections.return_value=[]
        manager.AddAndActivateConnection.return_value=('/settings','/active')
        state.Get.return_value=2
        connection.GetSettings.return_value={'connection':{}}
        dbus.Interface.side_effect=[manager,device,wireless,ap,settings,connection,state]
        with patch.dict(sys.modules,{'dbus':dbus}),patch('os.geteuid',return_value=1000),patch('pwd.getpwuid') as user,patch('subprocess.run') as run:
            user.return_value.pw_name='stratagem'
            self.assertEqual(network.connect({'ssid':'Lab','password':'secret-password'}),0)
            run.assert_not_called()
        call=manager.AddAndActivateConnection.call_args.args
        self.assertEqual(call[0]['connection']['permissions'],['user:stratagem:'])
        self.assertEqual(call[1:],('/device','/ap'))
    def test_error_does_not_expose_secret(self):
        with patch('sys.stdin',io.StringIO('{"ssid":"Lab","password":"secret"}\n')),patch('sys.stdout',new_callable=io.StringIO) as output,patch.object(network,'connect',side_effect=RuntimeError('secret')):
            self.assertEqual(network.main(),1)
            self.assertNotIn('secret',output.getvalue())
    def test_reject_root(self):
        with patch('os.geteuid',return_value=0):
            with self.assertRaises(ValueError):network.connect({'ssid':'Lab'})
    def test_missing_saved_secret_requests_inline_password(self):
        with patch('sys.stdin',io.StringIO('{"ssid":"Lab"}\n')),patch('sys.stdout',new_callable=io.StringIO),patch.object(network,'connect',side_effect=network.PasswordRequired()):
            self.assertEqual(network.main(),2)
