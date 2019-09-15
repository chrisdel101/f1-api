import app
import os
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
def scrape_drivers():
    # -get all driver names
    all_drivers = driver_scraper.scrape_all_driver_names()
    # print(all_drivers)
    # - get all driver standings
    standings = driver_scraper.scrape_all_drivers_standings()
    # - loop over names
    for driver in all_drivers:
        # slugify name
        driver_slug = slugify(driver).lower()
        # scrape more driver data
        new_driver_dict = driver_scraper.apply_scraper_func1_complete_driver(
            driver_slug)
        # add etxra data to obj
        new_driver_dict = driver_scraper.apply_scraper_func2_complete_driver(
            driver_slug, new_driver_dict)
        i = 0
        # match standing with current driver
        while standings:
            if driver_slug == standings[i].get('name_slug'):
                new_driver_dict['points'] = standings[i].get('points')
                new_driver_dict['position'] = standings[i].get('position')
                # remove item from list so not looped over again
                standings.pop(i)
                i = 0
                break
            i = i + 1
        # print('new dict', new_dict)
        # - make instance of driver
        d = driver_model.Driver.new(new_driver_dict)
        # match driver team_name_slug to actual team with contains
        team_match_driver = team_model.Team.query.filter(
            team_model.Team.team_name_slug.contains(d.team_name_slug)).first()

        # print('TTTTTTTTTTTTTT', team_model.Team.query.filter)
        # get matching team name slug - both driver and team need the same one
        team_name_slug = team_match_driver.team_name_slug
        # print('XXXXXXX', team_match_driver)
        # error check
        # assign random value in tests
        if os.environ['FLASK_ENV'] == 'testing':
            new_driver_dict['team_id'] = 101
        else:
            if team_match_driver:
                # get team id from team lookup
                team_id = team_match_driver.id
                # add foreign key to driver
                new_driver_dict['team_id'] = team_id
        # reinstansiate driver instance with foriegn key
        d = driver_model.Driver.new(new_driver_dict)
        # add driver to team drivers_list
        # print('XXX', d.team_id)
        # print('ID', team_match_driver.drivers_list)
        compare = utils.compare_current_to_stored(d, driver_model.Driver)
        if compare and type(compare) != dict:
            # print('+++++++', d.team_id)
            # print('+++++++', d.exists(driver_slug))

            if d.exists(driver_slug):
                d.delete(driver_slug)
            d.insert()
        else:
            print('New instance is missing values')
            utils.log_None_values(compare)
        # return


def scrape_teams():
    # -get all driver names - returns dict w/ name and slug
    all_teams = team_scraper.scrape_all_team_names()
    # print(all_teams)
    # - loop over names
    for team in all_teams:
        # comes with all drivers list
        team_name_slug = team['name_slug']
        # convert to url_slug
        url_name_slug = utils.create_url_name_slug(team)
        # scrape each team
        new_dict = team_scraper.scrape_single_team_stats(url_name_slug)
        # add slug to model
        new_dict['team_name_slug'] = team_name_slug
        # add url slug to model
        new_dict['url_name_slug'] = url_name_slug
        # add main_ing to current team obj- add drivers
        new_dict = team_scraper.iterate_teams_markup(new_dict)
        # print('DD', new_dict)
        # - insert on scrape into DB
        d = team_model.Team.new(new_dict)

        if d.exists(team_name_slug):
            d.delete(team_name_slug)
        d.insert()
        # if(new_dict['name_slug'] == 'ferrari'):
        # return
