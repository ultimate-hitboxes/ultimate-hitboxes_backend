import os
from app import app

if __name__ == "__main__":
    if os.environ["Environment"] == "DEVELOPMENT":
        app.run(debug=True, port=5080)
    elif os.environ["Environment"] == "PRODUCTION":
        app.run(port=5443)
    else:
        print("No Environment set")
    