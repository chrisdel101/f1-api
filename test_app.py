from flask import Flask, session, make_response 
import sqlite3
import flask
import os
from datetime import timedelta
import unittest
from flask_sqlalchemy import SQLAlchemy
from utilities.scraper import driver_scraper, team_scraper
import scraper_runner
from utilities import utils
from models import driver_model, team_model, user_model
from controllers import drivers_controller, teams_controller, session_controller, users_controller
from database import db
from dotenv import load_dotenv, find_dotenv
import psycopg2
import flask_login
from flask_login import current_user, login_manager, LoginManager, login_required


# https://stackoverflow.com/a/50536837/5972531
def setup_testing_environment():
    load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))


def get_team_list(team_name, soup):
    lis = soup.find_all('li')
    for li in lis:
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
        if os.environ['FLASK_ENV'] == 'development' or os.environ['FLASK_ENV'] == 'dev_testing':
            setup_testing_environment()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
         # @login_manager.user_loader
            # def load_user(user_id):
            #     user_id = str(SELF.ID).encode('utf-8')
            #     return user_model.User.get(self.ID)
            # query = user_model.User.query.filter_by(
            #         id=self.ID).first()
            # print('user', user.is_active())
            # print('current user', current_user)
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

class TestDriverScraper(unittest.TestCase):

    def test_change_driver_image_size_medium(self):
        res = driver_scraper._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 1)
        self.assertTrue('640' in res)

    def test_change_driver_image_size_small(self):
        res = driver_scraper._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 0)
        self.assertTrue('320' in res)

    def test_scrape_all_driver_names(self):
        result = driver_scraper.scrape_all_driver_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    def test_scrape_all_driver_standings(self):
        result = driver_scraper.scrape_all_drivers_standings()
        self.assertTrue(type(result) is list)
        self.assertTrue(len(result) > 0)
        res1 = result[0]
        self.assertTrue('points' in res1)
        self.assertTrue('position' in res1)
        self.assertEqual(res1['position'], '1')

    def test_get_main_image_url(self):
        self.assertEqual(
            driver_scraper.get_main_image("sergio-perez"), 'https://www.formula1.com//content/fom-website/en/drivers/sergio-perez/_jcr_content/image.img.1536.medium.jpg/1554818944774.jpg')
        self.assertRaises(TypeError, driver_scraper.get_main_image, 4)

    def test_get_driver_name(self):
        self.assertEqual(driver_scraper.get_driver_name(
            "alexander-albon"), "Alexander Albon")
        self.assertEqual(driver_scraper.get_driver_name(
            "lewis-hamilton"), "Lewis Hamilton")
        self.assertRaises(TypeError, driver_scraper.get_driver_name, 44)

    def test_get_driver_number(self):
        self.assertEqual(driver_scraper.get_driver_number(
            "valtteri-bottas"), "77")
        self.assertEqual(driver_scraper.get_driver_number(
            "lewis-hamilton"), "44")
        self.assertRaises(TypeError, driver_scraper.get_driver_number, True)

    def test_get_driver_flag_url(self):
        self.assertEqual(driver_scraper.get_driver_flag(
            "lance-stroll"), "https://www.formula1.com//content/fom-website/en/drivers/lance-stroll/_jcr_content/countryFlag.img.jpg/1422627083354.jpg")
        self.assertEqual(driver_scraper.get_driver_flag(
            "george-russell"), "https://www.formula1.com//content/fom-website/en/drivers/george-russell/_jcr_content/countryFlag.img.jpg/1422627084440.jpg")
        self.assertRaises(TypeError, driver_scraper.get_driver_number, 33)

    def scrape_driver_details_func1(self):
        result1 = driver_scraper.scrape_driver_details_func1("alexander-albon")
        self.assertEqual(result1[1]['country'], 'Thailand')
        self.assertEqual(result1[1]['date_of_birth'], '23/03/1996')
        self.assertEqual(result1[1]['place_of_birth'], 'London, England')

    def test_check_any_new_driver_attrs(self):
        result1 = driver_scraper.scrape_driver_details_func1("alexander-albon")
        try:
            self.assertTrue(len(result1[0]) == 0)
        except Exception as e:
            raise ValueError(
                "Unknown driver attributes added to driver markup.")

    def test_apply_scraper_func2_complete_driver(self):
        result1 = driver_scraper.apply_scraper_func2_complete_driver(
            'sebastian-vettel', {
                'driver_name': 'Sebastian Vettel'
            })
        self.assertTrue(type(result1) == dict)
        self.assertTrue(
            'https://www.formula1.com//content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.1536.medium' in result1['main_image'])
        # test all manual additions
        result2 = driver_scraper.apply_scraper_func2_complete_driver(
            'romain-grosjean', {
                'driver_name': 'Romain Grosjean'
            })
        self.assertTrue(
            'https://www.formula1.com//content/fom-website/en/drivers/romain-grosjean/_jcr_content/countryFlag.img.gif' in result2['flag_img_url'])
        self.assertTrue(
            'https://www.formula1.com//content/fom-website/en/drivers/romain-grosjean/_jcr_content/image.img.1536.medium' in result2['main_image'])
        self.assertEqual(result2['driver_name'], 'Romain Grosjean')
        self.assertEqual(result2['driver_number'], '8')

    def test_apply_scraper_func1_complete_driver(self):
        result1 = driver_scraper.apply_scraper_func1_complete_driver(
            'sebastian-vettel'
        )
        self.assertTrue(type(result1) == dict)
        self.assertEqual(result1['country'], 'Germany')
        # test all manual additions
        result2 = driver_scraper.apply_scraper_func1_complete_driver(
            'romain-grosjean'
        )
        self.assertEqual(result2['country'], 'France')
        self.assertEqual(result2['date_of_birth'], '17/04/1986')


class TestTeamScraper(unittest.TestCase):

    def test_change_team_image_size_medium(self):
            res = team_scraper._change_team_img_size(
                "/content/fom-website/en/teams/Mercedes/_jcr_content/image16x9.img.1536.medium.jpg/1561122939027.jpg", 1)
            self.assertTrue('640' in res)

    def test_change_team_image_size_large(self):
            res = team_scraper._change_team_img_size(
                "/content/fom-website/en/teams/Mercedes/_jcr_content/image16x9.img.1536.medium.jpg/1561122939027.jpg", 2)
            print(res)
            self.assertTrue('768' in res)

    def test_scrape_all_team_names(self):
        result=team_scraper.scrape_all_team_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    def test_get_main_image(self):
        soup=team_scraper._team_page_scrape()
        ferrariList=get_team_list('Ferrari', soup)
        ferrari_data={
            'url_name_slug': "Ferrari",
        }
        team_scraper.get_main_image(
            ferrari_data, ferrariList, 'Ferrari')
        self.assertTrue('main_image' in ferrari_data)
        williamsList=get_team_list('Williams', soup)
        williams_data={
            'url_name_slug': "Williams",
        }
        team_scraper.get_main_image(
            williams_data, williamsList, 'Williams')
        self.assertTrue('main_image' in williams_data)

    def test_get_driver_flag_url(self):
        soup=team_scraper._team_page_scrape()
        williamsList=get_team_list('Williams', soup)
        williams_dict={
            'url_name_slug': 'Williams'
        }
        team_scraper.get_flag_img_url(williams_dict, williamsList, 'Williams')
        self.assertTrue('flag_img_url' in williams_dict)

    def test_get_logo_url(self):
        soup = team_scraper._team_page_scrape()
        haasList = get_team_list('Haas', soup)
        haas_data = {
            'url_name_slug': 'Haas'
        }
        team_scraper.get_logo_url(haas_data, haasList, 'Haas')
        self.assertTrue('logo_url' in haas_data)

    def test_get_championship_titles(self):
        soup = team_scraper._team_page_scrape()
        racingPointList = get_team_list('Racing-Point', soup)
        racing_point_data = {
            'url_name_slug': "Racing-Point",
        }
        team_scraper.get_championship_titles(
            racing_point_data, racingPointList, 'Racing-Point')
        self.assertTrue('championship_titles' in racing_point_data)
        MercedesList=get_team_list('Mercedes', soup)
        mercedes_data={
            'url_name_slug': "Mercedes"
        }
        team_scraper.get_championship_titles(
            mercedes_data, MercedesList, 'Mercedes')
        self.assertTrue('championship_titles' in mercedes_data)

    def test_get_podium_finishes(self):
        soup=team_scraper._team_page_scrape()
        renaultList=get_team_list('Renault', soup)
        renault_data={
            'url_name_slug': 'Renault'
        }
        team_scraper.get_podium_finishes(renault_data, renaultList, 'Renault')
        self.assertTrue('podium_finishes' in renault_data)

    def test_get_drivers(self):
        soup = team_scraper._team_page_scrape()
        renaultList = get_team_list('Renault', soup)
        renault_data = {
            'url_name_slug': 'Renault'
        }
        team_scraper.get_drivers(renault_data, renaultList, 'Renault')

        expected = [{'driver_name': 'Nico  Hulkenberg', 'name_slug': 'nico-hulkenberg'},
                    {'driver_name': 'Daniel Ricciardo', 'name_slug': 'daniel-ricciardo'}]
        self.assertEqual(renault_data['drivers'], expected)


class TestUtils(unittest.TestCase):

    def test_create_url_slug_name(self):
        dic1 = {'name_slug': 'haas_f1_team', 'name': 'Haas_F1_Team'}
        dic2 = {'name_slug': 'alfa_romeo_racing',
                'name': 'Alfa_Romeo_Racing'}
        url_slug1 = utils.create_url_name_slug(dic1)
        url_slug2 = utils.create_url_name_slug(dic2)
        self.assertEqual(url_slug1, 'Haas')
        self.assertEqual(url_slug2, 'Alfa-Romeo')

    def test_create_driver_list(self):
        drivers = ['Nico  Hulkenberg', 'Daniel Ricciardo']
        expected = [{'driver_name': 'Nico  Hulkenberg', 'name_slug': 'nico-hulkenberg'},
                    {'driver_name': 'Daniel Ricciardo', 'name_slug': 'daniel-ricciardo'}]
        driver_list = utils.create_driver_list(drivers)
        self.assertEqual(driver_list, expected)

    @unittest.skip('need to redo with a DB with instances inside - currently just returns true')
    def test_compare_current_to_stored_true(self):
        app = create_real_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # look up first driver in db
            get_first_driver_sql = driver_model.Driver.query.all()
            print('get',get_first_driver_sql)
            res = utils.compare_current_to_stored(
                get_first_driver_sql, driver_model.Driver)
            print('res',res)
            self.assertTrue(res)

    @unittest.skip(' # new class contains none vals')
    def test_compare_current_to_stored_false(self):
        app = create_real_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create new instance with diff properties
            diff_class = driver_model.Driver.new({
                'driver_name': 'Lewis Hamilton',
                'country': 'United Kingdom',
                'driver_number': '11',
                'team': 'Mercedes'
            })
            res = utils.compare_current_to_stored(
                diff_class, driver_model.Driver)
            print('1', diff_class)
            print('2', driver_model.Driver)
            self.assertTrue(type(res) == dict)
            self.assertTrue(type(res) != bool)

    @unittest.skip('needs update')
    def test_log_None_values(self):
        app = create_real_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create new instance with diff properties
            diff_class = driver_model.Driver.new({
                'driver_name': 'Lewis Hamilton',
                'country': 'United Kingdom',
                'driver_number': '11',
                'team': 'Mercedes'
            })
            res = utils.compare_current_to_stored(
                diff_class, driver_model.Driver)
            # print('RES', res)
            utils.log_None_values(res)
    
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


class TestScraperRunner(unittest.TestCase):
    #    https://stackoverflow.com/questions/16051422/patch-patching-the-class-introduces-an-extra-parameter
    # https://stackoverflow.com/questions/42482021/how-to-mock-modelclass-query-filter-by-in-flask-sqlalchemy
    # @patch('models.team_model.Team', return_value="test_slug")
    # @patch('flask_sqlalchemy._QueryProperty.__get__')
    def test_driver_runner(self, *args):
        # create app instance
        app = create_test_app()
        # add to context
        with app.app_context():
            # init db
            db.init_app(app)
            scraper_runner.scrape_drivers()

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

            db.session.remove()
            db.drop_all()

    def test_team_runner(self):

        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            scraper_runner.scrape_teams()
            ferrari = team_model.Team.query.filter_by(
                team_name_slug='ferrari').first()
            haas = team_model.Team.query.filter_by(
                team_name_slug='haas_f1_team').first()

            self.assertTrue('Scuderia Ferrari' in ferrari.full_team_name,
                            )
            self.assertEqual(ferrari.base, 'Maranello, Italy')
            self.assertEqual(ferrari.power_unit, 'Ferrari')

            self.assertTrue('Haas F1 Team' in haas.full_team_name)
            self.assertEqual(haas.base, 'Kannapolis, United States')
            self.assertEqual(haas.power_unit, 'Ferrari')

            db.session.remove()
            db.drop_all()



    # make sure runners work together
    def test_all_runners(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            scraper_runner.scrape_drivers()
            scraper_runner.scrape_teams()
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
            ferrari = team_model.Team.query.filter_by(
                team_name_slug='ferrari').first()
            haas = team_model.Team.query.filter_by(
                team_name_slug='haas_f1_team').first()

            self.assertTrue('Scuderia Ferrari' in ferrari.full_team_name,
                            )
            self.assertEqual(ferrari.base, 'Maranello, Italy')
            self.assertEqual(ferrari.power_unit, 'Ferrari')

            self.assertTrue('Haas F1 Team' in haas.full_team_name)
            self.assertEqual(haas.base, 'Kannapolis, United States')
            self.assertEqual(haas.power_unit, 'Ferrari')

            db.session.remove()
            db.drop_all()

    @unittest.skip #need to rewrite - no nullable false to fail now
    # run witn fail flag set to true - test for correct DB action
    def test_driver_runner_failure(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            scraper_runner.scrape_drivers(True)
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
    @unittest.skip #rewrite needed 
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
                'team_id':t_id
            })
            driver.insert()
            d = driver_model.Driver.query.all()
            print(d[0].team_id)


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
            self.assertEqual(driver, 'No Driver with that name')

class TestUserController(unittest.TestCase):
    # DATA = {
    #     "driver_data": ["driver1", "driver2"],
    #     "team_data": ["team1", "team2"],
    #     "user_id": 2
    # }
    ID = 1111111111
    DATA = {
                "username":"username1",
                "password":"password1"
            }
    # test combination of user new/insert
    def test_register_user_success(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # register new user
            user = users_controller.register_user({
                'id':self.ID, 
                'username':self.DATA['username'],
                'password': self.DATA['password']
            })
            # confirm user exists
            exists = user.exists(user.id)
            self.assertTrue(exists)
            # and in db
            assert user in db.session
            db.session.remove()
            db.drop_all()

    # test error raised when no id
    def test_register_user_fail_id(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # raise error when ID is none
            self.assertRaises(ValueError,users_controller.register_user,{
                'id': None, 
                'username':self.DATA['username'],
                'password': self.DATA['password']
            })
            db.session.remove()
            db.drop_all()

    def test_register_user_fail_username(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            # raise error when username is none
            self.assertRaises(ValueError,users_controller.register_user,{
                'id': self.ID, 
                'username':None,
                'password': self.DATA['password']
            })
            db.session.remove()
            db.drop_all()

    def test_handle_user(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = users_controller.handle_user(self.DATA)
            self.assertEqual(user.driver_data, self.DATA['driver_data'] )
            self.assertEqual(user.id, self.DATA['id'] )
            assert user in db.session
             # drop db
            db.session.remove()
            db.drop_all()
    
    def test_filter_user_data_removed(self):
        keys_allowed = ['driver_data', 'team_data', 'user_id']
        data_copy = self.DATA.copy()
        # confirm not extract data
        self.assertNotIn('hello', data_copy)
        # check it was added okay
        data_copy['hello'] = 'hello'
        self.assertIn('hello', data_copy)
        # add new key to data
        print()
        new_data = users_controller._filter_user_data(data_copy, keys_allowed)
        self.assertNotIn('hello', new_data)

    def test_filter_user_data_added(self):
        keys_allowed = ['driver_data', 'team_data', 'user_id', 'hello']
        data_copy = self.DATA.copy()
        # confirm not extract data
        self.assertNotIn('hello', data_copy)
        # check it was added okay
        data_copy['hello'] = 'hello'
        self.assertIn('hello', data_copy)
        new_data = users_controller._filter_user_data(data_copy, keys_allowed)
        self.assertIn('hello', new_data)
    
class TestUserModel(unittest.TestCase):
    # --------- UTILS FUNCS
    ID = 1111111111
    DATA = {
                "username":"username1",
                "password":"password1"
            }
    
    def create_new_user_pass(self):
        user = user_model.User.new(self.ID,self.DATA)
        return user

    def create_new_user_fail(self,type_of_failure):
        if type_of_failure == 'username':
            return user_model.User  .new(self.ID,{
                'password': 'password123'
            })
        elif type_of_failure == 'password':
             return user_model.User.new(self.ID,{
                'username':'username123',
            })
        else:
            # default
            print('USER', user_model.User.new(None,{
                'username':'username1',
                'password':'password123'
            }))
            return user_model.User.new(None,{
                'username':'username1',
                'password':'password123'
            })
    # ------------ TESTS 
    # test user.new() - success
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
            self.assertRaises(ValueError,self.create_new_user_fail, 'id')
            db.session.remove()
            db.drop_all()

    def test_user_new_fail_no_username(self):
        app = create_test_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance w/o username
            self.assertRaises(ValueError,self.create_new_user_fail, 'username')
            db.session.remove()
            db.drop_all()

    def test_user_new_fail_no_password(self):
        app = create_test_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # create driver instance w/o password
            self.assertRaises(ValueError,self.create_new_user_fail, 'password')
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
                user1 = user_model.User.new(1,self.DATA)
                user1.insert()
                # check exists okay
                exists1 = user1.exists(user1.id)
                self.assertTrue(exists1)
                # create second user - same username
                user2 = user_model.User.new(2,self.DATA)
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
                'username':'username1',
                'password':'password123'
            })
            user2 = user_model.User.new(2, {
                'username':'username2',
                'password':'password123'
            })
            user3 = user_model.User.new(3, {
                'username':'username3',
                'password':'password123'
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
                "driver_data":['driver1', 'driver5', 'driver6', 'driver7'],
                "team_data":['team1', 'team5', 'team6', 'team7']
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

    def test_encode_auth_token(self):
        app = create_test_app()
        with app.app_context():
            db.init_app(app)
            user = self.create_new_user_pass()
            db.session.add(user)
            db.session.commit()
            auth_token = user.encode_auth_token(user.id)
            print(auth_token, 'AUTH')
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
            self.assertTrue(isinstance(auth_token, bytes))
            # should decode to user ID
            self.assertTrue(user_model.User.decode_auth_token(auth_token) == self.I)
            db.session.remove()
            db.drop_all()


class TestSessionController(unittest.TestCase):
    # use test_request_context https://flask.palletsprojects.com/en/1.1.x/quickstart/#context-locals
    ID = 1111111111
    DATA = {
                "username":"username1",
                "password":"password1"
            }
    COMBINE_DATA = DATA
    COMBINE_DATA['id'] = ID
    def create_test_user(self):
        return user_model.User.new(self.ID,self.DATA)   

    def test_login_fail_unregistered_user(self):
        app = create_test_app()
        with app.test_request_context('/login', method='POST'):
            db.init_app(app)
            logged_in = session_controller.login(session, self.COMBINE_DATA)
            self.assertFalse(logged_in)
            db.session.remove()
            db.drop_all()

    def test_login_fail_incorrect_password(self):
        app = create_test_app()
        with app.test_request_context('/login', method='POST'):
            db.init_app(app)
             # register test user
            is_registred = users_controller.register_user(self.COMBINE_DATA)
            # assert registered success
            self.assertTrue(is_registred)
            # attemp login wrong PW
            login = session_controller.login(session, {
                'id':1111111,
                'username':'username1',
                'password': 'some-wrong-password'
            })
            # check login fails
            self.assertFalse(login)
            db.session.remove()
            db.drop_all()

    def test_login_fail_incorrect_username(self):
        app = create_test_app()
        with app.test_request_context('/login', method='POST'):
            db.init_app(app)
             # register test user
            is_registred = users_controller.register_user(self.COMBINE_DATA)
            # assert registered success
            self.assertTrue(is_registred)
            # attemp login wrong username
            login = session_controller.login(session, {
                'id':1111111,
                'username':'username2',
                'password': 'some-password'
            })
            # check login fails
            self.assertFalse(login)
            db.session.remove()
            db.drop_all()
    # tests login overall login funcionality inc authorization
    def test_login_success_w_password_username(self):
        app = create_test_app()
        with app.test_request_context('/login', method='POST'):
            db.init_app(app)
            # register test user
            is_registred = users_controller.register_user(self.COMBINE_DATA)
            # assert registered success
            self.assertTrue(is_registred)
            # attempt login
            is_logged = session_controller.login(session, self.COMBINE_DATA)
            # assert login okay
            self.assertTrue(is_logged)
            db.session.remove()
            db.drop_all()

    def test_login_success_user_already_in_session(self):
        app = create_test_app()
        with app.test_request_context('/login', method='POST'):
            db.init_app(app)
            # register test user
            is_registred = users_controller.register_user(self.COMBINE_DATA)
            # assert registered success
            self.assertTrue(is_registred)
            # add user to session
            session[self.COMBINE_DATA['username']] = self.COMBINE_DATA['username']
            # attempt login with wrong password - tests it takes correct path inside func
            login = session_controller.login(session, {
                'id':1111111,
                'username':'username1',
                'password': 'some-wrong-password'
            })
            # assert login okay b/c of session
            self.assertTrue(login)
            db.session.remove()
            db.drop_all()
            
    def test_login_then_test_user_still_in_session(self):
        app = create_test_app()
        login_manager = LoginManager()
        login_manager.init_app(app)
        with app.test_request_context('/login', method='POST'):
            db.init_app(app)
            @login_manager.user_loader
            def load_user(user_id):
                user = user_model.User.query.filter_by(
                    id=user_id).first()
                print('QQQ', user)
                return user
            return
            # add route to hit
            @app.route('/test-login', methods=['GET', 'POST'])
                # @login_required
            def testing_route():
                print('+++current user++++', current_user.username)
                print('in session')
                res = make_response()
                res.status_code = 200
                return res
            # query = user_model.User.query.filter_by(
            #         id=self.ID).first()
            # print('user', user.is_active())
            
            # register test user
            is_registred = users_controller.register_user(self.COMBINE_DATA)
            # assert registered success
            self.assertTrue(is_registred)
            # login
            login = session_controller.login(self.COMBINE_DATA)
            # check login okay
            self.assertTrue(login)
            # self.assertEqual(current_user.username, self.DATA['username'])
            print('+++current user++++', current_user.username)
            # try to call route where login is neccessary
            with app.test_client() as c:
                response = c.get('/test-login')
                self.assertEqual(response.status_code, 200)
            db.session.remove()
            db.drop_all()


    

if __name__ == '__main__':
    unittest.main()

