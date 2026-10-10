from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server

from app.main import app


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


if __name__ == "__main__":
    with make_server("127.0.0.1", 8000, app, server_class=ThreadingWSGIServer) as server:
        print("GD Arena Flask WSGI server running at http://127.0.0.1:8000")
        server.serve_forever()
