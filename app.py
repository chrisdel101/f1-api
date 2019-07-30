from controllers import drivers_controller, teams_controller
from utilities import scraper
from models import driver_model
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db
import json
from utilities import scraper_runner, utils

app = Flask(__name__)
# db.init_app(app)

app.config.from_pyfile("flask.cfg")
app.config.update(
    SQLALCHEMY_TRACK_MODIFICATIONS=app.config['SQLALCHEMY_TRACK_MODIFICATIONS'],
    SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/drivers')
def all_drivers():
    return jsonify(drivers_controller.show_all_drivers())


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):
    return jsonify(drivers_controller.show_single_driver(driver_slug))


@app.route('/teams')
def all_teams():
    x = teams_controller.show_all_teams()
    print(x)
    return "hello"


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(scraper.scrape_single_drvier_stats(team_slug))


@app.route('/scrape-drivers')
def test():
    scraper_runner.scrape_drivers()


@app.route('/scrape-drivers/<driver_slug>')
def test1(driver_slug):
    new_data = scraper.scrape_single_driver_stats(driver_slug)
    print('NEW', new_data)
    d = driver_model.Driver.new(new_data)
    if d.exists(driver_slug):
        d.delete(driver_slug)
    d.insert()
    return "hello"


@app.route('/scrape-teams')
def test2():
    new_data = scraper_runner.main()
    print('NEW', new_data)
    return "hello"


if __name__ == '__main__':
    app.run(debug=True)
