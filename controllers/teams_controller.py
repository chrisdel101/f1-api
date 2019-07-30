from models import team_model
from utilities import utils


def show_all_teams():
    print(team_model.Team.query.all())
    # obj = utils.serialize(team_model.Team.query.all())
    # print('OBJ', obj)
    # return utils.serialize_row(obj)


def show_single_driver(name_slug):
    driver = vars(driver_model.Driver.query.filter_by(
        name_slug=name_slug).first())
    return utils.serialize_row(driver)
