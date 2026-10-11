import hashlib,json,tempfile,unittest
from pathlib import Path
from publisher import verified_metrics
class PinnedEvidenceTests(unittest.TestCase):
 def test_source_drift_detected_even_if_selected_number_unchanged(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);file=root/'data.json';file.write_text('{"value":1,"context":"first"}')
   pin=hashlib.sha256(file.read_bytes()).hexdigest();metric={'source':'data.json','field':'value','label':'v','expected_sha256':pin}
   self.assertEqual(verified_metrics({'metrics':[metric]},root)[0]['value'],1)
   file.write_text('{"value":1,"context":"different"}')
   with self.assertRaises(ValueError):verified_metrics({'metrics':[metric]},root)
 def test_boolean_declared_as_one_and_negative_index_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'data.json').write_text('{"values":[1]}')
   metric={'source':'data.json','field':'values.0','label':'v','value':True}
   with self.assertRaises(ValueError):verified_metrics({'metrics':[metric]},root)
   metric.pop('value');metric['field']='values.-1'
   with self.assertRaises(ValueError):verified_metrics({'metrics':[metric]},root)
 def test_malformed_metric_collection(self):
  with self.assertRaises(ValueError):verified_metrics({'metrics':42},Path('.'))
