import logging

from flask import Flask, render_template, Response, redirect

from basic.db import close_connection
from dataEntries import routes as de_routes, adapter as data_adapter
from dataTrait import adapter as trait_adapter
from dataTraitManagement import adapter as trait_mgt_adapter
from dataTraitManagement import routes as dtm_routes

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

app = Flask(__name__)
app.register_blueprint(de_routes, url_prefix='/v1')
app.register_blueprint(dtm_routes, url_prefix='/v1')


@app.teardown_appcontext
def destroy_resources(exception):
    close_connection(exception)


@app.route('/', methods=['GET'])
def root():
    return redirect("/static/index.html", code=302)


with app.app_context():
    data_adapter.ensure_data()
    trait_mgt_adapter.ensure_data()
    trait_adapter.flush_data_trait_tables()

if __name__ == "__main__":
    app.run(debug=True)
