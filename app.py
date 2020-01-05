import json
import os
import psycopg2
import scraper_runner
import flask
import loader
from flask_login import LoginManager, current_user, login_required, login_user
from controllers import drivers_controller, teams_controller, users_controller
from utilities import scraper
from models import driver_model, team_model, user_model
from flask import request, jsonify, Response, render_template, Flask, session, make_response, escape
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from utilities import utils


a = loader.App()
# print(vars(a))
app = a.create_app()['app']
db = a.create_app()['db']
# db = app.create_app()
migrate = Migrate(app, db)


# @login_manager.user_loader
# def load_user(user_id):
#     user = user_model.User.query.filter_by(
#         id=user_id).first()
#     print('USER_LOADER', user)
#     return user


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
        print('PARSE', parsedJsonCredentials)
        # error if not json
        if not parsedJsonCredentials:
            print('Error in /login json')
            return TypeError('Error in /login json. Must be json.')

        print('bottom', parsedJsonCredentials)
        users_controller.login(parsedJsonCredentials)
        return "complete\n"
    except Exception as e:
        print('error in login route', e)
        return e


@app.route('/register', methods=['POST'])
def register():
    parsedData = request.get_json(force=True)
    print(parsedData)
    if not request.is_json or not parsedData:
        print('Error in /login json')
        return TypeError('Error in /register json. Must be json.')
    return users_controller.register(parsedData)


@app.route('/user-status')
def status():
    auth_header = request.headers.get('Authorization')
    print('auth', auth_header)
    # return users_controller.status(auth_header)


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
