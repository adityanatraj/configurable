# Configurable

Maybe you want to have a persisted configuration file that's:
    - in either JSON or YAML format
    - can be loaded or saved to

```bash
$ cat config.yml
---
name: configurable

```

Then you could use the `Configurable` like:

```py
>>> config = Configurable(local_file='config.yml')
>>> config['name']
'configurable'
>>> config['g'] = ['wow']
>>> config.save()
```

But maybe you also have a Flask application.

```py
simple_api = Flask('test_api')
simple_api.config['name'] = 'inflexible'

@simple_api.route('/hello', methods=['GET'])
def hello():
    return 'hello. I am {}'.format(simple_api.config['name'])
```

Depending on whether your application requires configuration
values before "it is ready" or not, you can use this differently.

If your app is simpler and only uses config values "lazily", you can:

```py
from flask import current_app

simple_api = Flask('test_api')

@simple_api.route('/hello', methods=['GET'])
def hello():
    return 'hello. I am {}'.format(current_app.config['name'])

Configurable(flask_app=simple_api, local_file='config.yml')

```

Note the import of `current_app` and using that as the reference for the config.


If your app uses configuration values during it's initialization you can instead:

```py
from flask import current_app

class MyApp(Flask):
    def __init__(self, ...):
        super(...).__init__(...)
        Configurable(flask_app=self, local_file='config.yml')
        
complex_api = MyApp()

@complex_api.route('/hello', methods=['GET'])
def hello():
    return 'hello. I am {}'.format(current_app.config['name'])

```

If that was the case, then what you may have also noticed is that your API got
hijacked. `Configurable` when connected to a Flask application provides:

1. `GET /config/` - returns json of current configuration
2. TODO: `POST /config/` - allows setting the config via API

A limitation of this is that you can't have your app use `/config/` as a base to any 
route.