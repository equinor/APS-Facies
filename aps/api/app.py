# -*- coding: utf-8 -*-
from os import environ, urandom

from flask import Flask, jsonify, request
from flask.cli import main

from aps.api.ui import call
from aps.utils.parsing import parse_signature


def _get_environ(variable_name, default, divider=':'):
    value = environ.get(variable_name, default)
    if value is None:
        value = ''
    if isinstance(value, str) and divider in value:
        value = value.split(divider)
    return value


app = Flask(__name__)
app.secret_key = urandom(64)
app.debug = _get_environ('FLASK_DEBUG', False)


@app.route('/api/<path:method>', methods=['POST'])
def call_python(method: str) -> str:
    signature = f'{method}({request.data.decode()})'
    method_name, args = parse_signature(signature)
    return jsonify(call(method_name, *args))


@app.route('/favicon.ico')
def favicon():
    return ''


try:
    project
except NameError:
    if 'RMS_PROJECT_PATH' in environ:
        # Ensure "project" is available as a global variable
        # similar to what ui.py expects
        import roxar

        project = roxar.Project.open(environ['RMS_PROJECT_PATH'])
        __builtins__ = globals()['__builtins__']  # load the module
        if not hasattr(__builtins__, 'project'):
            setattr(__builtins__, 'project', project)
    else:
        raise RuntimeError('No project available, and RMS_PROJECT_PATH is not set')


if __name__ == '__main__':
    main()
