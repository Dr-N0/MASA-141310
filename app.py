import os
from lockheed_141310 import app

if __name__ == "__main__":
    app.run(host=app.config['IP'], port=app.config['PORT'])
