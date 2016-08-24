import unittest

from formatting import FormatFactory


class FormatsTest(unittest.TestCase):
    """
    Tests for the `Format`s:

        These are tests for the `Format`s that can be used to read
        and write configuration files.

    Test steps:
        1. create a sample dict
        2. convert (1) to the desired format as a string
        TEST-1: (1) is a `str` (*)
        3. convert (2) back to a dict
        TEST-2: (1) == (3)

    note:
        [*] we add TEST-1 because if the formatter fails for some reason,
        it may be that 2 and 3 do nothing, making (1) trivially equal to (3).
        As a prevention, we note that if (2) is a `str`, it can't be equal to (3),
        in a case where TEST-2 would pass.

        TODO: have someone else verify that it is sufficient.

    """

    def setUp(self):
        self.test_dict = {
            'a': 1,
            'b': [2, 3, {'test': 'this'}],
            'c': {'d': 'e'}
        }

    def test_yaml_formatter(self):
        formatter = FormatFactory.get_formatter()
        self.assertEquals("yml", formatter.get_fmt())

        serialized = formatter.dumps(self.test_dict)
        self.assertTrue(isinstance(serialized, str))

        deserialized = formatter.loads(serialized)

        self.assertEquals(self.test_dict, deserialized)

    def test_json_formatter(self):
        formatter = FormatFactory.get_formatter(format_name="json")

        serialized = formatter.dumps(self.test_dict)
        self.assertTrue(isinstance(serialized, str))

        deserialized = formatter.loads(serialized)

        self.assertEquals(self.test_dict, deserialized)
