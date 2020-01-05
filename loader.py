
import os
import psycopg2
import flask

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class App:
    def __init__(self):
        print('init')

    def create_app(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if os.environ['FLASK_ENV'] == 'production' or os.environ['FLASK_ENV'] == 'prod_testing':
            app.secret_key = bytes(os.environ['SECRET_KEY'], encoding='utf-8')
            # app.permanent_session_lifetime = timedelta(hours=24)
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROD_DB')
            DATABASE_URL = app.config['SQLALCHEMY_DATABASE_URI']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            if os.environ['LOGS'] != 'off':
                print('app.py: Prod DB')
                print('connection', conn)
        elif os.environ['FLASK_ENV'] == 'development':
            app.secret_key = bytes(os.environ['SECRET_KEY'], encoding='utf-8')
            # app.permanent_session_lifetime = timedelta(hours=24)
            if os.environ['LOGS'] != 'off':
                print('app.py: dev DB')
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DEV_DB']
        elif os.environ['FLASK_ENV'] == 'dev_testing':
            app.secret_key = b'12345678910-not-my-real-key'
            if os.environ['LOGS'] != 'off':
                print('app.py: testing DB')
            app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////test_db.db"
        db = SQLAlchemy(app)

        return {
            'app': app,
            'db': db
        }
