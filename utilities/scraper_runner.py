from models import driver_model, team_model
from slugify import slugify, Slugify
from utilities import scraper, utils
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def main():
    scrape_teams()
    scrapte_drivers()


# - scrapes all drivers & inserts into DB
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


# scrape and add to DB
def scrape_teams():
    # -get all driver names
    all_teams = scraper.scrape_all_team_names()
    print('ALL', all_teams)
    # - loop over names
    for team in all_teams:
        print('TEAM', team['name_slug'])
        # remove all separators for count
        name = utils.custom_seperators(team['name'], "_")
     # shorten to match urls
        name = utils.teamShortener(name)
        # remove underscores - add dashes to match urls
        name = utils.custom_seperators(name, '_', '-')
     # remove whitespace - add dashes
        name = utils.custom_seperators(name, ' ', '-')
     # scrape each team
        new_data = scraper.scrape_single_team_stats(name)
        # add slug
        new_data['name_slug'] = team['name_slug']
    # - insert on scrape into DB
        d = team_model.Team.new(new_data)
        if d.exists(team['name_slug']):
            d.delete(team['name_slug'])
        d.insert()
