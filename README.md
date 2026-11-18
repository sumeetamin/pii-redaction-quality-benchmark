# PII Redaction Quality Benchmark

A small exact-span evaluation of a deliberately limited regex redaction baseline. The benchmark keeps all text and redacted rows local and publishes aggregate metrics only.

## Data

Uses the [Ai4Privacy OpenPII 1M dataset](https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m), licensed CC BY 4.0. The dataset card describes the records as synthetic PII and lists research/commercial reuse with attribution. This run used 1,000 rows from ten evenly spaced 100-row windows in the official validation split, spanning nine observed language codes. The local sample CSV fingerprint is `622f56149879d6f0eaf2cbf76e2eaf89e7f8dbbc3888df2549561d69a0c58c3d`.

## Results

| Measure | Result |
|---|---:|
| Labeled spans | 7,622 |
| Exact-span precision | 87.8% |
| Exact-span recall | 8.9% |
| Exact-span F1 | 16.2% |
| Email precision / recall | 98.7% / 96.8% |
| Phone precision / recall | 55.3% / 21.2% |
| Luhn-valid credit-card precision / recall | 66.7% / 13.9% |
| SSN-format precision / recall | 100% / 6.1% |

Email and US-formatted SSNs use regexes; phone detection uses libphonenumber with language-derived default regions; credit-card candidates must pass Luhn validation. The run found 681 exact-span matches, 95 false positives and 6,941 misses. Fifteen other labeled entity types (including names, addresses, dates and government IDs) remain unsupported, so overall recall is still only 8.9%. Phone detection still misses most labeled phones. This synthetic multilingual benchmark is not assurance for real personal data or a production privacy filter.

## Reproduce

```bash
python -m pip install -r requirements.txt
python fetch_sample.py
python main.py --input data/openpii_validation_sample.csv \\
  --dataset "Ai4Privacy OpenPII 1M" \\
  --source-url https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m \\
  --split-description "1,000 rows from ten evenly spaced windows in official validation"
```

The fetcher writes PII-like text locally under `data/`; the runner writes redacted text locally under `outputs/`. Both folders are ignored. No row-level text or redactions are published. Attribute the dataset to Ai4Privacy / Ai Suisse SA under CC BY 4.0. See the [aggregate report](reports/benchmark.json).
