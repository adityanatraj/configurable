import json
from StringIO import StringIO

import yaml

# In the case of JSON, the module already provides
# all the functions we expect of a Format.
JSON = json


class YAML(object):
    """
        a simple wrapper of the yaml module to satisfy what a "Format" is:

            def load(fp):
            def loads(string):
            def dump(fp):
            def dumps(obj):
    """

    @staticmethod
    def load(fp):
        return yaml.load(fp)

    @staticmethod
    def loads(string):
        return yaml.load(StringIO(string))

    @staticmethod
    def dump(obj, fp):
        return yaml.dump(obj, stream=fp)

    @staticmethod
    def dumps(obj):
        temp_string = StringIO()
        yaml.dump(obj, stream=temp_string)
        return temp_string.getvalue()
