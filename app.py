import logging
from os import environ as env

from flask import Flask

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
