import json
from pathlib import Path
import tempfile
import unittest
from portfolio import build_portfolio
class PortfolioTests(unittest.TestCase):
    def test_missing_pin_stops_whole_portfolio(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'spec.json';p.write_text(json.dumps({'metrics':[{'source':'x','field':'x','label':'x'}]}))
            with self.assertRaises(ValueError):build_portfolio([p],root)
    def test_actual_pinned_example_generates_local_review_only(self):
        root=Path(__file__).parent/'examples'
        result=build_portfolio([root/'release.json'],root)
        self.assertEqual(result['publication_state'],'local_draft_for_human_review');self.assertEqual(len(result['projects']),1)
