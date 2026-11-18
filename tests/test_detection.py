import unittest

from main import canonical_type, detect, luhn_valid, redact_text


class PiiDetectionTests(unittest.TestCase):
    def test_detects_supported_exact_spans(self):
        text = "Email alice@example.com; SSN 123-45-6789; phone +1 650-253-0000."
        spans = detect(text, "en")
        self.assertIn((text.index("alice@example.com"), text.index("alice@example.com") + len("alice@example.com"), "email"), spans)
        self.assertIn((text.index("123-45-6789"), text.index("123-45-6789") + len("123-45-6789"), "ssn"), spans)
        self.assertIn((text.index("+1 650-253-0000"), text.index("+1 650-253-0000") + len("+1 650-253-0000"), "phone"), spans)

    def test_detects_luhn_valid_card_and_rejects_bad_checksum(self):
        text = "Card 4111 1111 1111 1111; fake 4111 1111 1111 1112."
        spans = detect(text)
        start = text.index("4111 1111 1111 1111")
        self.assertIn((start, start + len("4111 1111 1111 1111"), "creditcardnumber"), spans)
        self.assertTrue(luhn_valid("4111 1111 1111 1111"))
        self.assertFalse(luhn_valid("4111 1111 1111 1112"))

    def test_uses_explicit_international_number_without_language(self):
        text = "Call +49 30 1234567."
        spans = detect(text)
        start = text.index("+49")
        self.assertIn((start, start + len("+49 30 1234567"), "phone"), spans)

    def test_normalizes_dataset_label_aliases(self):
        self.assertEqual(canonical_type("Phone"), "phone")
        self.assertEqual(canonical_type("SocialNum"), "ssn")

    def test_redacts_overlapping_spans_without_corrupting_offsets(self):
        text = "A 4111 1111 1111 1111 Z"
        start = text.index("4111")
        overlapping = [
            (start, start + 19, "creditcardnumber"),
            (start + 5, start + 14, "phone"),
        ]
        self.assertEqual(redact_text(text, overlapping), "A [REDACTED:multiple] Z")

    def test_redaction_leaves_unmatched_text_and_handles_empty_spans(self):
        self.assertEqual(redact_text("keep this", []), "keep this")
        self.assertEqual(redact_text("a secret z", [(2, 8, "email")]), "a [REDACTED:email] z")


if __name__ == "__main__":
    unittest.main()

