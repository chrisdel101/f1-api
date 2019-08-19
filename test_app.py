from flask import Flask
import sqlite3
import unittest
from unittest import mock
from unittest.mock import patch
from flask_sqlalchemy import SQLAlchemy
from utilities.scraper import driver_scraper, team_scraper
import scraper_runner
from utilities import utils
from bs4 import BeautifulSoup
from models import driver_model, team_model
from flask_migrate import Migrate
from flask_testing import TestCase
from database import db


def get_team_list(team_name, soup):
    lis = soup.find_all('li')
    for li in lis:
        s = li.find('section')
        if s:
            if s.find('a') and s.find('a')['href']:
                if team_name in s.find('a')['href']:
                    return li


class TestDriverScraper(unittest.TestCase):

    def test_change_driver_image_size(self):
        res = driver_scraper._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 2)
        self.assertEqual(
            res, "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.768.medium.jpg/1554818962683.jpg")

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

    def test_scrape_driver_details(self):
        result1 = driver_scraper.scrape_driver_details("alexander-albon")
        self.assertEqual(result1[1]['country'], 'Thailand')
        self.assertEqual(result1[1]['date_of_birth'], '23/03/1996')
        self.assertEqual(result1[1]['place_of_birth'], 'London, England')

    def test_check_any_new_driver_attrs(self):
        result1 = driver_scraper.scrape_driver_details("alexander-albon")
        try:
            self.assertTrue(len(result1[0]) == 0)
        except Exception as e:
            raise ValueError(
                "Unknown driver attributes added to driver markup.")

    def test_check_complete_driver_data(self):
        result1 = driver_scraper.get_complete_driver_data('sebastian-vettel')
        self.assertTrue(type(result1) == dict)
        self.assertEqual(
            result1['main_image'], 'https://www.formula1.com//content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.1536.medium.jpg/1554818962683.jpg')
        self.assertEqual(result1['country'], 'Germany')
        # test all manual additions
        result2 = driver_scraper.get_complete_driver_data('romain-grosjean')
        self.assertEqual(
            result2['flag_img_url'], 'https://www.formula1.com//content/fom-website/en/drivers/romain-grosjean/_jcr_content/countryFlag.img.gif/1423762801429.gif')
        self.assertEqual(
            result2['main_image'], 'https://www.formula1.com//content/fom-website/en/drivers/romain-grosjean/_jcr_content/image.img.1536.medium.jpg/1554818978139.jpg')
        self.assertEqual(result2['driver_name'], 'Romain Grosjean')
        self.assertEqual(result2['driver_number'], '8')


# @unittest.skip
class TestTeamScraper(unittest.TestCase):
    # @unittest.skip
    def test_scrape_all_team_names(self):
        result = team_scraper.scrape_all_team_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    # @unittest.skip
    def test_get_main_image(self):
        soup = team_scraper._team_page_scrape()
        ferrariList = get_team_list('Ferrari', soup)
        ferrari_data = {
            'url_name_slug': "Ferrari",
        }
        team_scraper.get_main_image(
            ferrari_data, ferrariList, 'Ferrari')
        self.assertTrue('main_image' in ferrari_data)
        williamsList = get_team_list('Williams', soup)
        williams_data = {
            'url_name_slug': "Williams",
        }
        team_scraper.get_main_image(
            williams_data, williamsList, 'Williams')
        self.assertTrue('main_image' in williams_data)

    # @unittest.skip
    def test_get_driver_flag_url(self):
        soup = team_scraper._team_page_scrape()
        williamsList = get_team_list('Williams', soup)
        williams_dict = {
            'url_name_slug': 'Williams'
        }
        team_scraper.get_flag_img_url(williams_dict, williamsList, 'Williams')
        self.assertTrue('flag_img_url' in williams_dict)

    # @unittest.skip
    def test_get_logo_url(self):
        soup = team_scraper._team_page_scrape()
        haasList = get_team_list('Haas', soup)
        haas_data = {
            'url_name_slug': 'Haas'
        }
        team_scraper.get_logo_url(haas_data, haasList, 'Haas')
        self.assertTrue('logo_url' in haas_data)

    # @unittest.skip
    def test_get_championship_titles(self):
        soup = team_scraper._team_page_scrape()
        racingPointList = get_team_list('Racing-Point', soup)
        racing_point_data = {
            'url_name_slug': "Racing-Point",
        }
        team_scraper.get_championship_titles(
            racing_point_data, racingPointList, 'Racing-Point')
        self.assertTrue('championship_titles' in racing_point_data)
        MercedesList = get_team_list('Mercedes', soup)
        mercedes_data = {
            'url_name_slug': "Mercedes"
        }
        team_scraper.get_championship_titles(
            mercedes_data, MercedesList, 'Mercedes')
        self.assertTrue('championship_titles' in mercedes_data)

    # @unittest.skip
    def test_get_podium_finishes(self):
        soup = team_scraper._team_page_scrape()
        renaultList = get_team_list('Renault', soup)
        renault_data = {
            'url_name_slug': 'Haas'
        }
        team_scraper.get_podium_finishes(renault_data, renaultList, 'Haas')
        self.assertTrue('podium_finishes' in renault_data)


class TestUtils(unittest.TestCase):
    @unittest.skip
    def test_create_url_slug_name(self):
        dic1 = {'name_slug': 'haas_f1_team', 'name': 'Haas_F1_Team'}
        dic2 = {'name_slug': 'alfa_romeo_racing',
                'name': 'Alfa_Romeo_Racing'}
        url_slug1 = utils.create_url_name_slug(dic1)
        url_slug2 = utils.create_url_name_slug(dic2)
        self.assertEqual(url_slug1, 'Haas')
        self.assertEqual(url_slug2, 'Alfa-Romeo')


class TestScraperRunner(unittest.TestCase):
    @patch("scraper_runner.scrape_drivers")
    def test_scraper_drivers(self, mod1):
        scraper_runner.scrape_drivers()
        assert mod1 is scraper_runner.scrape_drivers
        assert mod1.called
        assert mod1.assert_called_once_with(1, 2, 3)


class TestDriverModel(unittest.TestCase):

    def create_test_app(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
        db = SQLAlchemy(app)
        # migrate = Migrate(app, db)
        return {
            'app': app,
            'db': db
        }

    def create_test_client(self):
            # creates a test client
        app = self.create_test_app()['app']
        app.testing = True
        return app.test_client()

    def test_one(self):
        client = self.create_test_client()
        rv = client.get('/drivers')
        print(rv)

    DATABASE = 'database.db'

    # def get_db():
    #     db = getattr(g, '_database', None)
    #     if db is None:
    #         db = g._database = sqlite3.connect(DATABASE)
    #     return db

    # @app.teardown_appcontext
    # def close_connection(exception):
    #     db = getattr(g, '_database', None)
    #     if db is not None:
    #         db.close()

    # def app_context(app, new_dict):
    #     print('dict', new_dict)
    #     with app.app_context():
    #         db = get_db
    #         driver = driver_model.Driver.new(new_dict)
    #         exists = driver.exists(new_dict['name_slug'])
    #         print('here', exists)
    #         if exists:
    #             driver.delete(new_dict['name_slug'])
    #         driver.insert()
    #         # driver.insert()
    #         # print(driver.query.all())

    # # run python file

    # def migrate()

    # def test_driver_new(self):
    #     dic = {
    #         "name_slug": "test_slug2",
    #         "driver_name": "Test Slug2"
    #     }
    #     app = create_test_app()['app']
    #     app.testing = True
    #     app_context(app, dic)


# @unittest.skip
class TestConfig(TestCase):
    print()
    # def create_app(self):
    #     # SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    #     # TESTING = True
    #     # db = SQLAlchemy(app)
    #     # migrate = Migrate(app, db)
    #     app = Flask(__name__)
    #     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    #     return app

    # def setUp(self):
    #     db.create_all()

    # print('DB', db)
    # def tearDown(self):

    #     db.session.remove()
    #     db.drop_all()


class SomeTest(unittest.TestCase):

    def test_driver_added_to_db(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
        with app.app_context():

            db.init_app(app)
            db.create_all()
            # db.drop_all()
            user = driver_model.Driver(
                driver_name="Test Driver", name_slug="test_driver")
            db.session.add(user)
            db.session.commit()

        # # this works
            assert user in db.session

            db.session.remove()
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
