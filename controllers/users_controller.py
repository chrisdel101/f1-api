from models import user_model
from flask import make_response, jsonify
import bcrypt
import flask
import os
import json
from utilities import utils

# registers user to db -returns response and code


def register(parsedData):
    try:
        # if user with this id exists - no instance
        exists_on_class = user_model.User.exists_on_class(parsedData['id'])
        if not exists_on_class:
            # create temp user obj
            user = user_model.User.new(parsedData['id'], parsedData)
            user.insert()
            auth_token = user.encode_auth_token(user.id)
            responseObject = {
                'status': 'success',
                'message': 'registered',
                'auth_token': auth_token.decode()
            }
            if os.environ['LOGS'] != 'off':
                print('user registered okay')
            return make_response(jsonify(responseObject), 201)
        else:
            if os.environ['LOGS'] != 'off':
                print('user already exists')
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject), 202)
    except Exception as e:
        print('exception in user_controller.register', e)
        raise e


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
            # check password matches DB password
            matches = utils.check_hashed_password(
                parsedJsonCredentials['password'], query.password)
            # if match PW return T
            if matches:
                # login user
                try:
                    # make auth token
                    auth_token = user.encode_auth_token(user.id)
                    if auth_token:
                        responseObject = {
                            'status': 'success',
                            'message': 'logged in',
                            'auth_token': auth_token.decode(),
                            'logged_in': True
                        }
                    if os.environ['LOGS'] != 'off':
                        print('user exists and PW success.')
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
            responseObject = {
                'status': 'failed',
                'message': 'not logged in',
                'logged_in': False
            }
            print("HERE")
            return make_response(jsonify(responseObject), 404)
    except Exception as e:
        print('error in login', e)
        raise e


# takes a response or a byte string
def status(auth_header):
    # if byte string type
    if type(auth_header) == 'bytes':
        auth_token = auth_header
    # if response type
    elif type(auth_header) == flask.wrappers.Response:
        auth_token = json.loads(auth_header.data)['auth_token']
    else:
        auth_token = ''
    if auth_token:
        resp = user_model.User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = user_model.User.query.filter_by(id=resp).first()
            responseObject = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    # 'admin': user.admin,
                    # 'registered_on': user.registered_on
                }
            }
            return make_response(jsonify(responseObject), 200)
        responseObject = {
            'status': 'fail',
            'message': resp
        }
        return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject))
