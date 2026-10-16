# PII Redaction Quality Benchmark

Redact emails, phone numbers, and SSNs and score exact-span precision/recall on a locally held labeled corpus.

> **Portfolio prototype.** Source code is provided; no benchmark results are claimed until you run it on the cited data and record the output.

## Use case

Redact emails, phone numbers, and SSNs and score exact-span precision/recall on a locally held labeled corpus. The CLI consumes local files, emits reproducible reports, and keeps data out of the repository.

## Data and provenance

Use only an authorized, de-identified corpus or a controlled local benchmark.. CSV columns `text` and optional `gold_spans_json`, a JSON list of {start,end,type} spans. Keep sensitive source data local and never commit it. Source files are not bundled. Respect source terms and cite the dataset when publishing results.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Download/prepare the source data locally, then run:
python main.py --input data/labeled_text.csv --text text --gold-spans gold_spans_json --out outputs
```

## Outputs

Generated results are saved under `outputs/`; file names and metrics are printed or documented by the CLI. The repository excludes downloaded data and artifacts.

## Evaluation and operating notes

Regex is a deliberately simple baseline and can miss names, addresses, international identifiers, and obfuscated PII. Do not upload raw or labeled personal text to this repository.

For production use, add a frozen reference period, out-of-time evaluation, monitoring ownership, and a documented rollback or escalation path. This project is a local baseline, not a deployed service.

## License

No code license file is included yet. Third-party data remains subject to its source terms.
