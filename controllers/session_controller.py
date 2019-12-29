from models import user_model
from utilities import utils
from flask import make_response
import bcrypt
import os


# return T of F if user is logged in
def login(current_session, parsedJsonCredentials):
    try:
        print(current_session, parsedJsonCredentials)
    # if logged in return confimation
        if parsedJsonCredentials['username'] in current_session:
            if os.environ['LOGS'] != 'off':
                print('Logged in as %s' %
                      escape(current_session[parsedJsonCredentials['username']]))
            return True
        # if not logged in authenticate
        else:
            # create temp user obj
            user = user_model.User.new(
                parsedJsonCredentials['id'], parsedJsonCredentials)
            # check if user obj exists in DB
            if user.exists(parsedJsonCredentials['username'], 'username'):
                # find user in DB
                query = user.query.filter_by(
                    username=parsedJsonCredentials['username']).first()
                # check password matches DB password
                matches = utils.check_hashed_password(
                    parsedJsonCredentials['password'], query.password)
                print(matches)

                # match PW
            else:
                if os.environ['LOGS'] != 'off':
                    print('username does not exist. register user.')
                return False
    except Exception as e:
        print('error in login', e)
        raise e
