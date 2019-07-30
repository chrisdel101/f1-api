from models import driver_model
from utilities import scraper
from slugify import slugify, Slugify
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
    print(all_teams)
    return
    # - loop over names
    for team in all_teams:
        # print(team)
        # scrape each team
        new_data = scraper.scrape_single_team_stats(
            team['name_slug'].capitalize())
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
