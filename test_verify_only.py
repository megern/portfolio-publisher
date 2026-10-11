import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class VerifyOnlyTests(unittest.TestCase):
    def test_verification_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'unused.md'
            result=subprocess.run([sys.executable,str(ROOT/'publisher.py'),str(ROOT/'examples/release.json'),'--evidence-root',str(ROOT/'examples'),'--verify-only','--require-pins','--output',str(output)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(json.loads(result.stdout)['review_required'])
            self.assertEqual(list(Path(folder).iterdir()),[])
    def test_missing_pin_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'spec.json';spec=json.loads((ROOT/'examples/release.json').read_text())
            del spec['metrics'][0]['expected_sha256'];path.write_text(json.dumps(spec))
            result=subprocess.run([sys.executable,str(ROOT/'publisher.py'),str(path),'--require-pins','--verify-only'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
