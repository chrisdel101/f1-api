from models import user_model
from utilities import utils
import flask
from flask import escape
from flask_login import login_user, current_user
import bcrypt
import os


# return T of F if user is logged in
def login(current_session, parsedJsonCredentials):
    try:
        # if logged session return confimation
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
                print('query', query)
                # check password matches DB password
                matches = utils.check_hashed_password(
                    parsedJsonCredentials['password'], query.password)
                print('match', matches)
                # if match PW return T
                if matches:
                    if os.environ['LOGS'] != 'off':
                        print('user exists and PW success. login success')
                    # login user
                    try:
                        print('USER', user)
                        login_user(user)
                        # authenticate user
                        # user.is_authenticated = True
                        print('Logged in successfully.', current_user.username)
                        return matches
                    except Exception as e:
                        print('error in inner e', e)
                # if not match return F
                else:
                    if os.environ['LOGS'] != 'off':
                        print(
                            'user exists but PW fails. login failed')
                    return matches
            else:
                if os.environ['LOGS'] != 'off':
                    print('username does not exist. login failed')
                return False
    except Exception as e:
        print('error in login', e)
        raise e
