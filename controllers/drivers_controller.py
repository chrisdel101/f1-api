from models import driver_model
from utilities import utils

# retutns a list


def show_all_drivers():
    return driver_model.Driver.query.all()


def show_single_driver(name_slug):
    driver = driver_model.Driver.query.filter_by(
        name_slug=name_slug).first()
    driver = utils.serialize_row(driver)
    print('DDD', driver)
    return dict(driver)
