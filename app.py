from controllers import drivers_controller, teams_controller, users_controller, session_controller
from utilities import scraper
from models import driver_model, team_model
from flask import request, jsonify, Response, render_template, Flask, session, make_response, escape
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import json
from utilities import utils
import scraper_runner
import os
import psycopg2
import json
from collections import namedtuple


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if os.environ['FLASK_ENV'] == 'production' or os.environ['FLASK_ENV'] == 'prod_testing':
        app.secret_key = bytes(os.environ['SECRET_KEY'], encoding='utf-8')
        # app.permanent_session_lifetime = timedelta(hours=24)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROD_DB')
        DATABASE_URL = app.config['SQLALCHEMY_DATABASE_URI']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        if os.environ['LOGS'] != 'off':
            print('app.py: Prod DB')
            print('connection', conn)
    elif os.environ['FLASK_ENV'] == 'development':
        app.secret_key = bytes(os.environ['SECRET_KEY'], encoding='utf-8')
        # app.permanent_session_lifetime = timedelta(hours=24)
        if os.environ['LOGS'] != 'off':
            print('app.py: dev DB')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DEV_DB']
    elif os.environ['FLASK_ENV'] == 'dev_testing':
        app.secret_key = b'12345678910-not-my-real-key'
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
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# runs before every req
if os.environ['AUTH'] != 'off':
    @app.before_request
    def check_incoming_authorization():
        # if no api_key return error
        print(request.headers)
        if request.headers.get("X-Api-Key") != os.environ['API_KEY']:
            print('Unauthourized')
            res = make_response()
            res.status_code = 401
            return res
        else:
            print('access okay')

if os.environ['FLASK_ENV'] == 'dev_testing':
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)
        print('session time')


@app.route('/test', methods=['GET', 'POST'])
def testing_route():
    return 'hello'
    # res = make_response()
    # print('res', res)
    # return res


@app.route('/test-logged-in', methods=['GET', 'POST'])
def testing_login():
    # pass
    # res = make_response()
    print('res', res)
    # return res


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


@app.route('/login', methods=['POST'])
def login():
    try:
        # print('REQ+++', request.data)
        parsedJsonCredentials = request.get_json()
        # print('below', request.data)
        # error if not json
        if not request.is_json or not parsedJsonCredentials:
            print('Error in /login json')
            return TypeError('Error in /login json. Must be json.')
        if parsedJsonCredentials['username'] in session:
            print('Logged in as %s' %
                  escape(session[parsedJsonCredentials['username']]))
            return 'Logged in as %s' % escape(session[parsedJsonCredentials['username']])
        else:
            print('bottom', request.data)
            return session_controller.login(session, parsedJsonCredentials)
    except Exception as e:
        print('error in login route', e)
        return e


@app.route('/register', methods=['POST'])
def register():
    parsedData = request.get_json(force=True)
    if not request.is_json or not parsedData:
        print('Error in /login json')
        return TypeError('Error in /register json. Must be json.')
    return users_controller.register_user(parsedData)


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
