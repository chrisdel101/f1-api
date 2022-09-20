import logging
from database import db
import app
import os
import random
from models import driver_model, team_model
from slugify import Slugify
from utilities import utils
from utilities.scraper import team_scrape_logic, driver_scrape_logic
# underscore slug team
_slugify = Slugify(to_lower=True)
_slugify.separator = "_"
# hypen slug driver
slugify = Slugify()
slugify = Slugify(to_lower=True)
slugify.separator = '-'


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
            # - get all driver standings - contains driver slug
            standings = driver_scrape_logic.scrape_all_drivers_standings()
            # -get all driver names
            all_drivers = driver_scrape_logic.extract_all_drivers_names_from_standings(
                standings)
            # - loop over names
            for standing in standings:
                # extract slug from standings
                driver_slug = standing['name_slug']
                print('DDD', driver_slug)
                # scrape more driver data
                new_driver_dict = driver_scrape_logic.gather_driver_data(
                    driver_slug)
                if os.environ['FLASK_ENV'] == 'dev_testing' or os.environ['FLASK_ENV'] == 'prod_testing':
                    # fail flag can be set for testing
                    if fail:
                        # test for failure
                        new_driver_dict['team_id'] = None
                    else:
                        # assign random value in tests
                        new_driver_dict['team_id'] = random.randint(1, 100000)

                else:
                    new_driver_dict = driver_scrape_logic.gather_drivers_team_data(
                        _slugify(new_driver_dict['team']))
                    d = driver_model.Driver.new(new_driver_dict)
                    drivers_models.append(d)

        # after scrape add to DB
            if len(drivers_models):
                for model in drivers_models:
                    if model.exists(model.  name_slug):
                        model.delete(model.name_slug)
                    model.insert()
            return
    except Exception as e:
        logging.error('Error inserting driver in scraper: %s', e)
    finally:
        db.session.close()


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
                new_dict['images'] = team_scrape_logic.get_carousel_imgs_for_main_img(
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

            if len(team_models):
                for model in team_models:
                    if model.exists(model.team_name_slug):
                        model.delete(model.team_name_slug)
                    model.insert()
    except Exception as e:
        logging.error('Error inserting team in scraper: %s', e)
    finally:
        db.session.close()
