#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""CI's independent JSON Schema validation; runtime uses no third-party packages."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(__file__).resolve().parents[1]
for kind, paths in [('catalog', [root / 'catalog/tools.json']),
                    ('profile', sorted((root / 'profiles').glob('*.json')))]:
    schema = json.loads((root / f'schemas/{kind}.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for path in paths:
        validator.validate(json.loads(path.read_text()))
print('Catalog and profile JSON Schema checks passed.')
