# -*- coding: utf-8 -*-
from os import environ, urandom
from flask import Flask, jsonify, request
from flask.cli import main
from flask_cors import CORS, cross_origin

from aps.utils.parsing import parse_signature
from aps.api.ui import call


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

cors = CORS(app)


@app.route('/api/<path:method>', methods=['POST'])
@cross_origin()
def call_python(method: str) -> str:
    signature = f'{method}({request.data.decode()})'
    method_name, args = parse_signature(signature)
    return jsonify(call(method_name, *args))


@app.route('/favicon.ico')
def favicon():
    return ''


if __name__ == '__main__':
    main()
