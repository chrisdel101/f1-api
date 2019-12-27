from flask import Flask
import sqlite3
import os
import unittest
from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.append(
    '/Users/chrisdielschnieder/desktop/code_work/formula1/f1Scraper/f1scraper-flask/utilities')
print(sys.path)
import utilities
# from importlib.machinery import SourceFileLoader
# driver_scraper = SourceFileLoader(
#     "utilities.scraper", "/Users/chrisdielschnieder/desktop/code_work/formula1/f1Scraper/f1scraper-flask/utilities/scraper/driver_scraper.py").load_module()
# from utilities.scraper import driver_scraper, team_scraper
# import scraper_runner
# from models import driver_model, team_model, user_model
# from controllers import drivers_controller, teams_controller, users_controller
# from database import db
# from dotenv import load_dotenv, find_dotenv
# import psycopg2



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
