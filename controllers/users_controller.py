from models import user_model
from flask import make_response, jsonify
import bcrypt
import flask
import os
import json

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
