import os
import tempfile
import unittest

from configurable import Configurable
from formatting import FormatFactory


class FileworkTest(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            'application': {
                'debug': False,
                'commit': 'something',
            },
            'mysql': {
                'host': 12345,
                'words': ['a', 'b', 'c']
            }
        }

    def test_load_from_file(self):
        """

        1. create temp file with desired config (use default format)
        2. create a ConfigurableAPI using that file as a config
        TEST desired config is equal to the APIs config

        """

        temp_file = tempfile.NamedTemporaryFile(delete=False)

        formatter = FormatFactory.get_formatter()
        formatter.dump(self.test_config, temp_file)
        temp_file.close()

        conf_api = Configurable(local_file=temp_file.name)
        os.unlink(temp_file.name)

        self.assertEquals(self.test_config, conf_api.config)

    def test_save_to_file(self):
        """

        1. create temp file with desired config (use default format)
        2. create a ConfigurableAPI using that file as a config
        3. delete the temp file
        4. save the config
        5. load the tempfile and check it's equal to the config

        """
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        formatter = FormatFactory.get_formatter()
        formatter.dump(self.test_config, temp_file)
        temp_file.close()

        conf_api = Configurable(local_file=temp_file.name)
        os.unlink(temp_file.name)

        conf_api.save()

        with open(temp_file.name, 'rb') as infile:
            conf_from_file = formatter.load(infile)

        self.assertEquals(self.test_config, conf_from_file)
        os.unlink(temp_file.name)

