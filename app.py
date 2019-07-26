from controllers import drivers_controller, teams_controller
import utils
from models import driver_model
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_pyfile("flask.cfg")
app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']
)

db = SQLAlchemy(app)

SQLALCHEMY_TRACK_MODIFICATIONS = False


@app.route('/drivers')
def all_drivers():
    data = drivers_controller.list_all_drivers()
    return jsonify(data)


@app.route('/drivers/<driver_slug>')
def driver(driver_slug):
    print("HELLLLIII")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    new_data = drivers_controller.driver_stats(driver_slug)
    db.create_all()
    __table_args__ = {'extend_existing': True}
    db.metadata.clear()
    if driver_model.Driver:
        print('ZZZ', driver_model.Driver.query.all())
        # look up by slug
        # slug = driver_model.Driver.query.filter_by(
        #     name_slug=driver_slug).first()
        # if slug:
        #     # convert to dict
        #     db_data = dict((col, getattr(slug, col))
        #                    for col in slug.__table__.columns.keys())
        #     # check if any values are changed
        #     changed_vals = utils.dict_compare_vals(new_data, db_data)
        #     print('XX', changed_vals)

        return 'Complete'

    # d = driver_model.Driver(
    #     driver_name=data['driver_name'],
    #     name_slug=data['driver_slug'],
    #     date_of_birth=data['date_of_birth'],
    #     driver_number=data['driver_number'],
    #     place_of_birth=data['place_of_birth'],
    #     flag_img_url=data['flag_img_url'],
    #     main_image=data['main_image'],
    #     podiums=data['podiums'],
    #     points=data['points'],
    #     world_championships=data['world_championships'],
    #     team=data['team']
    # )

    # db.session.add(d)
    # db.session.commit()

    return "hello"


@app.route('/teams')
def all_teams():
    return jsonify(teams_controller.list_all_teams())


@app.route('/teams/<team_slug>')
def team(team_slug):
    return jsonify(teams_controller.team_stats(team_slug))


if __name__ == '__main__':
    app.run(debug=True)
