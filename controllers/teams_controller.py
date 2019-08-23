from models import team_model
from utilities import utils


# make obj with name and slug
def make_slug_dict(arr):
    results = []
    for item in arr:
        d = {
            'name': str(item),
            'name_slug': slugify(str(item).lower())
        }
        results.append(d)
    return result_arr


def show_all_teams():
    arr = team_model.Team.query.all()
    results = []
    for item in arr:
        item = vars(item)
        obj = {
            'name': item['full_team_name'],
            'name_slug': item['team_name_slug']
        }
        results.append(obj)
    return results


# takes either the team_name_slug or the team ID
def show_single_team(identifier):
    # check if it's ID
    if type(identifier) == int:
        try:
            team = vars(team_model.Team.query.filter_by(
                id=identifier).first())
            return utils.serialize_row(team)
        except Exception as e:
            print('Error', e)
    # or if it's name_slug
    else:
        try:
            team = vars(team_model.Team.query.filter_by(
                team_name_slug=identifier).first())
            return utils.serialize_row(team)
        except Exception as e:
            print('Error', e)
