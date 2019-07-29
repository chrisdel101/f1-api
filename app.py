from controllers import drivers_controller, teams_controller
from utilities import scraper
from models import driver_model
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db

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
    data = scraper.scrape_all_driver_names()
    return jsonify(data)


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):

    new_data = scraper.scrape_single_driver_stats(driver_slug)
    # print('new', new_data)
    d = driver_model.Driver.new(new_data)
    if d.exists(driver_slug):
        d.delete(driver_slug)
    d.insert()
    return "hello"


@app.route('/teams')
def all_teams():
    return jsonify(scraper.scrape_all_team_names())


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(scraper.scrape_single_team_stats(team_slug))


if __name__ == '__main__':
    app.run(debug=True)
