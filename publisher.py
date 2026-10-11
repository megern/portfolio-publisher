"""Build professional post drafts from local, verifiable experiment evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse


def verified_metrics(spec: dict, evidence_root: Path) -> list[dict]:
    result = []
    if not isinstance(spec.get('metrics', []), list):
        raise ValueError("metrics must be an array")
    root = evidence_root.resolve()
    for metric in spec.get("metrics", []):
        if not isinstance(metric, dict):
            raise ValueError("each metric must be an object")
        for key in ('source', 'field', 'label'):
            if not isinstance(metric.get(key), str) or not metric[key].strip():
                raise ValueError("metric requires nonempty " + key)
        if not isinstance(metric.get('unit', ''), str):
            raise ValueError("metric unit must be a string")
        source = (root / metric["source"]).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError("metric source must be a file inside evidence-root")
        raw = source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if 'expected_sha256' in metric and metric['expected_sha256'] != digest:
            raise ValueError("evidence source changed from the expected SHA-256")
        value = json.loads(raw)
        for key in metric["field"].split("."):
            if isinstance(value, list):
                if not key.isdecimal():
                    raise ValueError("list indices must be nonnegative decimal integers")
                value = value[int(key)]
            elif isinstance(value, dict):
                value = value[key]
            else:
                raise ValueError("metric field traverses a scalar")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)):
            raise ValueError("metric must resolve to a finite numeric measurement")
        if 'value' in metric and (isinstance(metric['value'], bool) or not isinstance(metric['value'], (int, float)) or (isinstance(metric['value'], float) and not math.isfinite(metric['value']))):
            raise ValueError("declared metric must be a finite number")
        if "value" in metric and metric["value"] != value:
            raise ValueError("declared metric does not match evidence")
        result.append({"label": metric["label"], "value": value, "unit": metric.get("unit", ""),
            "source": str(source.relative_to(root)), "field": metric["field"],
            "sha256": digest})
    return result


def make_draft(spec: dict, evidence_root: Path) -> tuple[str, dict]:
    for field in ("project", "version", "summary_en", "summary_ar", "limitations_en", "limitations_ar", "repository_url"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise ValueError(f"missing nonempty {field}")
    url = urlparse(spec["repository_url"])
    if url.scheme != "https" or url.netloc != "github.com" or len(url.path.strip("/").split("/")) != 2 or url.username or url.query or url.fragment:
        raise ValueError("repository_url must be a canonical HTTPS GitHub repository link")
    metrics = verified_metrics(spec, evidence_root)
    requirements = verified_requirements(spec, evidence_root)
    values = "\n".join(f"- {m['label']}: {m['value']}{(' ' + str(m['unit'])) if m['unit'] else ''}." for m in metrics)
    text = f"# {spec['project']} {spec['version']} — draft\n\n## English\n\n{spec['summary_en']}\n\n{values}\n\nLimits: {spec['limitations_en']}\n\nCode: {spec['repository_url']}\n\n## العربية\n\n{spec['summary_ar']}\n\n{values}\n\nحدود التجربة: {spec['limitations_ar']}\n\nالكود: {spec['repository_url']}\n\n---\nDraft for human review. No post has been published.\n"
    return text, {"schema_version": 1, "project": spec["project"], "version": spec["version"], "verified_metrics": metrics,
        "verified_requirements": requirements,
        "review_required": True, "limitations": ["Narrative is supplied by the author and is not fact-checked.",
            "Only numeric claims in the metrics list are checked against local evidence."]}


def verified_requirements(spec: dict, evidence_root: Path) -> list[dict]:
    """Optional pinned gates, e.g. refusing a draft from an incomplete run."""
    requirements = spec.get('evidence_requirements', [])
    if not isinstance(requirements, list):
        raise ValueError('evidence_requirements must be an array')
    root = evidence_root.resolve()
    result = []
    for requirement in requirements:
        if not isinstance(requirement, dict) or any(not isinstance(requirement.get(key), str)
                or not requirement[key].strip() for key in ('source', 'field', 'expected_sha256')):
            raise ValueError('Each evidence requirement needs source, field and expected_sha256')
        expected = requirement.get('equals')
        if type(expected) not in (str, bool, int, float) or isinstance(expected, float) and not math.isfinite(expected):
            raise ValueError('Requirement equals must be a finite scalar')
        source = (root / requirement['source']).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError('Requirement source must be inside evidence-root')
        raw = source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != requirement['expected_sha256']:
            raise ValueError('Requirement evidence hash changed')
        value = json.loads(raw)
        for field in requirement['field'].split('.'):
            if isinstance(value, dict):
                value = value[field]
            elif isinstance(value, list) and field.isdecimal():
                value = value[int(field)]
            else:
                raise ValueError('Invalid evidence requirement field')
        if type(value) is not type(expected) or value != expected:
            raise ValueError('Evidence requirement not satisfied: ' + requirement['field'])
        result.append({'source': str(source.relative_to(root)), 'field': requirement['field'],
                       'equals': expected, 'sha256': digest})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--evidence-root", type=Path, default=Path("."))
    parser.add_argument("--verify-only", action="store_true", help="Print evidence audit without writing a draft")
    parser.add_argument("--require-pins", action="store_true", help="Require expected_sha256 on every metric")
    parser.add_argument("--output", type=Path, default=Path("draft.md"))
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text())
        if not isinstance(spec, dict) or not isinstance(spec.get("metrics", []), list):
            raise ValueError("Specification must be an object with a metrics array")
        if args.require_pins and any(not isinstance(metric, dict) or 'expected_sha256' not in metric for metric in spec.get('metrics', [])):
            raise ValueError("All metrics need expected_sha256 in pinned mode")
        draft, audit = make_draft(spec, args.evidence_root)
        if args.verify_only:
            print(json.dumps(audit, ensure_ascii=False, indent=2))
            return
        audit_output = args.output.with_suffix(".audit.json")
        protected = {args.spec.resolve()}
        protected.update((args.evidence_root.resolve() / metric["source"]).resolve()
                         for metric in audit["verified_metrics"])
        protected.update((args.evidence_root.resolve() / gate['source']).resolve()
                         for gate in audit['verified_requirements'])
        outputs = {args.output.resolve(), audit_output.resolve()}
        if outputs & protected:
            raise ValueError("draft and audit outputs must not replace the specification or verified evidence")
        if len(outputs) != 2:
            raise ValueError("draft and audit outputs must be different files")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        parser.exit(2, f"Evidence error: {exc}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(draft)
    audit_output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print(f"Draft saved to {args.output}; nothing was posted.")


if __name__ == "__main__":
    main()
