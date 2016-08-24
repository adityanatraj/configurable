import unittest

from configurable import Configurable


class DictnessTest(unittest.TestCase):
    def test_get(self):
        test_config = {
            'a': 1,
            'b': {
                'c': 3,
                'd': [True]
            }
        }

        conf_api = Configurable(defaults=test_config)

        # test existing get
        self.assertEquals(test_config['a'], conf_api['a'])

        # test non-existing get
        with self.assertRaises(Exception):
            doesnt_exist = conf_api['e']

        # test nested value get
        self.assertEquals([True], conf_api['b']['d'])

    def test_get_default(self):
        test_config = {
            'a': 1,
            'b': {
                'c': 3,
                'd': [True]
            }
        }

        conf_api = Configurable(defaults=test_config)

        # test existing get
        self.assertEquals(test_config['a'], conf_api.get('a', 10))

        # test non-existing get
        self.assertEquals(10, conf_api.get('e', 10))

        # test nested value get
        self.assertEquals([True], conf_api.get('b').get('d'))

        # test nested value get defaulted
        self.assertEquals([False], conf_api.get('b').get('r', [False]))

    def test_get_with_flask_config(self):
        test_config = {
            'a': 1,
            'b': {
                'c': 3,
                'd': [True]
            }
        }

        conf_api = Configurable(defaults=test_config)
        # let's inject a flask config without having to make a whole app
        conf_api._config = {'DEBUG': True}

        # test flask _config existing get
        self.assertTrue(conf_api['DEBUG'])

    def test_set(self):

        test_conf = {
            'a': 1,
            'b': {
                'c': '3',
            }
        }

        conf_api = Configurable(defaults=test_conf)
        conf_api['b']['e'] = 10
        conf_api['d'] = {'r': {'a': [True]}}

        expected_conf = {
            'a': 1,
            'b': {
                'c': '3',
                'e': 10
            },
            'd': {'r': {'a': [True]}}
        }
        self.assertEquals(expected_conf, conf_api.config)
