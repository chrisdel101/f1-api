from constants import TeamHeaderNames
import psycopg2
from dotenv import load_dotenv, find_dotenv
from database import db
from controllers import drivers_controller, teams_controller, users_controller
from models import driver_model, team_model, user_model
from utilities import utils
import scraper
from utilities.scraper import driver_scrape_logic, team_scrape_logic
from sqlalchemy import *
from flask import Flask
import json
import os
import unittest
from slugify import Slugify
slugify = Slugify(to_lower=True)
slugify.separator = '_'


# https://stackoverflow.com/a/50536837/5972531
def setup_testing_environment():
    load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))


def get_team_list(team_name, soup):
    list = soup.find_all('li')
    for li in list:
        print('li', li)
        s = li.find('section')
        if s:
            if s.find('a') and s.find('a')['href']:
                if team_name in s.find('a')['href']:
                    return li


def create_test_app():
    try:
        app = Flask(__name__)
        app.secret_key = b'12345678910-not-my-real-key'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if os.environ['FLASK_ENV'] == 'dev_testing':
            setup_testing_environment()
            app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        elif os.environ['FLASK_ENV'] == 'development':
            setup_testing_environment()
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
                'DEV_TESTING_DB')
        else:
            raise RuntimeError("Invalid FLASK_ENV")
        return app
    except Exception as e:
        print('Error in create_test_app', e)


def create_real_app():
    try:
        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if os.environ['FLASK_ENV'] == 'prod_testing':
            if os.environ['LOGS'] != 'off':
                print('Prod TEST', os.environ.get('PROD_DB'))
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROD_DB')
            DATABASE_URL = app.config['SQLALCHEMY_DATABASE_URI']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        elif os.environ['FLASK_ENV'] == 'development' or os.environ['FLASK_ENV'] == 'dev_testing':
            # import env
            setup_testing_environment()
            if os.environ['LOGS'] != 'off':
                print('DEV DB', os.environ.get('DEV_DB'))
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DEV_DB')
        return app
    except Exception as e:
        print('Error in create_real_app', e)


class TestDriverScapeLogic(unittest.TestCase):

    def test_change_driver_image_size_medium(self):
        res = driver_scrape_logic._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 1)
        self.assertTrue('640' in res)

    def test_change_driver_image_size_small(self):
        res = driver_scrape_logic._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 0)
        self.assertTrue('320' in res)

    def test_scrape_all_driver_names(self):
        result = driver_scrape_logic.scrape_all_driver_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    def test_scrape_all_driver_standings(self):
        result = driver_scrape_logic.scrape_all_drivers_standings()
        print('res', result)
        self.assertTrue(type(result) is list)
        self.assertTrue(len(result) > 0)
        res1 = result[0]
        self.assertTrue('points' in res1)
        self.assertTrue('standings_position' in res1)
        self.assertEqual(res1['standings_position'], '1')
        res2 = result[1]
        self.assertTrue('points' in res2)
        self.assertTrue('standings_position' in res2)
        self.assertEqual(res2['standings_position'], '2')

    def test_get_main_image_url(self):
        # check for subStr
        self.assertTrue('formula1.com//content/fom-website/en/drivers/sergio-perez' in
                        driver_scrape_logic.get_main_image("sergio-perez"))
        self.assertRaises(TypeError, driver_scrape_logic.get_main_image, 4)

    def test_get_driver_name(self):
        self.assertEqual(driver_scrape_logic.get_driver_name(
            "alexander-albon"), "Alexander Albon")
        self.assertEqual(driver_scrape_logic.get_driver_name(
            "lewis-hamilton"), "Lewis Hamilton")
        self.assertRaises(TypeError, driver_scrape_logic.get_driver_name, 44)

    def test_get_driver_number(self):
        self.assertEqual(driver_scrape_logic.get_driver_number(
            "valtteri-bottas"), "77")
        self.assertEqual(driver_scrape_logic.get_driver_number(
            "lewis-hamilton"), "44")
        self.assertRaises(
            TypeError, driver_scrape_logic.get_driver_number, True)

    def test_get_driver_flag_url(self):
        self.assertTrue(('content/fom-website/en/drivers/lance-stroll' and 'countryFlag') in driver_scrape_logic.get_driver_flag(
            "lance-stroll"))
        self.assertTrue(('content/fom-website/en/drivers/george-russell' and 'countryFlag') in driver_scrape_logic.get_driver_flag(
            "george-russell"))
        self.assertRaises(TypeError, driver_scrape_logic.get_driver_number, 33)

    def scrape_drivrer_details(self):
        result1 = driver_scrape_logic.scrape_drivrer_details("alexander-albon")
        self.assertEqual(result1[1]['country'], 'Thailand')
        self.assertEqual(result1[1]['date_of_birth'], '23/03/1996')
        self.assertEqual(result1[1]['place_of_birth'], 'London, England')

    def test_check_any_new_driver_attrs(self):
        result1 = driver_scrape_logic.scrape_drivrer_details("alexander-albon")
        try:
            self.assertTrue(len(result1[0]) == 0)
        except Exception as e:
            raise ValueError(
                "Unknown driver attributes added to driver markup.")

    def test_scrape_driver_stats(self):
        result1 = driver_scrape_logic.scrape_driver_stats(
            'sebastian-vettel'
        )
        self.assertTrue(type(result1) == dict)
        self.assertEqual(result1['country'], 'Germany')
        # test all manual additions
        result2 = driver_scrape_logic.scrape_driver_stats(
            'lewis-hamilton'
        )
        self.assertEqual(result2['country'], 'United Kingdom')
        self.assertEqual(result2['date_of_birth'], '07/01/1985')


class TestTeamScrapLogic(unittest.TestCase):

    def test_change_team_image_size_medium(self):
        res = team_scrape_logic._change_team_img_size(
            "/content/fom-website/en/teams/Mercedes/_jcr_content/image16x9.img.1536.medium.jpg/1561122939027.jpg", 1)
        self.assertTrue('640' in res)

    def test_change_team_image_size_large(self):
        res = team_scrape_logic._change_team_img_size(
            "/content/fom-website/en/teams/Mercedes/_jcr_content/image16x9.img.1536.medium.jpg/1561122939027.jpg", 2)
        self.assertTrue('768' in res)

    def test_scrape_all_team_names(self):
        result = team_scrape_logic.scrape_all_team_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    def test_scrape_single_team_stats(self):
        stats_to_scrape_run1 = [
            'Full Team Name',
            'Base',
        ]
        team_name_header1 = TeamHeaderNames.red_bull_racing.value
        RESULT1 = team_scrape_logic.scrape_single_team_stats(
            team_name_header1, stats_to_scrape_run1)
        self.assertTrue(type(RESULT1) is dict)
        self.assertTrue(slugify
                        (stats_to_scrape_run1[0]) in RESULT1)
        self.assertTrue(slugify(stats_to_scrape_run1[1]) in RESULT1)
        self.assertTrue(utils.word_seperator_manager(
            team_name_header1, '-') in RESULT1.get('full_team_name'))

        stats_to_scrape_run2 = [
            'Full Team Name',
            'First Team Entry',
            'World Championships',
            'Highest Race Finish',
        ]
        team_name_header2 = TeamHeaderNames.mclaren.value
        RESULT2 = team_scrape_logic.scrape_single_team_stats(
            team_name_header2, stats_to_scrape_run2)
        self.assertTrue(slugify
                        (stats_to_scrape_run2[0]) in RESULT2)
        self.assertTrue(slugify(stats_to_scrape_run2[1]) in RESULT2)
        self.assertTrue(slugify(stats_to_scrape_run2[2]) in RESULT2)
        self.assertTrue(utils.word_seperator_manager(
            team_name_header2, '-') in RESULT2.get('full_team_name'))

    def test_get_small_logo_url(self):
        result = team_scrape_logic.get_small_logo_url('Ferrari')
        self.assertTrue('ferrari-logo' in result)
        result = team_scrape_logic.get_small_logo_url('Red Bull Racing')
        self.assertTrue('red-bull-racing-logo' in result)

    def test_main_logo_url(self):
        result1 = team_scrape_logic.get_main_logo_url('Red-Bull')
        self.assertTrue('Red-Bull-Racing' and 'logo' in result1)
        result2 = team_scrape_logic.get_main_logo_url('Aston-Martin')
        self.assertTrue('Aston-Martin' in result2)

    def test_get_main_image(self):
        team_name_header1 = "Red-Bull"
        team_name_header2 = "Aston-Martin"
        result1 = team_scrape_logic.get_main_image(team_name_header1)
        self.assertTrue('gallery' in result1)
        self.assertTrue('jpg' in result1)
        self.assertTrue('Red-Bull-Racing' in result1)
        result2 = team_scrape_logic.get_main_image(team_name_header2)
        self.assertTrue('gallery' in result2)
        self.assertTrue('jpg' in result2)
        self.assertTrue('Aston-Martin' in result2)

    def test_get_drivers(self):
        team_name_header1 = "Red-Bull"
        team_name_header2 = "Aston-Martin"
        team_name_header3 = "Haas-F1-Team"
        result1 = team_scrape_logic.get_drivers(team_name_header1)
        result2 = team_scrape_logic.get_drivers(team_name_header2)
        result3 = team_scrape_logic.get_drivers(team_name_header3)
        self.assertTrue(next(
            (driver for driver in result1 if driver["name_slug"] == " max-verstappen"), True))
        self.assertTrue(next(
            (driver for driver in result2 if driver["name_slug"] == " sebastian-vettel"), True))
        self.assertTrue(next(
            (driver for driver in result3 if driver["name_slug"] == " mick-schumacher"), True))


class TestUtils(unittest.TestCase):

    def test_create_team_header_from_slug(self):
        name_slug1 = 'haas_f1_team'
        name_slug2 = 'alfa_romeo_racing'
        name_slug3 = 'red_bull_racing'
        name_slug4 = 'mclaren'
        result1 = utils.create_team_header_from_slug(name_slug1)
        result2 = utils.create_team_header_from_slug(name_slug2)
        result3 = utils.create_team_header_from_slug(name_slug3)
        result4 = utils.create_team_header_from_slug(name_slug4)
        self.assertEqual(result1, 'Haas')
        self.assertEqual(result2, 'Alfa-Romeo')
        self.assertEqual(result4, 'McLaren')

    def test_create_team_header_from_team_name(self):
        team_name1 = 'Red Bull Racing'
        team_name2 = 'McLaren'
        RESULT1 = utils.create_team_header_from_team_name(team_name1)
        RESULT2 = utils.create_team_header_from_team_name(team_name2)
        self.assertEqual(RESULT1, TeamHeaderNames.red_bull_racing.value)
        self.assertEqual(RESULT2, TeamHeaderNames.mclaren.value)

    def test_create_driver_list(self):
        drivers = ['Nico  Hulkenberg', 'Daniel Ricciardo']
        expected = [{'driver_name': 'Nico  Hulkenberg', 'name_slug': 'nico-hulkenberg'},
                    {'driver_name': 'Daniel Ricciardo', 'name_slug': 'daniel-ricciardo'}]
        driver_list = utils.create_driver_list(drivers)
        self.assertEqual(driver_list, expected)

    def test_hash_password(self):
        password = 'password123'
        hashed = utils.hash_password(password)
    #    check that hashed is not equal to text
        self.assertNotEqual(password, hashed)

    def test_check_hashed_password(self):
        password = 'password123'
        hashed = utils.hash_password(password)
    #    check that hashed is not equal to text
        matched = utils.check_hashed_password(password, hashed)
        self.assertTrue(matched)


class TestScraper(unittest.TestCase):
    #    https://stackoverflow.com/questions/16051422/patch-patching-the-class-introduces-an-extra-parameter
    # https://stackoverflow.com/questions/42482021/how-to-mock-modelclass-query-filter-by-in-flask-sqlalchemy
    # @patch('models.team_model.Team', return_value="test_slug")
    # @patch('flask_sqlalchemy._QueryProperty.__get__')
    def test_driver_scraper(self, *args):
        # create app instance
        app = create_test_app()
        # add to context
        with app.app_context():
            # init db
            db.init_app(app)
            scraper.driver_scraper()
            drivers = driver_model.Driver.query.all()
            self.assertTrue(type(drivers) == list)
            self.assertTrue(len(drivers) == 20)

            hamilton = driver_model.Driver.query.filter_by(
                name_slug='lewis-hamilton').first()
            albon = driver_model.Driver.query.filter_by(
                name_slug='alexander-albon').first()
            self.assertEqual(hamilton.name_slug, 'lewis-hamilton')
            self.assertEqual(hamilton.place_of_birth, 'Stevenage, England')
            self.assertEqual(hamilton.country, 'United Kingdom')

            self.assertEqual(albon.name_slug, 'alexander-albon')
            self.assertEqual(albon.place_of_birth, 'London, England')
            self.assertEqual(albon.date_of_birth, '23/03/1996')

            db.session.remove()
            db.drop_all()

    def test_team_scraper(self):

        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            scraper.team_scraper()
            ferrari = team_model.Team.query.filter_by(
                team_name_slug='ferrari').first()
            haas = team_model.Team.query.filter_by(
                team_name_slug='haas_f1_team').first()
            mclaren = team_model.Team.query.filter_by(
                team_name_slug='mclaren').first()

            self.assertListEqual(ferrari.drivers_scraped, [
                {'driver_name': 'Charles Leclerc', 'name_slug': 'charles-leclerc'},
                {'driver_name': 'Carlos Sainz', 'name_slug': 'carlos-sainz'}
            ])
            self.assertTrue('Scuderia Ferrari' in ferrari.full_team_name,
                            )
            self.assertEqual(ferrari.base, 'Maranello, Italy')
            self.assertEqual(ferrari.power_unit, 'Ferrari')

            self.assertTrue('ferrari-logo' in ferrari.small_logo_url)

            self.assertTrue('haas-f1-team-logo' in haas.small_logo_url)
            self.assertTrue('Haas F1 Team' in haas.full_team_name)
            self.assertEqual(haas.base, 'Kannapolis, United States')
            self.assertEqual(haas.power_unit, 'Ferrari')
            self.assertListEqual(haas.drivers_scraped, [
                {'driver_name': 'Mick Schumacher', 'name_slug': 'mick-schumacher'}, {
                    'driver_name': 'Kevin Magnussen', 'name_slug': 'kevin-magnussen'}
            ])

            self.assertTrue('McLaren' in mclaren.full_team_name)
            self.assertEqual('McLaren', mclaren.team_name_header)
            self.assertEqual(mclaren.base, 'Woking, United Kingdom')
            self.assertTrue('mclaren-logo' in mclaren.small_logo_url)

            db.session.remove()
            db.drop_all()

    # make sure runners work together

    def test_all_runners(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            scraper.team_scraper()
            ferrari = team_model.Team.query.filter_by(
                team_name_slug='ferrari').first()
            haas = team_model.Team.query.filter_by(
                team_name_slug='haas_f1_team').first()
            mclaren = team_model.Team.query.filter_by(
                team_name_slug='mclaren').first()
            scraper.driver_scraper()
            drivers = driver_model.Driver.query.all()
            # print('Dr', drivers)
            self.assertTrue(type(drivers) == list)
            self.assertTrue(len(drivers) == 20)

            hamilton = driver_model.Driver.query.filter_by(
                name_slug='lewis-hamilton').first()
            albon = driver_model.Driver.query.filter_by(
                name_slug='alexander-albon').first()
            self.assertEqual(hamilton.name_slug, 'lewis-hamilton')
            self.assertEqual(hamilton.place_of_birth, 'Stevenage, England')
            self.assertEqual(hamilton.country, 'United Kingdom')

            self.assertEqual(albon.name_slug, 'alexander-albon')
            self.assertEqual(albon.place_of_birth, 'London, England')
            self.assertEqual(albon.date_of_birth, '23/03/1996')

            self.assertEqual(ferrari.base, 'Maranello, Italy')
            self.assertEqual(ferrari.power_unit, 'Ferrari')
            self.assertTrue('ferrari-logo' in ferrari.small_logo_url)
            self.assertEqual(haas.power_unit, 'Ferrari')

            self.assertTrue('Haas F1 Team' in haas.full_team_name)
            self.assertEqual(haas.base, 'Kannapolis, United States')
            self.assertTrue('haas-f1-team-logo' in haas.small_logo_url)

            self.assertTrue('McLaren' in mclaren.full_team_name)
            self.assertEqual('McLaren', mclaren.team_name_header)
            self.assertEqual(mclaren.base, 'Woking, United Kingdom')
            self.assertTrue('mclaren-logo' in mclaren.small_logo_url)

            db.session.remove()
            db.drop_all()

    @unittest.skip  # need to rewrite - no nullable false to fail now
    # run witn fail flag set to true - test for correct DB action
    def test_driver_runner_failure(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            scraper.driver_scraper(True)
            drivers = driver_model.Driver.query.all()
            self.assertTrue(len(drivers) == 0)

            db.session.remove()
            db.drop_all()


class TestDriverModel(unittest.TestCase):
    # utiliy functions to use in below tests
    def create_new_driver_pass(self):
        driver = driver_model.Driver.new(
            {
                "driver_name": "Test Driver",
                "name_slug": "test-driver",
                "country": "test country",
                "base": "test base",
                "team": "Test Team Racing",
                "team_name_slug": "test_team_racing",
                "team_id": 1
            }
        )
        return driver

    def create_new_driver_fail(self):
        driver = driver_model.Driver.new(
            {
                "driver_name": "Test Driver",
                "name_slug": "test-driver",
                "country": "test country",
                "base": "test base",
                "team": "Test Team Racing",
                "team_name_slug": "test_team_racing"
            }
        )
        return driver

    def test_driver_new(self):
        # create app instance
        app = create_test_app()
        # add to context
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance
            driver = self.create_new_driver_pass()
            self.assertEqual(driver.driver_name, 'Test Driver')
            self.assertEqual(driver.name_slug, 'test-driver')
            self.assertEqual(driver.team_name_slug, 'test_team_racing')
            # drop db
            db.session.remove()
            db.drop_all()

     # should pass with all constraints
    def test_driver_insert_pass(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            driver_pass = self.create_new_driver_pass()
            self.assertEqual(driver_pass.driver_name, 'Test Driver')
            driver_pass.insert()
            assert driver_pass in db.session
            db.session.remove()
            db.drop_all()

    @unittest.skip  # rewrite needed
    def test_driver_insert_fail(self):
        # should fail missing contstraint
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            driver_fail = self.create_new_driver_fail()
            driver_fail.insert()
            assert driver_fail not in db.session
            self.assertRaises(AssertionError, driver_fail.insert())
            db.session.remove()
            db.drop_all()

    def test_driver_does_not_exist(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            driver = self.create_new_driver_pass()
            self.assertEqual(driver.driver_name, 'Test Driver')
            exists = driver.exists(driver.name_slug)
            self.assertFalse(exists)
            db.session.remove()
            db.drop_all()

    def test_driver_does_exists(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            driver = self.create_new_driver_pass()
            self.assertEqual(driver.driver_name, 'Test Driver')
            driver.insert()
            exists = driver.exists(driver.name_slug)
            self.assertTrue(exists)
            db.session.remove()
            db.drop_all()

    def test_driver_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            driver = self.create_new_driver_pass()
            self.assertEqual(driver.driver_name, 'Test Driver')
            driver.insert()
            driver.delete(driver.name_slug)
            assert driver not in db.session
            db.session.remove()
            db.drop_all()

    def test_driver_not_exists_after_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            driver = self.create_new_driver_pass()
            self.assertEqual(driver.driver_name, 'Test Driver')
            driver.insert()
            driver.delete(driver.name_slug)
            exists = driver.exists(driver.name_slug)
            self.assertFalse(exists)
            db.session.remove()
            db.drop_all()


class TestTeamModel(unittest.TestCase):
    def create_new_team_pass(self):
        team = team_model.Team.new(
            {
                "full_team_name": "Test Team",
                "team_name_slug": "test_team"
            }
        )
        return team

    def create_new_team_fail(self):
        team = team_model.Team.new(
            {
                "full_team_name": "Test Team",
            }
        )
        return team

    def test_team_new(self):
        # create app instance
        app = create_test_app()
        # add to context
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance
            team = self.create_new_team_pass()
            self.assertEqual(team.full_team_name, 'Test Team')
            self.assertEqual(team.team_name_slug, 'test_team')
            # drop db
            db.session.remove()
            db.drop_all()

    def test_team_insert_pass(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            team = self.create_new_team_pass()
            self.assertEqual(team.full_team_name, 'Test Team')
            team.insert()
            assert team in db.session
            db.session.remove()
            db.drop_all()

    @unittest.expectedFailure
    def test_team_insert_fail(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            team = self.create_new_team_fail()
            self.assertRaises(AssertionError, team.insert())
            assert team not in db.session
            db.session.remove()
            db.drop_all()

    def test_team_does_not_exists(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            team = self.create_new_team_pass()
            self.assertEqual(team.full_team_name, 'Test Team')
            exists = team.exists(team.team_name_slug)
            self.assertFalse(exists)
            db.session.remove()
            db.drop_all()

    def test_team_does_exist(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            team = self.create_new_team_pass()
            self.assertEqual(team.full_team_name, 'Test Team')
            team.insert()
            exists = team.exists(team.team_name_slug)
            self.assertTrue(exists)
            db.session.remove()
            db.drop_all()

    def test_team_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            team = self.create_new_team_pass()
            self.assertEqual(team.full_team_name, 'Test Team')
            team.insert()
            team.delete(team.team_name_slug)
            assert team not in db.session
            db.session.remove()
            db.drop_all()

    def test_team_not_exists_after_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            team = self.create_new_team_pass()
            self.assertEqual(team.full_team_name, 'Test Team')
            team.insert()
            team.delete(team.team_name_slug)
            exists = team.exists(team.team_name_slug)
            self.assertFalse(exists)
            db.session.remove()
            db.drop_all()

    def test_team_driver_id_match(self):
        app = create_test_app()
        # add to context
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance
            team = self.create_new_team_pass()
            team.insert()
            # team = vars(team)
            # add driver
            t = team_model.Team.query.all()
            t_id = t[0].id
            driver = driver_model.Driver.new({
                'driver_name': 'Lewis Hamilton',
                'country': 'United Kingdom',
                'driver_number': '11',
                'team': 'Mercedes',
                'team_id': t_id
            })
            driver.insert()

            db.session.remove()
            db.drop_all()
            # print(team)
            # print(team)


class TestTeamController(unittest.TestCase):
    def test_show_single_team_w_id(self):
        app = create_real_app()
        with app.app_context():
            db.init_app(app)
            # look up first team
            team_one_id = vars(team_model.Team.query.all()[0])['id']
            team_one_slug = vars(team_model.Team.query.all()[0])[
                'team_name_slug']
            # use id to run test
            team = teams_controller.show_single_team(str(team_one_id))
            self.assertEqual(team['team_name_slug'], team_one_slug)
            self.assertEqual(team['id'], team_one_id)

    def test_show_single_team_w_slug(self):
        app = create_real_app()
        with app.app_context():
            db.init_app(app)
            team_four_id = vars(team_model.Team.query.all()[3])['id']
            team_four_slug = vars(team_model.Team.query.all()[0])[
                'team_name_slug']
            team = teams_controller.show_single_team(team_four_slug)
            self.assertEqual(team['team_name_slug'], team_four_slug)

    def test_show_all_teams(self):
        app = create_real_app()
        with app.app_context():
            db.init_app(app)
            team = teams_controller.show_all_teams()
            self.assertTrue(type(team), list)
            self.assertTrue(len(team) > 0)


class TestDriverController(unittest.TestCase):
    def test_show_all_drivers(self):
        app = create_real_app()
        with app.app_context():
            db.init_app(app)
            drivers = drivers_controller.show_all_drivers()
            self.assertTrue(type(drivers), list)
            self.assertTrue(len(drivers) > 0)
            self.assertTrue(len(drivers) == 20)

    def test_show_single_driver_true(self):
        app = create_real_app()
        with app.app_context():
            db.init_app(app)
            driver = drivers_controller.show_single_driver('lewis-hamilton')
            self.assertTrue(type(driver is dict))
            self.assertTrue('place_of_birth' in driver)
            self.assertTrue(driver['place_of_birth'], 'Stevenage, England')

    # test if DB is empty
    def test_show_single_driver_false(self):
        app = create_real_app()
        with app.app_context():
            db.init_app(app)
            driver = drivers_controller.show_single_driver('some-random-name')
            self.assertEqual(driver, None)


@unittest.skip
class TestUserModel(unittest.TestCase):
    # --------- UTILS FUNCS
    ID = 1111111111
    DATA = {
        "username": "username1",
        "password": "password1"
    }

    def create_new_user_pass(self):
        user = user_model.User.new(self.ID, self.DATA)
        return user

    def create_new_user_fail(self, type_of_failure):
        if type_of_failure == 'username':
            return user_model.User  .new(self.ID, {
                'password': 'password123'
            })
        elif type_of_failure == 'password':
            return user_model.User.new(self.ID, {
                'username': 'username123',
            })
        else:
            # default
            print('USER', user_model.User.new(None, {
                'username': 'username1',
                'password': 'password123'
            }))
            return user_model.User.new(None, {
                'username': 'username1',
                'password': 'password123'
            })
    # ------------ TESTS
    # test user.new() - success

    def test_encode_auth_token(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            db.session.add(user)
            db.session.commit()
            auth_token = user.encode_auth_token(user.id)
            # print(auth_token, 'AUTH')
            self.assertTrue(isinstance(auth_token, bytes))
            db.session.remove()
            db.drop_all()

    def test_decode_auth_token(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            db.session.add(user)
            db.session.commit()
            auth_token = user.encode_auth_token(user.id)
            print('ENCODE', auth_token)
            self.assertTrue(isinstance(auth_token, bytes))
            # should decode to user ID
            self.assertTrue(user_model.User.decode_auth_token(
                auth_token) == self.ID)
            decode = user_model.User.decode_auth_token(auth_token)
            print('DECODE', decode)
            db.session.remove()
            db.drop_all()

    def test_user_new_pass(self):
        app = create_test_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance
            user = self.create_new_user_pass()
            self.assertEqual(user.id, self.ID)
            self.assertEqual(user.username, self.DATA["username"])
            # drop db
            db.session.remove()
            db.drop_all()

    # test user.new() - failures
    def test_user_new_fail_no_id(self):
        app = create_test_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance w/o ID
            self.assertRaises(ValueError, self.create_new_user_fail, 'id')
            db.session.remove()
            db.drop_all()

    def test_user_new_fail_no_username(self):
        app = create_test_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance w/o username
            self.assertRaises(
                ValueError, self.create_new_user_fail, 'username')
            db.session.remove()
            db.drop_all()

    def test_user_new_fail_no_password(self):
        app = create_test_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance w/o password
            self.assertRaises(
                ValueError, self.create_new_user_fail, 'password')
            db.session.remove()
            db.drop_all()
    # test user.insert()

    def test_user_insert_pass(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            user.insert()
            assert user in db.session
            db.session.remove()
            db.drop_all()

    # write a test model that creates user without id to test
    @unittest.skip
    def test_user_insert_fail(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            assert user not in db.session
            # raises assertion will not work
            db.session.remove()
            db.drop_all()
    # test user.exists() with id param

    def test_user_does_exist_by_id(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            # check user.new works
            self.assertEqual(user.id, self.ID)
            self.assertEqual(user.username, self.DATA["username"])
            # # insert new user
            user.insert()
            # # now check to ensure exists func works - id should match
            exists = user.exists(user.id)
            self.assertTrue(exists)
            db.session.remove()
            db.drop_all()

    # test user.exists() with username param
    def test_user_does_exist_by_username(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            # check user.new works
            self.assertEqual(user.id, self.ID)
            self.assertEqual(user.username, self.DATA["username"])
            # # insert new user
            user.insert()
            # # now check to ensure exists func works - id should match
            exists = user.exists(user.username, 'username')
            self.assertTrue(exists)
            db.session.remove()
            db.drop_all()

    # test user_on_class.exists() with id param
    def test_user_exist_on_class_by_id(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            # check user.new works
            self.assertEqual(user.id, self.ID)
            self.assertEqual(user.username, self.DATA["username"])
            # # insert new user
            user.insert()
            # # now check to ensure exists func works - id should match
            exists = user_model.User.exists_on_class(user.id)
            self.assertTrue(exists)
            db.session.remove()
            db.drop_all()

    # test user_on_class.exists() fails
    def test_user_exist_on_class_fails_user_not_exist(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # check is a user exists - no instance
            exists = user_model.User.exists_on_class(self.ID)
            self.assertFalse(exists)
            db.session.remove()
            db.drop_all()

    # fails on unique constraint
    def test_users_insert_fail_same_id(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # create and insert new user1
            user1 = self.create_new_user_pass()
            user1.insert()
            # check exists okay
            exists1 = user1.exists(user1.id)
            self.assertTrue(exists1)
            # create second user
            user2 = self.create_new_user_pass()
            # cause error b/c of identical id to user1
            self.assertRaises(Exception,
                              user2.insert)
            # check user 2 is not in db
            exists2 = user2.exists(user2.id)
            self.assertFalse(exists2)
            db.session.remove()
            db.drop_all()
    # fails on unique constraint

    def test_users_insert_fail_same_username(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # create and insert new user1
            user1 = user_model.User.new(1, self.DATA)
            user1.insert()
            # check exists okay
            exists1 = user1.exists(user1.id)
            self.assertTrue(exists1)
            # create second user - same username
            user2 = user_model.User.new(2, self.DATA)
            self.assertRaises(Exception,
                              user2.insert)
            # check user 2 is not in db
            exists2 = user2.exists(user2.id)
            self.assertFalse(exists2)
            db.session.remove()
            db.drop_all()
    # test user.delete()

    def test_single_user_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            user.insert()
            # confirm added to DB
            assert user in db.session
            self.assertEqual(user.id, self.ID)
            user.delete(user.id)
            # confirm deleted from DB
            assert user not in db.session
            db.session.remove()
            db.drop_all()

    # test user.delete()
    def test_mutiple_users_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # create 3 test users
            user1 = user_model.User.new(1, {
                'username': 'username1',
                'password': 'password123'
            })
            user2 = user_model.User.new(2, {
                'username': 'username2',
                'password': 'password123'
            })
            user3 = user_model.User.new(3, {
                'username': 'username3',
                'password': 'password123'
            })
            # insert all users
            user1.insert()
            user2.insert()
            user3.insert()
            # confirm all added to DB
            assert user1 in db.session
            assert user2 in db.session
            assert user3 in db.session
            # delete all users
            user1.delete(user1.id)
            user2.delete(user2.id)
            user3.delete(user3.id)
            # confirm all deleted from DB
            assert user1 not in db.session
            assert user2 not in db.session
            assert user3 not in db.session
            db.session.remove()
            db.drop_all()
    # test user.exists()

    def test_user_does_not_exists_after_delete(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            user.insert()
            # check exists
            self.assertTrue(user.exists(user.id))
            user.delete(user.id)
            # check not exists
            self.assertFalse(user.exists(user.id))
            db.session.remove()
            db.drop_all()

    def test_user_update_single_item(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            user.insert()
            # check exists
            self.assertTrue(user.exists(user.id))
            # check user is indentical to original - driver and team and None
            self.assertEqual(user.id, self.ID)
            self.assertEqual(user.username, self.DATA['username'])
            self.assertEqual(user.driver_data, self.DATA.get('driver_data'))
            self.assertEqual(user.team_data, self.DATA.get('team_data'))
            # add driver and team data
            new_data = {
                "driver_data": ['driver1', 'driver5', 'driver6', 'driver7'],
                "team_data": ['team1', 'team5', 'team6', 'team7']
            }
            user.update(new_data)
            # check that user data updated
            self.assertTrue(user.driver_data == new_data['driver_data'])
            self.assertTrue(user.team_data == new_data['team_data'])
            # check other data is still same and not altered
            self.assertEqual(user.id, self.ID)
            self.assertEqual(user.username, self.DATA['username'])
            db.session.remove()
            db.drop_all()


@unittest.skip
class TestUserController(unittest.TestCase):
    # DATA = {
    #     "driver_data": ["driver1", "driver2"],
    #     "team_data": ["team1", "team2"],
    #     "user_id": 2
    # }
    ID = 1111111111
    DATA = {
        "username": "username1",
        "password": "password1"
    }
    COMBINE_DATA = DATA
    COMBINE_DATA['id'] = ID
    # test combination of user new/insert

    def test_register_success(self):
        app = create_test_app()
        # with app.app_context():
        with app.test_request_context('/register', method='POST'):
            db.init_app(app)
            # register new user
            res = users_controller.register({
                'id': self.ID,
                'username': self.DATA['username'],
                'password': self.DATA['password']
            })
            # check correct status code
            self.assertEqual(res.status_code, 201)
            db.session.remove()
            db.drop_all()

    # test error raised when no id
    def test_register_fail_no_id(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # raise error when ID is none
            self.assertRaises(ValueError, users_controller.register, {
                'id': None,
                'username': self.DATA['username'],
                'password': self.DATA['password']
            })
            db.session.remove()
            db.drop_all()

    def test_register_fail_no_username(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # raise error when username is none
            self.assertRaises(ValueError, users_controller.register, {
                'id': self.ID,
                'username': None,
                'password': self.DATA['password']
            })
            db.session.remove()
            db.drop_all()

    def test_register_fail_already_exists(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # raise error when username is none
            reg_res = users_controller.register({
                'id': self.ID,
                'username': self.DATA['username'],
                'password': self.DATA['password']
            })
            # check correct status code on first entry
            self.assertEqual(reg_res.status_code, 201)
            res2 = users_controller.register({
                'id': self.ID,
                'username': self.DATA['username'],
                'password': self.DATA['password']
            })
            print('res2', res2)
            db.session.remove()
            db.drop_all()

    def test_user_status_after_registration(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            reg_res = users_controller.register({
                'id': self.ID,
                'username': self.DATA['username'],
                'password': self.DATA['password']
            })
            # check registered ok
            self.assertEqual(reg_res.status_code, 201)
            status_res = users_controller.status(reg_res)
            self.assertEqual(status_res.status_code, 200)
            self.assertEqual(json.loads(status_res.data)['status'], 'success')
            db.session.remove()
            db.drop_all()

    def test_user_status_after_login(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # print(flask.request.path)
            reg_res = users_controller.register({
                'id': self.ID,
                'username': self.DATA['username'],
                'password': self.DATA['password']
            })
            # check registerd ok
            self.assertEqual(reg_res.status_code, 201)
            login_res = users_controller.login(self.COMBINE_DATA)
            # check login okay
            self.assertEqual(login_res.status_code, 200)
            status_res = users_controller.status(login_res)
            # check status okay
            self.assertEqual(status_res.status_code, 200)
            self.assertEqual(json.loads(status_res.data)['status'], 'success')

    def test_login_fail_unregistered_user(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            logged_in = users_controller.login(self.COMBINE_DATA)
            self.assertFalse(logged_in)
            db.session.remove()
            db.drop_all()

    def test_login_fail_incorrect_username(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # register test user
            reg_res = users_controller.register(self.COMBINE_DATA)
            # check registerd ok
            self.assertEqual(reg_res.status_code, 201)
            # attemp login wrong username
            login_res = users_controller.login({
                'id': 1111111,
                'username': 'username2',
                'password': 'some-password'
            })
            # check login fails
            self.assertFalse(login_res)
            db.session.remove()
            db.drop_all()

    def test_login_fail_incorrect_password(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # register test user
            reg_res = users_controller.register(self.COMBINE_DATA)
            # check registerd ok
            self.assertEqual(reg_res.status_code, 201)
            # attemp login wrong PW
            login_res = users_controller.login({
                'id': 1111111,
                'username': 'username1',
                'password': 'some-wrong-password'
            })
            # check login fails
            self.assertFalse(login_res)
            db.session.remove()
            db.drop_all()

    # tests login overall login funcionality inc authorization
    def test_login_success_w_password_username(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # register test user
            reg_res = users_controller.register(self.COMBINE_DATA)
            # check registerd ok
            self.assertEqual(reg_res.status_code, 201)
            # attempt login
            login_res = users_controller.login(self.COMBINE_DATA)
            self.assertEqual(json.loads(login_res.data)['status'], 'success')
            self.assertEqual(json.loads(login_res.data)
                             ['message'], 'logged in')
            self.assertEqual(login_res.status_code, 200)
            db.session.remove()
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
