from models import user_model
from utilities import utils
from flask import make_response, jsonify
import bcrypt
import os

KEYS = ['drivers_arr', 'teams_arr', 'user_id']


# registers user to db -returns response and code
def register(parsedData):
    try:
        # create temp user obj
        print(parsedData)
        exists = user_model.User.exists(parsedData['id'])
        print('EX', exists)
        user = user_model.User.new(parsedData['id'], parsedData)
        if user:
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
