from models import team_model
from utilities import utils


def make_slug_dict(arr):
    result_arr = []
    for item in arr:
        d = {
            'name': str(item),
            'name_slug': slugify(str(item).lower())
        }
        result_arr.append(d)
    return result_arr


def show_all_teams():
    obj = team_model.Team.query.all()
    print('OBJ', obj)
    # return utils.make_slug_dict(obj)


def show_single_driver(name_slug):
    try:
        team = vars(team_model.Team.query.filter_by(
            name_slug=name_slug).first())
        print('dri', team)
        return utils.serialize_row(team)
    except Exception as e:
        print('Error', e)
