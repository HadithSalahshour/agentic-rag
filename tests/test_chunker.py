import unittest

from ingestion.chunker import chunk


class ChunkerTests(unittest.TestCase):
    def setUp(self):
        self.document = {
            "text": "one two three four five six",
            "source": "demo.txt",
            "filename": "demo.txt",
        }

    def test_creates_overlapping_chunks(self):
        chunks = chunk(self.document, size=3, overlap=1)

        self.assertEqual(
            [item["text"] for item in chunks],
            ["one two three", "three four five", "five six"],
        )
        self.assertEqual(
            [item["chunk_index"] for item in chunks],
            [0, 1, 2],
        )

    def test_empty_document_returns_no_chunks(self):
        document = {**self.document, "text": ""}
        self.assertEqual(chunk(document), [])

    def test_rejects_non_positive_size(self):
        with self.assertRaises(ValueError):
            chunk(self.document, size=0)

    def test_rejects_invalid_overlap(self):
        for overlap in (-1, 3, 4):
            with self.subTest(overlap=overlap):
                with self.assertRaises(ValueError):
                    chunk(self.document, size=3, overlap=overlap)


if __name__ == "__main__":
    unittest.main()
