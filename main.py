import logging

from flask import redirect

from app import app
from basic.annotations import login_required
from basic.db import close_connection
from dataEntries import adapter as data_adapter
from dataTrait import adapter as trait_adapter
from dataTraitManagement import adapter as trait_mgt_adapter
from routes import init_routes

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)


@app.teardown_appcontext
def destroy_resources(exception):
    close_connection(exception)


@app.route('/', methods=['GET'])
@login_required
def root():
    return redirect("/static/index.html", code=302)


with app.app_context():
    data_adapter.ensure_data()
    trait_mgt_adapter.ensure_data()
    trait_adapter.flush_data_trait_tables()

init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
