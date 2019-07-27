from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app = Flask(__name__)
app.config.from_pyfile("flask.cfg")
app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI'],
    SQLALCHEMY_TRACK_MODIFICATIONS=app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
)

db = SQLAlchemy()
