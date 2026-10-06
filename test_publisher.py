import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from publisher import make_draft


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "evidence.json").write_text(json.dumps({"measurements": {"tests": 4}}))
        self.spec = dict(project="Demo", version="0.1.0", summary_en="A local experiment.", summary_ar="تجربة محلية.",
            limitations_en="Small fixture set.", limitations_ar="بيانات تجريبية صغيرة.",
            repository_url="https://github.com/megern/demo", metrics=[
                {"label": "Tests", "source": "evidence.json", "field": "measurements.tests", "value": 4}])

    def tearDown(self):
        self.temp.cleanup()

    def test_uses_actual_value_and_keeps_audit_hash(self):
        text, audit = make_draft(self.spec, self.root)
        self.assertIn("Tests: 4", text)
        self.assertEqual(len(audit["verified_metrics"][0]["sha256"]), 64)
        self.assertTrue(audit["review_required"])

    def test_inflated_metric_rejected(self):
        self.spec["metrics"][0]["value"] = 99
        with self.assertRaises(ValueError):
            make_draft(self.spec, self.root)

    def test_display_preserves_parsed_numeric_values_without_six_digit_rounding(self):
        for value in [1234567, 0.123456789, 10 ** 400]:
            with self.subTest(value=value):
                (self.root / "evidence.json").write_text(json.dumps({"measurements": {"tests": value}}))
                self.spec["metrics"][0]["value"] = value
                text, audit = make_draft(self.spec, self.root)
                self.assertIn(f"Tests: {value}.", text)
                self.assertEqual(audit["verified_metrics"][0]["value"], value)

    def test_path_escape_and_nonfinite_rejected(self):
        self.spec["metrics"][0]["source"] = "../private.json"
        with self.assertRaises(ValueError):
            make_draft(self.spec, self.root)
        self.spec["metrics"][0]["source"] = "evidence.json"
        (self.root / "evidence.json").write_text('{"measurements":{"tests":NaN}}')
        with self.assertRaises(ValueError):
            make_draft(self.spec, self.root)

    def invoke_cli(self, output):
        spec_path = self.root / "release.json"
        spec_path.write_text(json.dumps(self.spec))
        return subprocess.run([
            sys.executable, str(Path(__file__).with_name("publisher.py")), str(spec_path),
            "--evidence-root", str(self.root), "--output", str(output),
        ], text=True, capture_output=True, check=False)

    def test_cli_direct_output_conflicts_preserve_spec_and_evidence(self):
        evidence = self.root / "evidence.json"
        original = evidence.read_bytes()
        for name in ("evidence.json", "release.json"):
            with self.subTest(output=name):
                command = self.invoke_cli(self.root / name)
                self.assertEqual(command.returncode, 2)
                self.assertEqual(evidence.read_bytes(), original)
                self.assertEqual(json.loads((self.root / "release.json").read_text()), self.spec)

    def test_cli_draft_symlink_cannot_overwrite_evidence(self):
        evidence = self.root / "evidence.json"
        original = evidence.read_bytes()
        output = self.root / "draft.md"
        output.symlink_to(evidence)
        command = self.invoke_cli(output)
        self.assertEqual(command.returncode, 2)
        self.assertEqual(evidence.read_bytes(), original)
        self.assertFalse((self.root / "draft.audit.json").exists())

    def test_cli_audit_symlink_conflict_is_detected_before_writing_draft(self):
        evidence = self.root / "evidence.json"
        original = evidence.read_bytes()
        output = self.root / "draft.md"
        output.with_suffix(".audit.json").symlink_to(evidence)
        command = self.invoke_cli(output)
        self.assertEqual(command.returncode, 2)
        self.assertEqual(evidence.read_bytes(), original)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
