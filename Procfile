# web: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program

web: gunicorn -b 0.0.0.0:$PORT app:app
worker: python worker.py

# got this at https://github.com/yefim/flask-heroku-sample
