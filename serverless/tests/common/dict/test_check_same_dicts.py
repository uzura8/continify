import unittest
from app.common.dict import check_same_dicts


class TestCheckSameDicts(unittest.TestCase):
    def test_identical_dicts(self):
        dict_a = {'a': 1, 'b': 2, 'c': 3}
        dict_b = {'a': 1, 'b': 2, 'c': 3}
        ignore_keys = []
        self.assertTrue(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_different_values(self):
        dict_a = {'a': 1, 'b': 2, 'c': 3}
        dict_b = {'a': 1, 'b': 2, 'c': 4}
        ignore_keys = []
        self.assertFalse(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_ignored_keys(self):
        dict_a = {'a': 1, 'b': 2, 'c': 3}
        dict_b = {'a': 1, 'b': 2, 'c': 4}
        ignore_keys = ['c']
        self.assertTrue(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_missing_keys(self):
        dict_a = {'a': 1, 'b': 2}
        dict_b = {'a': 1, 'b': 2, 'c': 3}
        ignore_keys = ['c']
        self.assertTrue(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_empty_dicts(self):
        dict_a = {}
        dict_b = {}
        ignore_keys = []
        self.assertTrue(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_ignored_nonexistent_keys(self):
        dict_a = {'a': 1, 'b': 2}
        dict_b = {'a': 1, 'b': 2}
        ignore_keys = ['z']
        self.assertTrue(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_additional_keys_in_ignore_list(self):
        dict_a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        dict_b = {'a': 1, 'b': 2, 'c': 5, 'd': 6}
        ignore_keys = ['c', 'd']
        self.assertTrue(check_same_dicts(dict_a, dict_b, ignore_keys))

    def test_nested_dicts(self):
        dictA = {'a': 1, 'b': {'x': 5}}
        dictB = {'a': 1, 'b': {'x': 5}}
        self.assertTrue(check_same_dicts(dictA, dictB))


if __name__ == '__main__':
    unittest.main()
