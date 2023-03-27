import logging
from os import environ as env

from apiflask import APIFlask
from flask.logging import default_handler

from basic.annotations import formatter
from dataEntries import adapter as data_adapter
from dataTrait import adapter as trait_adapter
from dataTraitManagement import adapter as trait_mgt_adapter

default_handler.setFormatter(formatter)

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

app = APIFlask(__name__)
app.config['SPEC_FORMAT'] = 'yaml'
app.secret_key = env.get("APP_SECRET_KEY")


with app.app_context():
    data_adapter.ensure_data()
    trait_mgt_adapter.ensure_data()
    trait_adapter.flush_data_trait_tables()
