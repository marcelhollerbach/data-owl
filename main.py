import logging

from app import app
from basic.db import close_connection
from routes import init_routes

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)


@app.teardown_appcontext
def destroy_resources():
    close_connection()


init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
