import os
from app import app

#Start the server with a different port depending on the environment
if __name__ == "__main__":
    if os.environ.get("ENV") != "prod":
        app.run(port=5080, host="0.0.0.0", debug=True)
    else:
        app.run(port=5443, host="0.0.0.0")