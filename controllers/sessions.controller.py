from models import user_model
from utilities import utils
from flask import make_response
import bcrypt
import os


def login(current_session, parsedJsonCredentials)
   # if logged in return confimation
   if parsedJsonCredentials['username'] in current_session:
        if os.environ['LOGS'] != 'off':
            print('Logged in as %s' %
                escape(current_session[parsedJsonCredentials['username']]))
        return 'Logged in as %s' % escape(current_session[parsedJsonCredentials['username']])
    # if not logged in authenticate
    else:
        # check if user exists
        if user_model.User.exists(parsedJsonCredentials, 'username'):
            user = self.query.filter_by(username=parsedJsonCredentials['username']).first()
            print('user', user)
            # match PW
        else:
            if os.environ['LOGS'] != 'off':
                print('username does not exist')
            return 'user does not exist'
            



