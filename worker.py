from utilities import utils
from rq import Worker, Queue, Connection
from dotenv import load_dotenv, find_dotenv
import os
import redis
import scraper
from flask import Flask
import flask
import psycopg2
from flask_sqlalchemy import SQLAlchemy
import app

load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))


def create_app():
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
        app.testing = True
        app.secret_key = b'12345678910-not-my-real-key'
        if os.environ['LOGS'] != 'off':
            print('app.py: testing DB')
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    db = SQLAlchemy(app)
    app.db = db
    return {
        'app': app,
        'db': db
    }


def worker():
    # app = create_app()
    app = create_app()
    print('app', app)
    app['app'].app_context()
    # init db
    # db.init_app(app)
    listen = ['high', 'default', 'low']

    redis_url = os.environ['REDISTOGO_URL']
    conn = redis.from_url(redis_url)
    queue = Queue(connection=conn)
    # result = queue.enqueue(utils.count_words_at_url, 'http://heroku.com')
    result = queue.enqueue(scraper.driver_scraper)
    print('RES', result)

    if __name__ == '__main__':
        with Connection(conn):
            worker = Worker(map(Queue, listen))
            worker.work()
