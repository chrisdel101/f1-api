from models import driver_model
from utilities import utils
from slugify import slugify


# make data into arr of dicts
def make_slug_dict(arr):
    result_arr = []
    for item in arr:
        d = {
            'name': str(item),
            'name_slug': slugify(str(item).lower())
        }
        result_arr.append(d)
    return result_arr


def show_all_drivers():
    obj = driver_model.Driver.query.all()
    return make_slug_dict(obj)


def show_single_driver(name_slug):
    driver = vars(driver_model.Driver.query.filter_by(
        name_slug=name_slug).first())
    # print('DRVIER', driver)
    return utils.serialize_row(driver)
