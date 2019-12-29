from models import user_model
from utilities import utils
from flask import make_response
import bcrypt
import os


def authenticate(jsonCredentials):
    password = b"jsonCredentials['password']"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    if bcrypt.checkpw(password, hashed):
        print("It Matches!")
    else:
        print("It Does not Match :(")


def login(current_session, parsedJsonCredentials)
   # if logged in return confimation
   if parsedJsonCredentials['username'] in current_session:
        print('Logged in as %s' %
              escape(current_session[parsedJsonCredentials['username']]))
        return 'Logged in as %s' % escape(current_session[parsedJsonCredentials['username']])
    # if not logged in authenticate
    else:
