import os
from app import app

if __name__ == "__main__":
    if os.environ.get("ENV") != "prod":
        app.run(debug=True, host="0.0.0.0", port=5080)
    else:
        app.run(port=5443, host="0.0.0.0")
    