import unittest

from main import canonical_type, detect


class PiiDetectionTests(unittest.TestCase):
    def test_detects_supported_exact_spans(self):
        text = "Email alice@example.com; SSN 123-45-6789; phone 415-555-0132."
        spans = detect(text)
        self.assertIn((text.index("alice@example.com"), text.index("alice@example.com") + len("alice@example.com"), "email"), spans)
        self.assertIn((text.index("123-45-6789"), text.index("123-45-6789") + len("123-45-6789"), "ssn"), spans)
        self.assertIn((text.index("415-555-0132"), text.index("415-555-0132") + len("415-555-0132"), "phone"), spans)

    def test_normalizes_dataset_label_aliases(self):
        self.assertEqual(canonical_type("Phone"), "phone")
        self.assertEqual(canonical_type("SocialNum"), "ssn")


if __name__ == "__main__":
    unittest.main()
