import unittest
from backend.text_processing import clean_text, chunk_text, repair_symbol_text, extract_page_text
from backend.prompts import build_rag_prompt


class MathPipelineTests(unittest.TestCase):
    def test_preserves_notation_and_labels(self):
        text = "Definition (1): A ∩ B ⊆ A\nExample: ∅ ∈ {∅}; x² • à"
        self.assertEqual(clean_text(text), text)
        self.assertEqual(chunk_text(text, 'lecture.pdf', 8)[0]['text'], text)

    def test_symbol_repair_is_font_specific(self):
        self.assertEqual(repair_symbol_text('A Ç B È C', {'/BaseFont': '/ABC+SymbolMT'}), 'A ∩ B ∪ C')
        self.assertEqual(repair_symbol_text('È Ç', {'/BaseFont': '/Arial'}), 'È Ç')

    def test_real_lecture_union(self):
        from pathlib import Path
        from pypdf import PdfReader
        reader = PdfReader(Path(__file__).resolve().parent.parent / 'data/compilers/2140_lexer_2025.pdf')
        text = extract_page_text(reader.pages[7])
        self.assertIn('∪', text)
        self.assertNotIn('È', text)
        self.assertIn('Definition', text)

    def test_chunk_overlap_and_pages(self):
        chunks = chunk_text('a b\nc d e', 'lecture.pdf', 2, chunk_size=3, overlap=1)
        self.assertEqual([c['text'] for c in chunks], ['a b\nc', 'c d e'])
        self.assertTrue(all(c['page'] == 2 for c in chunks))
        self.assertEqual(chunk_text('', 'empty.pdf'), [])

    def test_prompt_notation(self):
        prompt = build_rag_prompt('intersection?', ['A ∩ B'])
        self.assertIn(r'\cap', prompt)
        self.assertIn('A ∩ B', prompt)
        self.assertIn('missing or ambiguous', prompt)


if __name__ == '__main__':
    unittest.main()
