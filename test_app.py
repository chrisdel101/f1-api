from flask import Flask
import sqlite3
import os
import unittest
from flask_sqlalchemy import SQLAlchemy
from utilities.scraper import driver_scraper, team_scraper
import scraper_runner
from utilities import utils
from models import driver_model, team_model
from controllers import drivers_controller, teams_controller
from database import db
from dotenv import load_dotenv, find_dotenv
import psycopg2


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
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if os.environ['FLASK_ENV'] == 'development' or os.environ['FLASK_ENV'] == 'dev_testing':
            setup_testing_environment()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
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
        print('Error in create_real_app',e)

class TestDriverScraper(unittest.TestCase):

    def test_change_driver_image_size(self):
        res = driver_scraper._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 2)
        self.assertEqual(
            res, "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.768.medium.jpg/1554818962683.jpg")

    def test_scrape_all_driver_names(self):
        result=driver_scraper.scrape_all_driver_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    def test_scrape_all_driver_standings(self):
        result=driver_scraper.scrape_all_drivers_standings()
        self.assertTrue(type(result) is list)
        self.assertTrue(len(result) > 0)
        res1=result[0]
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
        result1=driver_scraper.scrape_driver_details_func1("alexander-albon")
        self.assertEqual(result1[1]['country'], 'Thailand')
        self.assertEqual(result1[1]['date_of_birth'], '23/03/1996')
        self.assertEqual(result1[1]['place_of_birth'], 'London, England')

    def test_check_any_new_driver_attrs(self):
        result1=driver_scraper.scrape_driver_details_func1("alexander-albon")
        try:
            self.assertTrue(len(result1[0]) == 0)
        except Exception as e:
            raise ValueError(
                "Unknown driver attributes added to driver markup.")

    def test_apply_scraper_func2_complete_driver(self):
        result1=driver_scraper.apply_scraper_func2_complete_driver(
            'sebastian-vettel', {
                'driver_name': 'Sebastian Vettel'
            })
        self.assertTrue(type(result1) == dict)
        self.assertTrue(
            'https://www.formula1.com//content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.1536.medium' in result1['main_image'])
        # test all manual additions
        result2=driver_scraper.apply_scraper_func2_complete_driver(
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
        result1=driver_scraper.apply_scraper_func1_complete_driver(
            'sebastian-vettel'
        )
        self.assertTrue(type(result1) == dict)
        self.assertEqual(result1['country'], 'Germany')
        # test all manual additions
        result2=driver_scraper.apply_scraper_func1_complete_driver(
            'romain-grosjean'
        )
        self.assertEqual(result2['country'], 'France')
        self.assertEqual(result2['date_of_birth'], '17/04/1986')


class TestTeamScraper(unittest.TestCase):

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

    def test_compare_current_to_stored_true(self):
        app = create_real_app()
        with app.app_context():
            # init db
            db.init_app(app)
            # look up first driver in db
            get_first_driver_sql = driver_model.Driver.query.all()[0]
            res = utils.compare_current_to_stored(
                get_first_driver_sql, driver_model.Driver)
            self.assertTrue(res)

    # new class contains none vals
    @unittest.skip
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

    @unittest.skip
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
# utiliy functions

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
        # should fail missing contstrainta
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

    def test_driver_new(self):
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
            team.insert()
            assert team not in db.session
            self.assertRaises(AssertionError, team.insert())
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

        
        # result = unittest.TestResult()
        # self.assertEqual(result.testsRun, 0 )
        # print('RES', result)
        

if __name__ == '__main__':
    unittest.main()
