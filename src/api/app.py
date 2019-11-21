# -*- coding: utf-8 -*-
from os import environ, urandom
from flask import Flask, jsonify
from flask_cors import CORS

from src.utils.parsing import parse_signature
from src.api.ui import call


def _get_environ(variable_name, default, divider=':'):
    value = environ.get(variable_name, default)
    if value is None:
        value = ''
    if isinstance(value, str):
        value = value.split(divider)
    return value


def _get_client_url():
    protocols = _get_environ('VUE_APP_APS_PROTOCOL', 'http:https')
    servers = _get_environ('VUE_APP_APS_SERVER', 'localhost:127.0.0.1')
    ports = (
        _get_environ('VUE_APP_APS_GUI_PORT', '8080')
        + _get_environ('VUE_APP_APS_API_PORT', '5000')
    )
    return [
        '{protocol}://{server}:{port}'.format(protocol=protocol, server=server, port=port)
        for protocol in protocols
        for server in servers
        for port in ports
    ]


app = Flask(__name__)
app.secret_key = urandom(64)
app.debug = _get_environ('FLASK_DEBUG', False)

cors = CORS(app)  #, origins=_get_client_url())


@app.route('/<path:signature>', methods=['GET'])
def call_python(signature: str) -> str:
    method_name, args = parse_signature(signature)
    return jsonify(call(method_name, *args))


@app.route('/favicon.ico')
def favicon():
    return ''


if __name__ == '__main__':
    app.run(
        host=_get_environ('VUE_APP_APS_SERVER', '127.0.0.1'),
        port=_get_environ('VUE_APP_APS_API_PORT', 5000),
        debug=True,
    )
