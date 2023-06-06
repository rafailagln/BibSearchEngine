import unittest
from relevancy import Relevancy


class TestRelevancy(unittest.TestCase):

    def test_cosine_similarity(self):
        self.assertAlmostEqual(Relevancy.cosine_similarity('I love apples', 'I love apples'), 1)
        self.assertAlmostEqual(Relevancy.cosine_similarity('I love apples', 'I love oranges'), 0.7, 1)
        self.assertAlmostEqual(Relevancy.cosine_similarity('I love apples', 'We hate apples'), 0.3, 1)
        self.assertAlmostEqual(Relevancy.cosine_similarity('I love apples', 'Completely different sentence'), 0)
        self.assertAlmostEqual(Relevancy.cosine_similarity('I love apples', ''), 0)
        self.assertAlmostEqual(Relevancy.cosine_similarity('', ''), 0)


if __name__ == '__main__':
    unittest.main()
