from models import user_model
from utilities import utils
import flask
from flask import escape, make_response, jsonify
from flask_login import LoginManager, current_user, login_required, login_user
import bcrypt
import os


# return T of F if user is logged in
def login(parsedJsonCredentials):
    try:
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
                    print('user exists and PW success.')
                # login user
                try:
                    # flask-login
                    login_user(user, remember=True)
                    print('Logged in successfully:',
                          current_user.username)
                    # make auth token
                    auth_token = user.encode_auth_token(user.id)
                    if auth_token:
                        responseObject = {
                            'status': 'success',
                            'message': 'logged in',
                            'auth_token': auth_token.decode()
                        }
                    return make_response(jsonify(responseObject), 200)
                except Exception as e:
                    print('error in login inner e', e)
                    raise e
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
