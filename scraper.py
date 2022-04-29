import app
import os
import random
from models import driver_model, team_model
from slugify import slugify, Slugify
from utilities import utils
from utilities.scraper import team_scrape_logic, driver_scrape_logic
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


def main():
    team_scraper()
    driver_scraper()


# - scrapes all drivers & inserts into DB
# - teams must be scraped first - driver depends on team model
def driver_scraper(fail=False):
    try:
        with app.app.app_context():
            drivers_models = []
            new_driver_dict = None
            team_match_driver = None
            # -get all driver names
            all_drivers = driver_scrape_logic.scrape_all_driver_names()
            # - get all driver standings
            standings = driver_scrape_logic.scrape_all_drivers_standings()
            # - loop over names
            for driver in all_drivers:
                # slugify name
                driver_slug = slugify(driver).lower()
                # scrape more driver data
                new_driver_dict = driver_scrape_logic.scrape_driver_stats(
                    driver_slug)
                # add etxra data to obj
                new_driver_dict['main_image'] = driver_scrape_logic.get_main_image(
                    driver_slug).strip()
                new_driver_dict['driver_name'] = driver_scrape_logic.get_driver_name(
                    driver_slug).strip()
                new_driver_dict['driver_number'] = driver_scrape_logic.get_driver_number(
                    driver_slug).strip()
                new_driver_dict['flag_img_url'] = driver_scrape_logic.get_driver_flag(
                    driver_slug).strip()
                i = 0
                # match standing with current driver
                while i < len(standings):
                    if driver_slug == standings[i].get('name_slug'):
                        new_driver_dict['points'] = standings[i].get('points')
                        new_driver_dict['standings_position'] = standings[i].get(
                            'standings_position')
                        # remove item from list so not looped over again
                        standings.pop(i)
                        i = 0
                        break
                    i = i + 1
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
                    team_slug = _slugify(new_driver_dict['team'])
                    team_match_driver = team_model.Team.query.filter(
                        team_model.Team.team_name_slug.contains(team_slug)).first()
                    # get team id from team lookup
                    team_id = team_match_driver.id
                    # # add foreign key to driver
                    new_driver_dict['team_id'] = team_id
                    d = driver_model.Driver.new(new_driver_dict)
                    drivers_models.append(d)
        # after scrape add to DB
            if len(drivers_models):
                for model in drivers_models:
                    if model.exists(model.name_slug):
                        model.delete(model.name_slug)
                    model.insert()
    except Exception as e:
        print('Error inserting driver in scraper:', e)


def team_scraper():
    try:
        with app.app.app_context():
            stats_to_scrape = [
                'Full Team Name',
                'Base',
                'Team Chief',
                'Technical Chief',
                'Chassis',
                'Power Unit',
                'First Team Entry',
                'World Championships',
                'Highest Race Finish',
                'Pole Positions',
                'Fastest Laps',
            ]
            team_models = []
            # -get all team names - returns dict w/ name and slug
            all_teams_names = team_scrape_logic.scrape_all_team_names()
            # - loop over names
            for team in all_teams_names:
                team_name_slug = team['name_slug']
                # convert to team_name_header
                team_name_header = utils.create_team_header_from_slug(
                    team_name_slug)
                # scrape each team -return dict
                new_dict = team_scrape_logic.scrape_single_team_stats(
                    team_name_header, stats_to_scrape)
                new_dict['team_name_slug'] = team_name_slug
                new_dict['main_image'] = team_scrape_logic.get_main_image(
                    team_name_header)
                new_dict['main_logo_url'] = team_scrape_logic.get_main_logo_url(
                    team_name_header)
                new_dict['small_logo_url'] = team_scrape_logic.get_small_logo_url(
                    team['team_name'])
                new_dict['team_name_header'] = team_name_header
                new_dict['team_name'] = team['team_name']
                new_dict['drivers'] = team_scrape_logic.get_drivers(
                    team_name_header)
                t = team_model.Team.new(new_dict)
                team_models.append(t)

            # print('team_models', team_models)
            if len(team_models):
                for model in team_models:
                    if model.exists(model.team_name_slug):
                        model.delete(model.team_name_slug)
                    model.insert()
    except Exception as e:
        print('Error inserting team in scraper:', e)
