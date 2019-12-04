from models import user_model
from utilities import utils
KEYS = ['driver_data', 'team_data', 'user_id']


def handle_user(data):
    try:
        data = _filter_user_data(data, KEYS)
        # create new istance
        user = user_model.User.new(data['user_id'], data)
        # check if exists
        exists = user.exists(user.id)
        if exists:
            user.update(data)
        else:
            user.insert()
        return 'Complete'
    except Exception as e:
        print('Error in handle_user', e)
        return 1


# remove any keys not included in the keys_allowed list
def _filter_user_data(data, keys_allowed):
    # remove key not in the keys_allowed list
    return {k: v for k, v in data.items() if k in keys_allowed}
