import json
import unittest

from flask import Flask
from flask import current_app

from configurable import Configurable


class APITest(unittest.TestCase):

    def setUp(self):

        simple_api = Flask("test_api")

        @simple_api.route('/hello', methods=['GET'])
        def hello():
            return 'hello'

        @simple_api.route('/test_config', methods=['GET'])
        def config_test():
            return repr(current_app.config)

        self.test_app = simple_api

    def test_app_wrap(self):

        test_config = {
            'a': 1,
            'b': {
                'c': [True],
                'd': 'wowowow'
            }
        }

        Configurable(flask_app=self.test_app, defaults=test_config)

        # 1. can we still get what the API delivers ?
        client = self.test_app.test_client()
        response = client.get('/hello')
        self.assertEquals("hello", response.data)

        # 2. can we access the /config/ route ?
        response = client.get('/config/')
        response_json = json.loads(response.data)
        self.assertEquals(response_json, test_config)

        # 3. can the underlying application use the .configuration ?
        response = client.get('/test_config')
        response_json = json.loads(response.data)
        self.assertEquals(response_json, test_config)
