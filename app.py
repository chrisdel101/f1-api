from controllers import drivers_controller, teams_controller
from models import driver_model
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import jsonify

app = Flask(__name__)

app.config.from_pyfile("flask.cfg")
app.config.update(
    MAIL_SERVER=app.config['SQLALCHEMY_DATABASE_URI']
)

db = SQLAlchemy(app)


@app.route('/drivers')
def all_drivers():
    data = drivers_controller.list_all_drivers()
    return jsonify(data)


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):

    data = drivers_controller.driver_stats(driver_slug)
    print(data['driver_number'])

    __table_args__ = {'extend_existing': True}
    db.metadata.clear()

    d = driver_model.Driver(
        name=data['driver_name'],
        date_of_birth=data['date_of_birth'],
        driver_number=data['driver_number'],
        place_of_birth=data['place_of_birth'],
        flag_img_url=data['flag_img_url'],
        main_image=data['main_image'],
        podiums=data['podiums'],
        points=data['points'],
        world_championships=data['world_championships'],
        team=data['team']
    )
    # print('XXX', data['country'])
    db.session.add(d)
    db.session.commit()

    return "hello"


@app.route('/teams')
def all_teams():
    return jsonify(teams_controller.list_all_teams())


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(teams_controller.team_stats(team_slug))


if __name__ == '__main__':
    app.run(debug=True)
