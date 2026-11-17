# PII Redaction Quality Benchmark

A small exact-span evaluation of a deliberately limited regex redaction baseline. The benchmark keeps all text and redacted rows local and publishes aggregate metrics only.

## Data

Uses the [Ai4Privacy OpenPII 1M dataset](https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m), licensed CC BY 4.0. The dataset card describes the records as synthetic PII and lists research/commercial reuse with attribution. This run used 1,000 rows from ten evenly spaced 100-row windows in the official validation split, spanning nine observed language codes. The local sample CSV fingerprint is \`622f56149879d6f0eaf2cbf76e2eaf89e7f8dbbc3888df2549561d69a0c58c3d\`.

## Results

| Measure | Result |
|---|---:|
| Labeled spans | 7,622 |
| Exact-span precision | 69.5% |
| Exact-span recall | 7.8% |
| Exact-span F1 | 14.1% |
| Email precision / recall | 98.7% / 96.8% |
| Phone precision / recall | 13.3% / 9.4% |
| SSN-format precision / recall | 100% / 6.1% |

The regexes cover only email, US-formatted phone, and SSN patterns. Other labeled classes (names, addresses, dates, government IDs, and more) are intentionally unsupported, which drives overall recall down. Phone patterns also produce substantial false positives. These figures are a synthetic-data baseline, not assurance for real personal data or a production privacy filter.

## Reproduce

\`\`\`bash
python -m pip install -r requirements.txt
python fetch_sample.py
python main.py --input data/openpii_validation_sample.csv \\
  --dataset "Ai4Privacy OpenPII 1M" \\
  --source-url https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m \\
  --split-description "1,000 rows from ten evenly spaced windows in official validation"
\`\`\`

The fetcher writes PII-like text locally under \`data/\`; the runner writes redacted text locally under \`outputs/\`. Both folders are ignored. No row-level text or redactions are published. Attribute the dataset to Ai4Privacy / Ai Suisse SA under CC BY 4.0. See the [aggregate report](reports/benchmark.json).
