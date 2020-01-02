from models import user_model
from utilities import utils
from flask import make_response, jsonify
import bcrypt
import os

KEYS = ['drivers_arr', 'teams_arr', 'user_id']


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
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            if os.environ['LOGS'] != 'off':
                print('user registered okay')
            return make_response((responseObject)), 201
        else:
            if os.environ['LOGS'] != 'off':
                print('user already exists')
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202
    except Exception as e:
        print('exception in user_controller.register', e)
        raise e
