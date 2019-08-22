from controllers import drivers_controller, teams_controller
from utilities import scraper
from models import driver_model, team_model
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from utilities import utils
import scraper_runner


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/f1"
    db = SQLAlchemy(app)
    return {
        'app': app,
        'db': db
    }


app = create_app()['app']
db = create_app()['db']
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
    scraper_runner.main()
    return 'Complete\n'


@app.route('/test')
def test():
    scraper_runner.tester()
    # print(scraper.driver_scraper.get_driver_flag('lewis-hamilton'))
    # print(scraper.driver_scraper.get_driver_flag('lewis-hamilton'))


if __name__ == '__main__':
    app.run(debug=True)
