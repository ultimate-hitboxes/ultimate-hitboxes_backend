import os
from app import app

#Start the server with a different port depending on the environment
if __name__ == "__main__":
    if os.environ.get("FLASK_ENV") != "production":
        app.run(port=5080, host="0.0.0.0", debug=True)
    else:
        app.run(port=5443, host="0.0.0.0", ssl_context=(os.environ.get("CERT"), os.environ.get("KEY")))