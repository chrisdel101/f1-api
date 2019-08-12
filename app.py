from controllers import drivers_controller, teams_controller
from utilities import scraper
from models import driver_model, team_model
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db
import json
from utilities import utils
import scraper_runner


app = Flask(__name__)

app.config.from_pyfile("flask.cfg")
app.config.update(
    SQLALCHEMY_TRACK_MODIFICATIONS=app.config['SQLALCHEMY_TRACK_MODIFICATIONS'],
    SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']
)
db = SQLAlchemy(app)
with app.app_context():
    from models import *
migrate = Migrate(app, db)


@app.route('/drivers')
def all_drivers():
    return jsonify(drivers_controller.show_all_drivers())


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):
    return jsonify(drivers_controller.show_single_driver(driver_slug))


@app.route('/teams')
def all_teams():
    return jsonify(teams_controller.show_all_teams())


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(teams_controller.show_single_team(team_slug))


@app.route('/drivers/scrape-drivers')
def scrape_drivers():
    scraper_runner.scrape_drivers()
    return 'Complete\n'


@app.route('/teams/scrape-teams')
def scrape_teams():
    scraper_runner.scrape_teams()
    return 'Complete\n'


@app.route('/scrape-all')
def all():
    scrape_drivers.main()
    return 'Complete\n'


@app.route('/test')
def test():
    scraper_runner.tester()
    # print(scraper.driver_scraper.get_driver_flag('lewis-hamilton'))
    # print(scraper.driver_scraper.get_driver_flag('lewis-hamilton'))


if __name__ == '__main__':
    app.run(debug=True)
