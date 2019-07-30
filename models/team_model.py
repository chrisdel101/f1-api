from database import db
from sqlalchemy import text
from slugify import slugify


class Team(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    full_team_name = db.Column(db.String(100), nullable=False, unique=True)
    team_slug = db.Column(db.String(100), unique=True)
    base = db.Column(db.String(100))
    team_chief = db.Column(db.String(100))
    technical_chief = db.Column(db.String(100))
    power_unit = db.Column(db.String(50))
    first_team_entry = db.Column(db.String(25))
    highest_race_finish = db.Column(db.String(25))
    pole_positions = db.Column(db.String(25))
    fastest_lap = db.Column(db.String(25))

    def __repr__(self):
        return "{0}".format(self.full_team_name)

    @classmethod
    def new(cls, scraper_dict):
        try:
            print('CREATE', scraper_dict)
            db.create_all()
            d = cls()
            d.full_team_name = scraper_dict.get('full_team_name')
            d.name_slug = slugify(d.full_team_name).lower()
            d.base = scraper_dict.get('base')
            d.highest_grid_position = scraper_dict.get('highest_grid_position')
            d.team_chief = scraper_dict.get('team_chief')
            d.technical_chief = scraper_dict.get('technical_chief')
            d.power_unit = scraper_dict.get('power_unit')
            d.first_team_entry = scraper_dict.get('first_team_entry')
            d.highest_grid_position = scraper_dict.get('flag_img_url')
            d.pole_positions = scraper_dict.get('main_image')
            d.fastest_lap = scraper_dict.get('fastest_lap')
            d.points = scraper_dict.get('points')
            print('TEAMTEAM', d)
            return d

        except Exception as e:
            print('Create error', e)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            print('INSERT OKAY')
        except Exception as e:
            print('RollBack', e)
            db.session.rollback()

    def delete(self, team_slug):
        d = self.query.filter_by(name_slug=team_slug).first()
        try:
            db.session.delete(d)
            db.session.commit()
            print('DELETE OKAY')
        except Exception as e:
            print('Delete Error', e)

    def exists(self, team_slug):
        try:
            if self.query.filter_by(name_slug=team_slug).first():
                return True
            return False
        except Exception as e:
            print("Does not exist", e)
            return False

    def as_dict(req):
        return {c.name: getattr(req, c.name) for c in req.__table__.columns}
