import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from publisher import verified_requirements


class RequirementTests(unittest.TestCase):
    def test_incomplete_evidence_rejected_even_with_valid_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'run.json'
            source.write_text(json.dumps({'complete': False}))
            gate = {'source': 'run.json', 'field': 'complete', 'equals': True,
                    'expected_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(ValueError, 'not satisfied'):
                verified_requirements({'evidence_requirements': [gate]}, root)
            gate['equals'] = False
            self.assertEqual(verified_requirements({'evidence_requirements': [gate]}, root)[0]['equals'], False)

    def test_bool_is_not_integer_and_changed_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'run.json'
            source.write_text('{"count":1}')
            gate = {'source': 'run.json', 'field': 'count', 'equals': True,
                    'expected_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(ValueError, 'not satisfied'):
                verified_requirements({'evidence_requirements': [gate]}, root)
            gate['equals'] = 1
            self.assertEqual(len(verified_requirements({'evidence_requirements': [gate]}, root)), 1)
            source.write_text('{"count":2}')
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                verified_requirements({'evidence_requirements': [gate]}, root)

    def test_outside_root_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gate = {'source': '../outside.json', 'field': 'complete', 'equals': True, 'expected_sha256': 'a' * 64}
            with self.assertRaisesRegex(ValueError, 'inside'):
                verified_requirements({'evidence_requirements': [gate]}, root)
