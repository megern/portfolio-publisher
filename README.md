# Portfolio Publisher

## Refusing drafts from incomplete evidence (local development)

Specifications may include `evidence_requirements`, each with `source`, `field`,
`equals`, and `expected_sha256`. For example, gate a draft on a hash-pinned
report's `complete` field being `true`. Every gate must pass before generating
or verifying a draft; an accurate numeric value from an incomplete experiment
is insufficient. Scalar types must match exactly, so integer `1` does not pass
a boolean `true` gate. Gate sources are protected from output overwrites.

These checks verify supplied local evidence fields. They do not establish the
truth of a narrative, scientific novelty, or authenticity of the evidence.

## Public preview v0.2.0

Python 3.11+; commands below use a local Mac/Linux shell. Source and reports are public; this is a research/development preview, not a production-security certification.

```sh
git clone --branch v0.2.0 https://github.com/megern/portfolio-publisher.git
cd portfolio-publisher
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
portfolio-publisher --help
```

The installed entry point was exercised outside the checkout in a separate local environment. This revision has 12 passing local tests. No hosted CI or cloud compute is used. Report an issue with the command, Python/OS versions, sanitized input and expected/actual behavior; remove credentials and private records first. Benchmarks describe the supplied fixtures and hardware.

Produce bilingual post drafts from local experiment reports. Numeric measurements are read from their source JSON files; supplied values that disagree with that evidence are rejected. Each draft has an audit file containing the source hash and JSON field.

```sh
python3 publisher.py examples/release.json --evidence-root examples --output examples/draft.md
python3 -m unittest -v
```

## Evidence before wording

A release specification contains a project, version, English/Arabic summaries and limitations, a canonical GitHub repository URL, and a list of metrics. Each metric names a source inside `evidence-root` and a dotted JSON field. List indices are supported. Values must be finite numbers, and sources cannot escape the evidence directory. Drafts preserve the parsed numeric value instead of rounding it to six significant digits; the same value is retained in the audit file.

Before writing either output, the CLI checks resolved draft and audit paths
against the release specification and every verified evidence source. Conflicts,
including symlinks, are rejected so a draft cannot replace its own evidence.

This tool verifies numeric entries in the metrics list. It **does not fact-check narrative text**, confirm links exist, or establish that the underlying experiment was well designed. The original example uses clearly labeled synthetic measurements. No account credentials, network client, social posting, or fabricated work history are part of the tool. Review the generated text before publishing it.

## Measured training example

[Draft](examples/measured-training/draft.md) · [Audit](examples/measured-training/draft.audit.json) · [Evidence](examples/measured-training/benchmark.json) · [Release specification](examples/measured-training/release.json)

This example uses a byte-for-byte copy of the measured `mac-local-training`
benchmark summary. The run is real; the model is tiny, randomly initialized, and
trained on synthetic data with one seed per strategy. The draft includes the
tradeoff: optimizer state decreased while total process RSS increased, and
rotating gave each layer fewer updates. It makes no cybersecurity-quality or
training-method novelty claim.

```sh
python3 publisher.py examples/measured-training/release.json --evidence-root examples/measured-training --output examples/measured-training/draft.md
```

Tests reject inflated numbers, path escapes, and non-finite values, check evidence hashes, and preserve large integers and decimal measurements in the draft. This is a template-based first version, not an LLM writer.

## العربية

يجهّز مسودة بالعربية والإنجليزية من نتائج محفوظة محليًا. يراجع الأرقام مقابل ملفاتها الأصلية ويحتفظ ببصماتها. النشر والمراجعة مسؤولية صاحب المحتوى؛ لا ينشر تلقائيًا ولا يختلق أرقامًا أو تاريخ عمل.

## Pinning metric evidence

Each metric may include `expected_sha256` with the digest of its entire source file. The publisher rejects a changed source even if the selected numeric value is unchanged. `examples/release.json` demonstrates pinned synthetic evidence. Omitting the pin preserves compatibility with earlier specs. Metric declarations require finite numbers; booleans and negative list indices are rejected.

```sh
python3 -m unittest discover -s .
```

Pins and the generated audit establish file consistency, not the truth of the narrative. Drafts still require human review. This tool does not post to LinkedIn or any other platform.


### Verify without creating content

```sh
portfolio-publisher examples/release.json --evidence-root examples --verify-only --require-pins
```

`--verify-only` prints the audit without writing any files. `--require-pins` rejects any metric without an expected source digest. Publishing remains a separate human action. The release catalog under `examples/public-preview/` links all nine projects and states their public-preview scope; it does not assert popularity, adoption or guaranteed hiring outcomes.

Browse [the nine-project release catalog](examples/public-preview/release-catalog.json) for links, versions and local test counts. Content drafts remain local for review; this repository contains the catalog and verified numeric evidence only.
