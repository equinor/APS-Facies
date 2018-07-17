# -*- coding: utf-8 -*-
from os import environ
from flask import Flask, jsonify
from flask_cors import CORS

from src.utils.parsing import parse_signature
from src.api.ui import call


def _get_client_url():
    protocol = environ.get('VUE_APP_APS_PROTOCOL', 'http')
    server = environ.get('VUE_APP_APS_SERVER', 'localhost')
    port = environ.get('VUE_APP_APS_GUI_PORT', '8080')
    return '{protocol}://{server}:{port}'.format(protocol=protocol, server=server, port=port)


app = Flask(__name__)
cors = CORS(app, origins=_get_client_url())


@app.route('/<signature>', methods=['GET'])
def call_python(signature: str):
    method_name, args = parse_signature(signature)
    return jsonify(call(method_name, *args))


@app.route('/favicon.ico')
def favicon():
    return ''
