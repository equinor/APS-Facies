# -*- coding: utf-8 -*-
from os import environ
from flask import Flask, jsonify
from flask_cors import CORS

from src.utils.parsing import parse_signature
from src.api.ui import call


def _get_environ(variable_name, default,  divider=':'):
    return environ.get(variable_name, default).split(divider)


def _get_client_url():
    protocols = _get_environ('VUE_APP_APS_PROTOCOL', 'http:https')
    servers = _get_environ('VUE_APP_APS_SERVER', 'localhost')
    ports = _get_environ('VUE_APP_APS_GUI_PORT', '8080')
    return [
        '{protocol}://{server}:{port}'.format(protocol=protocol, server=server, port=port)
        for protocol in protocols
        for server in servers
        for port in ports
    ]


app = Flask(__name__)
cors = CORS(app, origins=_get_client_url())


@app.route('/<signature>', methods=['GET'])
def call_python(signature: str):
    method_name, args = parse_signature(signature)
    return jsonify(call(method_name, *args))


@app.route('/favicon.ico')
def favicon():
    return ''
