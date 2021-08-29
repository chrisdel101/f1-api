import os
import random
from models import driver_model, team_model
from slugify import slugify, Slugify
from utilities import utils
from utilities.scraper import team_scraper, driver_scraper
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def main():
    scrape_teams()
    scrape_drivers()


# - scrapes all drivers & inserts into DB
# - teams must be scraped first - driver depends on team model
def scrape_drivers(fail=False):
    new_driver_dict = None
    team_match_driver = None
    # -get all driver names
    all_drivers = driver_scraper.scrape_all_driver_names()
    # - get all driver standings
    standings = driver_scraper.scrape_all_drivers_standings()
    # - loop over names
    for driver in all_drivers:
        # slugify name
        driver_slug = slugify(driver).lower()
        # scrape more driver data
        new_driver_dict = driver_scraper.scrape_driver_stats(
            driver_slug)
        # add etxra data to obj
        new_driver_dict = driver_scraper.apply_scraper_func2_complete_driver(
            driver_slug, new_driver_dict)
        i = 0
        # match standing with current driver
        while standings:
            if driver_slug == standings[i].get('name_slug'):
                new_driver_dict['points'] = standings[i].get('points')
                new_driver_dict['standings_position'] = standings[i].get(
                    'standings_position')
                # remove item from list so not looped over again
                standings.pop(i)
                i = 0
                break
            i = i + 1
        # - make instance of driver
        d = driver_model.Driver.new(new_driver_dict)

        if os.environ['FLASK_ENV'] == 'dev_testing' or os.environ['FLASK_ENV'] == 'prod_testing':
                # fail flag can be set for testing
            if fail:
                # test for failure
                new_driver_dict['team_id'] = None
            else:
                # assign random value in tests
                new_driver_dict['team_id'] = random.randint(1, 100000)
        else:
            # match driver team_name_slug to actual team with contains - goal is team_id
            team_match_driver = team_model.Team.query.filter(
                team_model.Team.team_name_slug.contains(d.team_name_slug)).first()
            # get team id from team lookup
            team_id = team_match_driver.id
            # # add foreign key to driver
            new_driver_dict['team_id'] = team_id
            # reinstansiate driver instance with foriegn key
            d = driver_model.Driver.new(new_driver_dict)

            # add driver to team drivers_list
        compare = utils.compare_current_to_stored(d, driver_model.Driver)
        if compare and type(compare) != dict:
            if d.exists(driver_slug):
                d.delete(driver_slug)
            d.insert()
        else:
            print('++++++New instance is missing values++++')
            utils.log_None_values(compare)
        # return


def scrape_teams():
    # -get all driver names - returns dict w/ name and slug
    all_teams = team_scraper.scrape_all_team_names()
    # - loop over names
    for team in all_teams:
        team_name_slug = team['name_slug']
        # convert to url_slug - name with starting cap
        url_name_slug = utils.create_url_name_slug(team)
        # scrape each team
        new_dict = team_scraper.scrape_single_team_stats(url_name_slug)
        # add slug to dict
        new_dict['team_name_slug'] = team_name_slug
        # add url slug to dict
        new_dict['url_name_slug'] = url_name_slug
        # add shorter version of name
        new_dict['name'] = team['name']
        # add additional markuop and drivers to dict
        new_dict = team_scraper.add_imgs_markup(new_dict)
        # - insert on scrape into DB
        d = team_model.Team.new(new_dict)
    #    if team exists delete old instance
        if d.exists(team_name_slug):
            d.delete(team_name_slug)
        # add to model
        d.insert()
