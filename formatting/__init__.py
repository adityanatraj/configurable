from formatting.formats import YAML, JSON


class FormatFactory(object):
    FORMATS = {
        "yml": YAML,
        "yaml": YAML,
        "json": JSON,
    }

    @staticmethod
    def get_formatter(format_name='yml'):
        """
        :param format_name: the format you'd like to use default: yaml
            also accepts: yml | yaml -> yaml, json -> json
         :type format_name: str
        """
        if (not format_name) or (format_name not in FormatFactory.FORMATS):
            format_name = 'yml'

        return Formatter(format_name, FormatFactory.FORMATS[format_name])


class Formatter(object):
    def __init__(self, format_name, with_format):
        """
        A Formatter wraps a class that implements the Format interface:

            def load(self, fp):
            def loads(self, string):
            def dump(self, obj, fp):
            def dumps(self, obj):

        :param format_name: the name of the format
         :type format_name: str

        :param with_format: module, class, or object implementing Format
         :type with_format: ~formatting.Format
        """
        self.format_name = format_name
        self.format = with_format

    def get_fmt(self):
        return self.format_name

    def load(self, fp):
        return self.format.load(fp)

    def loads(self, string):
        return self.format.loads(string)

    def dump(self, obj, fp):
        return self.format.dump(obj, fp)

    def dumps(self, obj):
        return self.format.dumps(obj)
