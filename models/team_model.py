from database import db
from sqlalchemy import text
from slugify import slugify


class Team(db.model):
    id = db.Column(db.Integer, primary_key=True)
    full_team_name = db.Column(db.String(100), nullable=False, unique=True),
    team_slug = db.Column(db.string(100), unique=True),
    base = db.Column(db.string(100)),
    team_chief = db.Column(db.string(100)),
    technical_chief = db.Column(db.string(100)),
    power_unit = db.Column(db.string(50)),
    first_team_entry = db.Column(db.string(25)),
    highest_race_finish = db.Column(db.string(25)),
    pole_positions = db.Column(db.string(25)),
    fastest_lap = db.Column(db.string(25))
