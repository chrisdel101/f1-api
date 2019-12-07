from models import user_model
from utilities import utils
from flask import make_response
import os

KEYS = ['drivers_arr', 'teams_arr', 'user_id']


def handle_user(data):
    try:
        data = _filter_user_data(data, KEYS)
        print('dat', data)
        # create new istance
        user = user_model.User.new(data['user_id'], data)
        # check if exists
        exists = user.exists(user.id)
        if os.environ['LOGS'] != 'off':
            print('user id', user.id)
            print('drivers', user.driver_data)
            print('teams', user.team_data)
            print('exists', exists)
        if exists:
            user.update(data)
        else:
            user.insert()
        return 'Success'
    except Exception as e:
        print('Error in handle_user', e)
        return 1


# remove any keys not included in the keys_allowed list
def _filter_user_data(data, keys_allowed):
    # for datum in data.keys():
    #     print(datum)
    # remove key not in the keys_allowed list
    return {k: v for k, v in data.items() if k in keys_allowed}
