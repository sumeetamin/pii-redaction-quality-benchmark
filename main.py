"""Score a local exact-span PII baseline on labeled text."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import phonenumbers


PATTERNS = {
    "email": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
TYPE_ALIASES = {"telephonenum": "phone", "socialnum": "ssn"}
PHONE_REGIONS_BY_LANGUAGE = {
    "bg": ["BG"], "de": ["DE"], "en": ["US", "GB", "CA", "AU"],
    "fi": ["FI"], "fr": ["FR"], "it": ["IT"], "nl": ["NL"],
    "sk": ["SK"], "sv": ["SE"],
}


def canonical_type(label):
    value = str(label).lower()
    return TYPE_ALIASES.get(value, value)


def luhn_valid(value):
    digits = [int(char) for char in value if char.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    reversed_digits = digits[::-1]
    checksum = sum(
        digit if index % 2 == 0 else (digit * 2 - 9 if digit * 2 > 9 else digit * 2)
        for index, digit in enumerate(reversed_digits)
    )
    return checksum % 10 == 0


def detect(text, language=None):
    """Return exact spans for supported PII types; phone parsing uses language regions."""
    value = str(text)
    spans = {
        (match.start(), match.end(), entity_type)
        for entity_type, pattern in PATTERNS.items()
        for match in pattern.finditer(value)
    }
    for match in CARD_PATTERN.finditer(value):
        if luhn_valid(match.group()):
            spans.add((match.start(), match.end(), "creditcardnumber"))
    language_code = "" if language is None or pd.isna(language) else str(language).lower()
    regions = PHONE_REGIONS_BY_LANGUAGE.get(language_code, [None])
    for region in regions:
        for match in phonenumbers.PhoneNumberMatcher(value, region):
            spans.add((match.start, match.end, "phone"))
    return sorted(spans)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--text", default="text")
    parser.add_argument("--gold-spans", default="gold_spans_json")
    parser.add_argument("--out", default="outputs")
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--source-url", default=None)
    parser.add_argument("--split-description", default=None)
    args = parser.parse_args()

    source = Path(args.input)
    data = pd.read_csv(source)
    if args.text not in data or args.gold_spans not in data:
        raise SystemExit(f"Input must contain {args.text!r} and {args.gold_spans!r} columns.")

    languages = data["language"] if "language" in data else [None] * len(data)
    predictions = [
        detect(text, language)
        for text, language in zip(data[args.text], languages)
    ]
    totals = Counter(tp=0, fp=0, fn=0)
    by_type = defaultdict(Counter)
    redacted = []
    for text, raw_gold, predicted in zip(data[args.text], data[args.gold_spans], predictions):
        parsed = json.loads(raw_gold) if isinstance(raw_gold, str) else raw_gold
        gold = {
            (int(span["start"]), int(span["end"]), canonical_type(span["type"]))
            for span in (parsed or [])
        }
        guesses = set(predicted)
        correct, false_positive, missed = gold & guesses, guesses - gold, gold - guesses
        totals.update(tp=len(correct), fp=len(false_positive), fn=len(missed))
        for _, _, label in gold:
            by_type[label]["gold"] += 1
        for _, _, label in guesses:
            by_type[label]["predicted"] += 1
        for _, _, label in correct:
            by_type[label]["tp"] += 1
        for _, _, label in false_positive:
            by_type[label]["fp"] += 1
        for _, _, label in missed:
            by_type[label]["fn"] += 1

        value = str(text)
        for start, end, label in sorted(predicted, reverse=True):
            value = value[:start] + f"[REDACTED:{label}]" + value[end:]
        redacted.append(value)

    precision = totals["tp"] / max(1, totals["tp"] + totals["fp"])
    recall = totals["tp"] / max(1, totals["tp"] + totals["fn"])
    report = {
        "dataset": args.dataset,
        "source_url": args.source_url,
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "split_description": args.split_description,
        "rows": int(len(data)),
        "languages": {str(k): int(v) for k, v in data["language"].value_counts().sort_index().items()} if "language" in data else None,
        "gold_spans": int(totals["tp"] + totals["fn"]),
        "detected_spans": int(totals["tp"] + totals["fp"]),
        "true_positive_spans": int(totals["tp"]),
        "false_positive_spans": int(totals["fp"]),
        "false_negative_spans": int(totals["fn"]),
        "exact_span_precision": precision,
        "exact_span_recall": recall,
        "exact_span_f1": 2 * precision * recall / max(1e-12, precision + recall),
        "per_type": {
            label: {
                **{key: int(value) for key, value in counts.items()},
                "precision": counts["tp"] / max(1, counts["tp"] + counts["fp"]),
                "recall": counts["tp"] / max(1, counts["tp"] + counts["fn"]),
            }
            for label, counts in sorted(by_type.items())
        },
        "limitations": "Email and US-formatted SSN use regexes. Phone numbers use libphonenumber with default regions inferred from the nine language codes in this sample; unknown languages detect only explicitly international numbers. Exact-span results on synthetic multilingual PII are not real-world privacy assurance; names, addresses, IDs, and other classes are intentionally unsupported. Raw text and row-level redactions must remain local.",
    }
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"redacted_text": redacted, "detected_spans": [json.dumps(x) for x in predictions]}).to_csv(
        output / "redacted.csv", index=False
    )
    (output / "metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
