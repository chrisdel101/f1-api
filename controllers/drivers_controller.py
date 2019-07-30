from models import driver_model
from utilities import utils

# retutns a list


def show_all_drivers():
    obj = utils.serialize(driver_model.Driver.query.all())
    return utils.serialize_row(obj)


def show_single_driver(name_slug):
    driver = vars(driver_model.Driver.query.filter_by(
        name_slug=name_slug).first())
    return utils.serialize_row(driver)
