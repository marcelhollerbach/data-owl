import logging
from os import environ as env

from apiflask import APIFlask

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

app = APIFlask(__name__)
app.config['SPEC_FORMAT'] = 'yaml'
app.secret_key = env.get("APP_SECRET_KEY")
