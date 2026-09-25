# SPDX-License-Identifier: MIT
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(sys.platform.startswith('linux'), 'Theme helpers require GNU/Linux utilities')
class ThemeIntegrationTests(unittest.TestCase):
    def test_all_bundled_palettes_generate_resolved_app_configs(self):
        runtime=ROOT/'desktop/runtime'
        with tempfile.TemporaryDirectory() as t:
            env={**os.environ,'HOME':t,'XDG_RUNTIME_DIR':t,'STRATAGEM_DARK_PATH':str(runtime),'STRATAGEM_DARK_THEME_HEADLESS':'1','STRATAGEM_DARK_THEME_SKIP_BACKGROUND':'1','PATH':str(runtime/'bin')+':'+os.environ['PATH']}
            for theme in sorted((runtime/'themes').iterdir()):
                with self.subTest(theme=theme.name):
                    result=subprocess.run([str(runtime/'bin/stratagem-theme-set'),theme.name],env=env,capture_output=True,text=True,timeout=30)
                    self.assertEqual(result.returncode,0,result.stderr)
                    current=Path(t)/'.local/state/stratagem/current'
                    self.assertEqual((current/'theme.name').read_text().strip(),theme.name)
                    for name in ['colors.toml','shell.toml','foot.ini','hyprland.lua','hyprlock-colors.conf']:
                        content=(current/'theme'/name).read_text()
                        self.assertNotIn('{{',content,name)
                    tomllib.loads((current/'theme/shell.toml').read_text())
            # Session setup must not reseed Phosphor files over the selected palette.
            sys.path.insert(0,str(ROOT/'src'))
            from stratagem_dark.install import setup_user
            result=setup_user(runtime,Path(t),apply=False)
            self.assertFalse(any('/current/theme/' in p for p in result['would_create']))
