"""Build a local project review from pinned evidence specifications; never post."""
import hashlib
import argparse
import json
from pathlib import Path
from publisher import make_draft
from portfolio_report_bundle import write_bundle, digest

def build_portfolio(spec_paths, evidence_root):
    if not 1 <= len(spec_paths) <= 32:
        raise ValueError('Supply 1..32 project evidence specifications')
    projects = []
    for path in spec_paths:
        raw = Path(path).read_bytes()
        spec = json.loads(raw)
        if not isinstance(spec, dict) or not spec.get('metrics') or any(('expected_sha256' not in metric for metric in spec['metrics'])):
            raise ValueError('Portfolio projects require nonempty hash-pinned metrics')
        if any(('expected_sha256' not in gate for gate in spec.get('evidence_requirements', []))):
            raise ValueError('All evidence requirements must be pinned')
        draft, audit = make_draft(spec, evidence_root)
        projects.append({'specification': Path(path).name, 'specification_sha256': hashlib.sha256(raw).hexdigest(), 'review_draft': draft, 'audit': audit})
    return {'tool': 'portfolio-review', 'projects': projects, 'publication_state': 'local_draft_for_human_review', 'scope': 'Evidence consistency checks, not novelty, adoption, or hiring guarantees. No social-network client, publishing operation or fabricated history.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('specs', nargs='+', type=Path)
    p.add_argument('--evidence-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        report = build_portfolio(a.specs, a.evidence_root)
        write_bundle(a.output, report, 'Project evidence portfolio review')
        print(json.dumps({'projects': len(report['projects']), 'published': False}))
    except (ValueError, OSError, KeyError, TypeError) as e:
        p.exit(2, str(e) + '\n')
if __name__ == '__main__':
    main()
