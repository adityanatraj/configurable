import json
import logging
import os
from threading import Lock

from flask import Flask

from formatting import FormatFactory


class Configurable(object):
    def __init__(self, flask_app=None, defaults=None, local_file=None,
                 local_file_formatter=FormatFactory.get_formatter(), logger=None):
        """
        :param flask_app: the application you want to make Configurable
         :type flask_app: flask.Flask

        :param defaults: (optional) values you want to start off with
         :type defaults: dict

        :param local_file: (optional) path to a local config file
         :type local_file: str

        :param local_file_formatter: (optional) local file formatter
            default: Formatter(fmt='yml')

            the Formatter class is currently both the interface required
            as well as the default implementation covering {yaml, json}..

            TODO: fix mix of interface definition vs implementation or think about it?
         :type local_file_formatter: utils.configuration.Formatter

        :param logger: (optional) the logger you'd like to use with this
         :type logger: logging.Logger
        """
        self._conf_app = None  # used to hold the /config/ app
        self._wsgi_app = None  # used to retain your app's _wsgi_app
        self._config = None  # used to retain your app's config

        if flask_app:
            self.attach_to_flask_app(flask_app)

        self.config = defaults or {}
        self.lock = Lock()

        self.local_file = local_file
        self.local_file_formatter = local_file_formatter

        self.logger = logger

        if local_file:
            self.load()

    def attach_to_flask_app(self, application):
        """
        While this method gets called if you initialize your Configurable with
        a Flask application, there may be instances where you'd like to attach it
        later.

        :param application: a flask application to attach to
         :type application: flask.Flask
        """
        self._conf_app = self.make_config_app()
        self._wsgi_app = application.wsgi_app
        self._config = application.config
        setattr(application, 'wsgi_app', self)
        setattr(application, 'config', self)

    def make_config_app(self):
        """
            this is where the web application that lives at `/config/`
            gets defined.
        """
        config_app = Flask('configurable')

        @config_app.route('/config/', methods=['GET'])
        def get_config():
            return json.dumps(self.config)

        return config_app

    def load(self):
        """
            loads the configuration into the state config. thread-safe
        """
        with self.lock:
            self.config = Configurable.load_from_file(self.local_file,
                                                      self.local_file_formatter,
                                                      logger=self.logger)

    def merge_in_dict(self, dict_to_merge, _cur_dict=None, _cur_path=None):
        """
        Notes:
            we can only really merge dicts. the primitive types obviously
            get overwritten, but when questions of lists and other
            data structures arise it's unclear what 'merging' might mean.

        :param dict_to_merge: the dict with the new state you want
         :type dict_to_merge: dict

        :param _cur_dict: not for you, helper for recursion
         :type _cur_dict: dict

        :param _cur_path: not for you, helper for recursion
         :type _cur_path: list of str

        :returns dict
            dict[flattened_path] => (new_value, old_value)
            - the paths are flattened using '.'-notation with
            - TODO: see if this is a good idea. current reasons:
                1. it's easy to len(dict) and see # of change
                2. i see most of its use in writing it as a log
                   and for verification. i dont think it matters
                   to keep the structure (though this does allow
                   full regeneration and '.' notation is pretty
                   well understood visually)
                3. it's easier than to have to recurse through a
                   nested change dict when going through it?
        """
        current_dict = _cur_dict or self.config
        cur_path = _cur_path or []
        changed_values = {}
        for k, v in dict_to_merge.iteritems():
            cur_path.append(k)
            if k in current_dict:
                old_value = current_dict[k]
                if isinstance(v, dict) and isinstance(old_value, dict):
                    deeper_changes = self.merge_in_dict(v,
                                                        _cur_dict=old_value,
                                                        _cur_path=cur_path)
                    changed_values.update(deeper_changes)
                else:
                    current_dict[k] = v
                    flat_path = '.'.join(cur_path)
                    changed_values[flat_path] = (v, old_value)
            else:
                current_dict[k] = v
                flat_path = '.'.join(cur_path)
                changed_values[flat_path] = (v, None)
        return changed_values

    @staticmethod
    def load_from_file(file_path, file_formatter, logger=None):
        """
        :param file_path: path to a local file to load into self.config
         :type file_path: str

        :param file_formatter: formatter of that file
         :type file_formatter: utils.configuration.Formatter

        :param logger: (optional) a logger to write errors to
         :type logger: logging.Logger

         :return dict
        """
        if not file_path:
            return {}

        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)

        if file_formatter.get_fmt() != ext:
            # TODO:  maybe do something when chosen formatter != extension of local file
            pass

        try:
            with open(file_path, 'rb') as input_file:
                logger and logger.info('loaded config at {}', file_path)
                return file_formatter.load(input_file)
        except IOError:
            if logger is not None:
                logger.error('couldnt open file at {}. no config loaded.', file_path)
            return {}

    def save(self):
        """
            saves the state config to the local file. thread-safe
        """
        if self.local_file:
            with self.lock:
                Configurable.save_to_file(self.config,
                                          self.local_file,
                                          self.local_file_formatter,
                                          logger=self.logger)

    @staticmethod
    def save_to_file(config, file_path, file_formatter, logger=None):
        """
        :param config: the configuration dict you'd like to write
         :type config: dict

        :param file_path: path to a local file to load into self.config
         :type file_path: str

        :param file_formatter: formatter of that file
         :type file_formatter: utils.configuration.Formatter

        :param logger: (optional) a logger to write errors to
         :type logger: logging.Logger
        """
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)

        if file_formatter.get_fmt() != ext:
            # TODO: do something when chosen formatter != extension of local file
            logger and logger.warning('format name doesnt match file extension')
            pass

        try:
            with open(file_path, 'wb') as output_file:
                file_formatter.dump(config, output_file)
                logger and logger.info('saved to {}.', file_path)
        except IOError:
            logger and logger.error('failed to save to {}', file_path)

    def __getitem__(self, item):
        """
        note: this function checks if it's in the consumed config and tries to
              return that, if not found in your current config.
        """
        try:
            return self.config[item]
        except KeyError as key_error:
            if self._config:
                return self._config[item]
            raise key_error

    def get(self, item, default=None):
        return self.config.get(item, default)

    def __eq__(self, other):
        return self.config.__eq__(other)

    def __repr__(self):
        return json.dumps(self.config)

    def __setitem__(self, key, value):
        self.config.__setitem__(key, value)
        if self.local_file:
            self.save()

    def __call__(self, environ, start_response):
        """
        :param environ: a WSGI environ bundle
         :type environ: dict

        :param start_response: something
         :type start_response: flask.Response
        """
        if environ['PATH_INFO'].startswith('/config/'):
            self.logger and self.logger.info('saw config in the path. stealing request.')
            return self._conf_app(environ, start_response)
        else:
            return self._wsgi_app(environ, start_response)
