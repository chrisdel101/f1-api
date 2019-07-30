from models import driver_model
from slugify import slugify, Slugify
from utilities import scraper, utils
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def main():
    # scrape_drivers()
    scrape_teams()


# - scrapes all drivers & inserts into DB
# returns unused dict
def scrape_drivers():
    # -get all driver names
    all_drivers = scraper.scrape_all_driver_names()
    # - loop over names
    for driver in all_drivers:
        # slugify name
        driver_slug = slugify(driver).lower()
        # scrape each driver
        new_data = scraper.scrape_single_driver_stats(driver_slug)
    # - insert on scrape into DB
        d = driver_model.Driver.new(new_data)
        if d.exists(driver_slug):
            d.delete(driver_slug)
        d.insert()

    return d


def scrape_teams():
    # -get all driver names
    all_teams = scraper.scrape_all_team_names()
    # print('ALL', all_teams)
    # - loop over names
    for team in all_teams:
        # remove all separators for count
        name = utils.custom_seperators(team['name'], "_")
        # shorten to match urls
        name = utils.teamShortener(name)
        # print(name)
        # print(name)
        # remove underscores - add dashes to match urls
        name = utils.custom_seperators(name, '_', '-')
        # # remove whitespace - add dashes
        name = utils.custom_seperators(name, ' ', '-')
        # # scrape each team
        # print(name)
        new_data = scraper.scrape_single_team_stats(
            name)
        print(new_data)
        # return
    # - insert on scrape into DB
        # d = driver_model.Driver.new(new_data)
        # if d.exists(driver_slug):
        #     d.delete(driver_slug)
        # d.insert()

    # return d


# if__name__ == "__main__"
# main()
