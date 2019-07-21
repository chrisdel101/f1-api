# endpoints
def home_endpoint():
    return "https://www.formula1.com"


def drivers_endpoint():
    return "{0}/en/drivers.html".format(home_endpoint())


def driver_endpoint(driver):
    return "https://www.formula1.com/en/drivers/{0}.html".format(driver)


def teams_endpoint():
    return "{0}/en/teams.html".format(home_endpoint())
