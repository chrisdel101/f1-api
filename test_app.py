import requests_mock
from flask import Flask
import unittest
# don't pass in the app object yet
from database import db
from utilities.scraper import driver_scraper, team_scraper
from utilities import utils
from bs4 import BeautifulSoup


@unittest.skip("showing class skipping")
class TestDriverScraper(unittest.TestCase):
    def create_test_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/f1"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        # Dynamically bind SQLAlchemy to application
        db.init_app(app)
        app.app_context().push()  # this does the binding
        return app

    def test_change_driver_image_size(self):
        res = driver_scraper._change_driver_img_size(
            "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.320.medium.jpg/1554818962683.jpg", 2)
        self.assertEqual(
            res, "/content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.768.medium.jpg/1554818962683.jpg")

    def test_scrape_all_driver_names(self):
        self.assertTrue(type(driver_scraper.scrape_all_driver_names()) == list)
        self.assertTrue(len(driver_scraper.scrape_all_driver_names()) >= 1)

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
        result = driver_scraper.get_complete_driver_data('sebastian-vettel')
        self.assertTrue(type(result) == dict)
        self.assertEqual(
            result['main_image'], 'https://www.formula1.com//content/fom-website/en/drivers/sebastian-vettel/_jcr_content/image.img.1536.medium.jpg/1554818962683.jpg')
        self.assertEqual(result['country'], 'Germany')


class TestTeamScraper(unittest.TestCase):
    def test_scrape_all_team_names(self):
        result = team_scraper.scrape_all_team_names()
        self.assertTrue(type(result) == list)
        self.assertTrue(len(result) >= 1)

    @unittest.skip
    def test_get_main_image(self):
        soup = team_scraper._team_page_scrape()
        # first one in list is currently Mercedes - will fail if markup changes
        li = soup.find('li', {'class', 'teamindex-teamteaser'})
        team_dict_no_image = {'full_team_name': 'ROKiT Williams Racing', 'base': 'Grove, United Kingdom', 'team_chief': 'Frank Williams', 'technical_chief': 'TBC', 'power_unit': 'Mercedes',
                              'first_team_entry': '1978', 'highest_race_finish': '1 (x114)', 'pole_positions': '129', 'fastest_laps': '133', 'name_slug': 'williams', 'url_name_slug': 'Williams'}
        team_dict_image = {'full_team_name': 'Mercedes AMG Petronas Motorsport', 'base': 'Brackley, United Kingdom', 'team_chief': 'Toto Wolff', 'technical_chief': 'James Allison', 'power_unit': 'Mercedes', 'first_team_entry': '1970', 'highest_race_finish':
                           '1 (x87)', 'pole_positions': '101', 'fastest_laps': '61', 'name_slug': 'mercedes', 'url_name_slug': 'Mercedes', 'main_image': 'https://www.formula1.com//content/fom-website/en/teams/Mercedes/_jcr_content/image16x9.img.1536.medium.jpg/1561122939027.jpg'}
        d2 = team_scraper.get_main_image(team_dict_image, li)
        self.assertTrue('main_image' in d2)
        d1 = team_scraper.get_main_image(team_dict_no_image, li)
        self.assertFalse('main_image' in d1)

    def test_get_driver_flag_url(self):
        soup = team_scraper._team_page_scrape()
        li = soup.find('li', {'class', 'teamindex-teamteaser'})
        team_dict1 = {'full_team_name': 'ROKiT Williams Racing', 'base': 'Grove, United Kingdom', 'team_chief': 'Frank Williams', 'technical_chief': 'TBC', 'power_unit': 'Mercedes',
                      'first_team_entry': '1978', 'highest_race_finish': '1 (x114)', 'pole_positions': '129', 'fastest_laps': '133', 'name_slug': 'williams', 'url_name_slug': 'Williams'}
        team_scraper.get_flag_img_url(team_dict1, li)


class TestUtils(unittest.TestCase):
    def test_create_url_slug_name(self):
        dic1 = {'name_slug': 'haas_f1_team', 'name': 'Haas_F1_Team'}
        dic2 = {'name_slug': 'alfa_romeo_racing', 'name': 'Alfa_Romeo_Racing'}
        url_slug1 = utils.create_url_name_slug(dic1)
        url_slug2 = utils.create_url_name_slug(dic2)
        self.assertEqual(url_slug1, 'Haas')
        self.assertEqual(url_slug2, 'Alfa-Romeo')


if __name__ == '__main__':
    unittest.main()
