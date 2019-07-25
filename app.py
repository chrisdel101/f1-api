from models import driver_model
from controllers import drivers_controller, teams_controller
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
    return jsonify(drivers_controller.driver_stats(driver_slug))


@app.route('/teams')
def all_teams():
    return jsonify(teams_controller.list_all_teams())


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(teams_controller.team_stats(team_slug))


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(20))
    place_of_birth = db.Column(db.String(50))
    # country = db.Column(db.string(50))
    # driver_number = db.Column(db.string(10))
    # flag_img_url = db.Column(db.string(150))
    # flag_img_url = db.Column(db.string(150))
    # podiums = db.Column(db.string(10))
    # points = db.Column(db.string(10))
    # world_championships = db.Column(db.string(10))
    # team = db.Column(db.string(50))

    def __repr__(self):
        return f"{self.name}"


if __name__ == '__main__':
    app.run(debug=True)
