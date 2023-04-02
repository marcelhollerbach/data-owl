APP_SECRET_KEY=local-secret AUTH0_CLIENT_ID=XXX AUTH0_CLIENT_SECRET=XXX AUTH0_DOMAIN=XXX LOG=DEBUG RUN_MODE=LOCALDEV python ./main.py &
sleep 5
pytest -c system-pytest.ini
