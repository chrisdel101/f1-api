from models import driver_model
from utilities import utils
from slugify import slugify
import sqlalchemy
from database import db


# make data into arr of dicts
def make_slug_dict(arr):
    result_arr = []
    for item in arr:
        d = {
            'driver_name': str(item.driver_name),
            'name_slug': slugify(str(item.driver_name).lower())
        }
        result_arr.append(d)
    return result_arr


def show_all_drivers():
    try:
        arr = driver_model.Driver.query.all()
        return make_slug_dict(arr)
    except sqlalchemy.exc.OperationalError:
        return 'Operations error: possibily no table exists in DB'
    finally:
        db.session.close()


def make_driver_dto(name_slug):
    driver = driver_model.Driver.query.filter_by(
        name_slug=str(name_slug)).first()


def show_single_driver(name_slug):
    try:
        driver = driver_model.Driver.query.filter_by(
            name_slug=str(name_slug)).first()
        if driver != None:
            driver = vars(driver)
            return utils.serialize_row(driver)
        else:
            print('No Driver with that name')
            return None
    except Exception as e:
        print('error in driver_controller.show_single_driver', e)
    finally:
        db.session.close()
