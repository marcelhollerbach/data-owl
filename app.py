import logging
from os import environ as env

from apiflask import APIFlask
from flask.logging import default_handler

from basic.annotations import formatter
from dataEntries import DataEntriesAdapter
from dataTrait.db import DataTraitAdapter
from dataTraitManagement import TraitManagementAdapter

default_handler.setFormatter(formatter)

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

app = APIFlask(__name__)
app.config['SPEC_FORMAT'] = 'yaml'
app.secret_key = env.get("APP_SECRET_KEY")

with app.app_context():
    DataEntriesAdapter.ensure_data()
    TraitManagementAdapter.ensure_data()
    DataTraitAdapter.flush_data_trait_tables()
