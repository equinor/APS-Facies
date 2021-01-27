from werkzeug.serving import run_with_reloader

from gevent.pywsgi import WSGIServer


from aps.api.app import app


@run_with_reloader
def run_server():
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()


run_server()
