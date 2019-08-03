from flask import Flask
import unittest
# don't pass in the app object yet
from database import db
from utilities.scraper import driver_scraper


class TestStringMethods(unittest.TestCase):
    def create_test_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/f1"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        # Dynamically bind SQLAlchemy to application
        db.init_app(app)
        app.app_context().push()  # this does the binding
        return app

    def test_scraper(self):
        res = driver_scraper.get_main_image("lewis-hamilton")
        print(res)


if __name__ == '__main__':
    unittest.main()
