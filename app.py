from controllers import drivers_controller, teams_controller, users_controller
from utilities import scraper
from models import driver_model, team_model
from flask import request, jsonify, Response, render_template, Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from utilities import utils
import scraper_runner
import os
import psycopg2
import json
from collections import namedtuple
# import flask


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if os.environ['FLASK_ENV'] == 'production' or os.environ['FLASK_ENV'] == 'prod_testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROD_DB')
        DATABASE_URL = app.config['SQLALCHEMY_DATABASE_URI']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        if os.environ['LOGS'] != 'off':
            print('app.py: Prod DB')
            print('connection', conn)
    elif os.environ['FLASK_ENV'] == 'development':
        if os.environ['LOGS'] != 'off':
            print('app.py: dev DB')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DEV_DB']
    elif os.environ['FLASK_ENV'] == 'dev_testing':
        if os.environ['LOGS'] != 'off':
            print('app.py: testing DB')
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////test_db.db"
    db = SQLAlchemy(app)

    return {
        'app': app,
        'db': db
    }


app = create_app()['app']
db = create_app()['db']
migrate = Migrate(app, db)


# runs before every req
@app.before_request
def check_auth():
    # if no api_key return error
    print(request.headers)
    if request.headers.get("X-Api-Key") != os.environ['API_KEY']:
        print('Unauthourized')
        res = make_response()
        res.status_code = 401
        return res
    else:
        print('access okay')
        # run next func


@app.route('/test', methods=['GET', 'POST'])
def testing_route():
    print('HERE')
    res = make_response()
    print('res', res)
    return res


@app.route('/drivers')
def all_drivers():
    print(request.url)
    return jsonify(drivers_controller.show_all_drivers())


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):
    return jsonify(drivers_controller.show_single_driver(driver_slug))


@app.route('/teams')
def all_teams():
    return jsonify(teams_controller.show_all_teams())


# takes a slug or an id
@app.route('/teams/<team_indentifier>')
def team(team_indentifier):
    return jsonify(teams_controller.show_single_team(team_indentifier))


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


@app.route('/user', methods=['GET', 'POST'])
def udpate_user():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        print('req', request.data)
        # True needed - force byte array into a dict
        parsedJson = request.get_json(force=True)
        print('par', parsedJson)
        if os.environ['LOGS'] != 'off':
            print('parsedJson', parsedJson)
        if not parsedJson:
            raise TypeError(
                'Error in handle_user_data: input must be json')
        return users_controller.udpate_user_data(parsedJson)
    else:
        raise TypeError(
            'Error in handle_user_data: HTTP method type must be POST of GET')


if __name__ == '__main__':
    app.run(debug=True)
