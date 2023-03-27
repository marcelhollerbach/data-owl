import logging
import os
from functools import wraps

from flask import session, redirect, url_for, request, Response, has_request_context

NORMAL = "NORMAL"
LOCALDEV = "LOCALDEV"

ALLOWED_RUN_MODES = [NORMAL, LOCALDEV]


def parse_mode():
    run_mode = os.getenv("RUN_MODE", NORMAL)
    if run_mode not in ALLOWED_RUN_MODES:
        logging.error("run-mode not known, falling back to NORMAL")
        run_mode = NORMAL
    if run_mode == LOCALDEV:
        logging.info("RUNNING IN LOCAL MODE!!!!")
    return run_mode


mode = parse_mode()


def ensure_local_user_session():
    # ensure that the IP address is only local
    session["user"] = {
        'access_token': 'Nice-Try',
        'id_token': 'Nice-Try',
        'scope': 'openid profile email', 'expires_in': 86400, 'token_type': 'Bearer', 'expires_at': 1679763806,
        'userinfo': {'nickname': 'mail', 'name': 'Marcel Hollerbach',
                     'picture': 'https://s.gravatar.com/avatar/5278389ed83179df02cd3b108f6a39b5?s='
                                '480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fma.png',
                     'updated_at': '2023-03-24T17:01:15.904Z', 'email': 'mail@bu5hm4n.de', 'email_verified': False,
                     'iss': 'https://dev-mh6upm9d.eu.auth0.com/', 'aud': 'pfJx9RSAgM9PE7TeLPYRmfR9U5aYY7yd',
                     'iat': 1679677317, 'exp': 1679713317, 'sub': 'auth0|6293a18f79f994006901390b',
                     'sid': 'pLu_duRSePbFuLUI4kigiFo0bNhp340X', 'nonce': '7EOWXEqSWnWgcep6Gucy'}}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if mode == NORMAL:
            if "user" not in session:
                return redirect(url_for('auth.login'))
        else:
            if request.remote_addr != '127.0.0.1':
                logging.error("Remote is not localhost!")
                return Response(status=404, response='This is not a connection from localhost.')
            else:
                ensure_local_user_session()
        return f(*args, **kwargs)

    return decorated_function


def fetch_author() -> str:
    current_user = session["user"]
    return current_user.get('userinfo').get('email')


def fetch_username():
    current_user = session.get("user", None)
    if current_user is None:
        return "Not-Logged-In"
    else:
        return current_user.get('userinfo').get('name')


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.user = fetch_username()
        else:
            record.user = None

        return super().format(record)


formatter = RequestFormatter(
    '%(asctime)s %(levelname)s %(name)s %(threadName)s [%(user)] : %(message)s'
)
