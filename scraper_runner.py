from models import driver_model, team_model
from slugify import slugify, Slugify
from utilities import utils
from utilities.scraper import team_scraper, driver_scraper
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def main():
    scrape_teams()
    scrapte_drivers()


# - scrapes all drivers & inserts into DB
def scrape_drivers():
    # -get all driver names
    all_drivers = driver_scraper.scrape_all_driver_names()
    # - loop over names
    for driver in all_drivers:
        # slugify name
        driver_slug = slugify(driver).lower()
        # scrape each driver
        new_data = driver_scraper.get_complete_driver_data(driver_slug)
    # - insert on scrape into DB
        d = driver_model.Driver.new(new_data)
        if d.exists(driver_slug):
            d.delete(driver_slug)
        d.insert()


# scrape and add to DB
def scrape_teams():
    # -get all driver names - returns dict w/ name and slug
    all_teams = team_scraper.scrape_all_team_names()
    # - loop over names
    for team in all_teams:
        # convert to url_slug
        url_name_slug = utils.create_url_name_slug(team)
        # scrape each team
        new_dict = team_scraper.scrape_single_team_stats(url_name_slug)
        # add slug to model
        new_dict['name_slug'] = team['name_slug']
        # add url slug to model
        new_dict['url_name_slug'] = url_name_slug
        # add main_ing to current team obj
        new_dict = team_scraper.team_iterator(new_dict)
        print('ND', new_dict)
    # - insert on scrape into DB
        d = team_model.Team.new(new_dict)
        if d.exists(team['name_slug']):
            d.delete(team['name_slug'])
        d.insert()
