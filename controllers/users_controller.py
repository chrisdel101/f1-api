from models import user_model
from utilities import utils


def handle_user(data):
    try:
        # create new istance
        user = user_model.User.new(data['user_id'], data)
        # check if exists
        exists = user.exists(user.id)
        if exists:
            user.update(data)
        else:
            user.insert()
        return user
    except Exception as e:
        print('Error in handle_user', e)
        return 1
