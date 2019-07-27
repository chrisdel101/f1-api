from flask_sqlalchemy import SQLAlchemy
# from database import db
# from controllers import drivers_controller
import utils
from models import driver_model
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_migrate import Migrate

from flask import jsonify
from flask import Flask
app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_pyfile("flask.cfg")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# db.init_app(app)
migrate = Migrate(app, db)


@app.route('/drivers')
def all_drivers():
    data = drivers_controller.list_all_drivers()
    data = {
        'drivers': drivers_controller.list_all_drivers()
    }
    return jsonify(data)


@app.route('/drivers/<driver>')
def driver(driver):
    data = drivers_controller.driver_stats(driver)
    return jsonify(data)


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):

    new_data = drivers_controller.driver_stats(driver_slug)
    # if doesn't exist - create
    # if not driver_model.Driver.exists(driver_slug):
    driver_model.Driver.create(new_data)
    # else:
    # else update
    driver_model.Driver.update(new_data)
    return "hello"


@app.route('/teams')
def all_teams():
    return jsonify(teams_controller.list_all_teams())


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(teams_controller.team_stats(team_slug))


if __name__ == '__main__':
    app.run(debug=True)
