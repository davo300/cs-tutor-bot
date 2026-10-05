import unittest
from unittest.mock import Mock, patch
from backend.llm import ask_llama, clean_generated_answer
from backend.prompts import build_rag_prompt


class GenerationTests(unittest.TestCase):
    def test_repeated_paragraphs_removed(self):
        first = 'Kleene closure includes ε.'
        second = 'Positive closure uses one or more strings.'
        self.assertEqual(clean_generated_answer(f'{first}\n\n{second}\n\n{first}\n\n{second}'), f'{first}\n\n{second}')

    def test_different_math_not_removed(self):
        text = 'Intersection: $A \\cap B$.\n\nUnion: $A \\cup B$.'
        self.assertEqual(clean_generated_answer(text), text)

    def test_code_and_display_math_preserved(self):
        for text in ['```\nprint(1)\n\nprint(1)\n```', '$$\nA\n\nA\n$$']:
            self.assertEqual(clean_generated_answer(text), text)

    def test_end_marker_removed(self):
        self.assertEqual(clean_generated_answer('Answer.<END_ANSWER>\nExtra'), 'Answer.')

    @patch('backend.llm.get_hf_config', return_value=('https://example.test', 'test-token'))
    @patch('backend.llm.requests.post')
    def test_request_limits_repetition(self, post, config):
        response = Mock()
        response.json.return_value = {'generated_text': 'Answer.\n\nAnswer.<END_ANSWER>'}
        post.return_value = response
        self.assertEqual(ask_llama('prompt'), 'Answer.')
        parameters = post.call_args.kwargs['json']['parameters']
        self.assertFalse(parameters['do_sample'])
        self.assertFalse(parameters['return_full_text'])
        self.assertGreater(parameters['repetition_penalty'], 1)
        self.assertEqual(parameters['max_new_tokens'], 256)
        self.assertIn('<END_ANSWER>', parameters['stop'])
        self.assertLessEqual(len(parameters['stop']), 4)
        response.raise_for_status.assert_called_once()

    def test_prompt_has_completion_boundary(self):
        prompt = build_rag_prompt('Explain closure', ['Course context'])
        self.assertIn('State each point once', prompt)
        self.assertIn('<END_ANSWER>', prompt)


if __name__ == '__main__':
    unittest.main()
