from models import user_model
from utilities import utils


def handle_user(user_id):
    # create new istance
    user = user_model.User.new(user_id)
    # check if exists
    print(user)
    exists = user.exists(user.id)
    if exists:
        print(user.update())
    else
    pass
    return 'post'
    # check if user is in DB
    # if not, add
    # if yes, update
