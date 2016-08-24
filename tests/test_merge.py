import unittest

from configurable import Configurable


class MergeTest(unittest.TestCase):
    def test_no_merge(self):
        base_conf = {
            'a': 1,
        }

        merge_in = {}

        conf_api = Configurable(defaults=base_conf)
        changes = conf_api.merge_in_dict(merge_in)

        # Check the changes: there shouldn't be any
        self.assertEquals(0, len(changes))

        self.assertEquals(base_conf, conf_api.config)

    def test_top_level_merge(self):
        base_conf = {'a': 1}

        merge_in = {'b': 2}

        conf_api = Configurable(defaults=base_conf)
        changes = conf_api.merge_in_dict(merge_in)

        expected = {'a': 1, 'b': 2}

        # Check the changes: 1 change where 'b' went from None -> 2
        self.assertEquals(1, len(changes))
        self.assertEquals({'b': (2, None)}, changes)

        self.assertEquals(expected, conf_api.config)

    def test_nested_merge(self):
        base_conf = {'a': 1, 'b': {'c': [True]}}

        merge_in = {'b': {'d': {'f': {1, 2, 3}}}}

        conf_api = Configurable(defaults=base_conf)
        changes = conf_api.merge_in_dict(merge_in)

        expected = {
            'a': 1,
            'b': {
                'c': [True],
                'd': {
                    'f': {1, 2, 3}
                }
            }
        }

        # Check the changes: 1 change where 'b.d' was set to {'f': {1, 2, 3}}
        self.assertEquals(1, len(changes))
        self.assertEquals({'b.d': ({'f': {1, 2, 3}}, None)}, changes)

        self.assertEquals(expected, conf_api.config)
