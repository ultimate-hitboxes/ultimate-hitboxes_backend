import os
from app import app

from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher
from cheroot.ssl.builtin import BuiltinSSLAdapter

#Start the server with a different port depending on the environment
if __name__ == "__main__":
    if os.environ.get("FLASK_ENV") != "production":
        app.run(port=5080, host="0.0.0.0", debug=True)
    else:

        my_app = WSGIPathInfoDispatcher({'/': app})
        server = WSGIServer(('0.0.0.0', 5443), my_app)

        ssl_cert = os.environ.get("CERT")
        ssl_key = os.environ.get("KEY")

        server.ssl_adapter =  BuiltinSSLAdapter(ssl_cert, ssl_key, None)
        
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()