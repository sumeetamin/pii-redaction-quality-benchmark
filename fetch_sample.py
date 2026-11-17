"""Fetch ten evenly spaced 100-row windows from OpenPII validation."""
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


DATASET = "ai4privacy/pii-masking-openpii-1m"
ROWS_URL = "https://datasets-server.huggingface.co/rows"
SAMPLE_SIZE = 1000
PAGE_SIZE = 100
VALIDATION_ROWS = 284746


def main():
    records = []
    offsets = [
        round(index * (VALIDATION_ROWS - PAGE_SIZE) / (SAMPLE_SIZE // PAGE_SIZE - 1))
        for index in range(SAMPLE_SIZE // PAGE_SIZE)
    ]
    for offset in offsets:
        query = urlencode({
            "dataset": DATASET,
            "config": "default",
            "split": "validation",
            "offset": offset,
            "length": PAGE_SIZE,
        })
        request = Request(ROWS_URL + "?" + query, headers={"User-Agent": "pii-redaction-benchmark/1.0"})
        with urlopen(request, timeout=60) as response:
            payload = json.load(response)
        records.extend({
            "text": row["row"]["source_text"],
            "gold_spans_json": json.dumps([
                {"start": span["start"], "end": span["end"], "type": span["label"].lower()}
                for span in row["row"]["privacy_mask"]
            ], ensure_ascii=False),
            "language": row["row"].get("language", ""),
        } for row in payload["rows"])
        time.sleep(0.25)

    output = Path("data/openpii_validation_sample.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(output, index=False)
    print(f"Saved {len(records):,} synthetic labeled records to {output}")


if __name__ == "__main__":
    main()
