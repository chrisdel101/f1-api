from models import driver_model


# retutns a list
def show_all_drivers():
    return driver_model.Driver.query.all()


def show_single_driver(name_slug):
    print(driver_model.Driver.query.filter_by(name_slug=name_slug))
