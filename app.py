import os
import psycopg2
import scraper
import flask
from flask_login import current_user, login_required
from controllers import drivers_controller, teams_controller, users_controller
from flask import request, jsonify, Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate


class App:

    def create_app(self):
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
            app.testing = True
            app.secret_key = b'12345678910-not-my-real-key'
            if os.environ['LOGS'] != 'off':
                print('app.py: testing DB')
            app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
            engine = create_engine('sqlite:///:memory:')
        db = SQLAlchemy(app)
        app.db = db
        return {
            'app': app,
            'db': db
        }


# if os.environ['FLASK_ENV'] != 'dev_testing':
a = App()
app = a.create_app()['app']
db = a.create_app()['db']
migrate = Migrate(app, db)

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


@app.route('/test', methods=['GET', 'POST'])
def testing_route():
    print('HELLO')
    return 'hello'
    # res = make_response()
    # return res


@app.route('/test-login', methods=['GET', 'POST'])
@login_required
def testing_login():
    print('+++current user++++', current_user.username)
    res = make_response()
    res.status_code = 200
    return 'Okay'


@app.route('/drivers')
def all_drivers():
    print(request.url)
    return jsonify(drivers_controller.show_all_drivers())


@app.route('/drivers-test', methods=['GET'])
def testing_route2():

    return "test"
    # res = make_response()
    # return res


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
    scraper.driver_scraper()
    return 'Complete\n'


@app.route('/teams/scrape-teams')
def scrape_teams():
    scraper.team_scraper()
    return 'Complete\n'


@app.route('/scrape-all')
def all():
    scraper.main()
    return 'Complete\n'


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            print('GET')
            return flask.render_template('login.jinja')
        # print('REQ+++', request.data)
         # hardcode ID for now - format for browser test
        # parsedJsonCredentials = {
        #     'id': 1234567891012983,
        #     'username': request.form.get('username'),
        #     'password': request.form.get('password')
        # }
        parsedJsonCredentials = request.get_json()
        # print('PARSE', parsedJsonCredentials)
        # error if not json
        if not parsedJsonCredentials:
            print('Error in /login json')
            return TypeError('Error in /login json. Must be json.')
        return users_controller.login(parsedJsonCredentials)
    except Exception as e:
        print('error in login route', e)
        return e


@app.route('/register', methods=['POST'])
def register():
    parsedData = request.get_json()
    # print('parsed', parsedData)
    if not request.is_json or not parsedData:
        print('Error in /login json')
        return TypeError('Error in /register json. Must be json.')
    # print('RES', users_controller.register(parsedData))
    return users_controller.register(parsedData)


@app.route('/user-status')
def status():
    auth_header = request.headers.get('Authorization')
    return users_controller.status(auth_header)


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
