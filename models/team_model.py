from database import db
from sqlalchemy import text
from .driver_model import Driver
from slugify import slugify, Slugify
import os
_slugify = Slugify()
_slugify = Slugify(to_lower=True)


class Team(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    full_team_name = db.Column(db.String(100), nullable=False, unique=True)
    # underscored name
    team_name_slug = db.Column(
        db.String(100), nullable=False, unique=True)
    # name with hypens for urls
    url_name_slug = db.Column(db.String(100))
    base = db.Column(db.String(100))
    team_chief = db.Column(db.String(100))
    technical_chief = db.Column(db.String(100))
    power_unit = db.Column(db.String(50))
    first_team_entry = db.Column(db.String(25))
    highest_race_finish = db.Column(db.String(25))
    pole_positions = db.Column(db.String(25))
    fastest_laps = db.Column(db.String(25))
    main_image = db.Column(db.String(200))
    flag_img_url = db.Column(db.String(200))
    logo_url = db.Column(db.String(200))
    podium_finishes = db.Column(db.String(25))
    championship_titles = db.Column(db.String(25))
    drivers_scraped = db.Column(db.PickleType)
    # drivers_list = db.relationship(
    #     'Driver', backref='team_name', lazy=True)

#   https://stackoverflow.com/a/44595303/5972531
    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v)
                           for k, v in self.__dict__.items()),
        )

    @classmethod
    def new(cls, scraper_dict):
        try:
            if os.environ['LOGS'] != 'off':
                # if os.environ['FLASK_ENV'] == 'development' or os.environ['FLASK_ENV'] == 'prod_testing' or os.environ['FLASK_ENV'] == 'dev_testing':
                print('CREATE TEAM', scraper_dict)
            db.create_all()
            d = cls()
            d.team_name_slug = scraper_dict.get('team_name_slug')
            d.url_name_slug = scraper_dict.get('url_name_slug')
            d.full_team_name = scraper_dict.get('full_team_name')
            d.base = scraper_dict.get('base')
            d.highest_grid_position = scraper_dict.get('highest_grid_position')
            d.team_chief = scraper_dict.get('team_chief')
            d.technical_chief = scraper_dict.get('technical_chief')
            d.power_unit = scraper_dict.get('power_unit')
            d.first_team_entry = scraper_dict.get('first_team_entry')
            d.highest_race_finish = scraper_dict.get('highest_race_finish')
            d.pole_positions = scraper_dict.get('pole_positions')
            d.fastest_laps = scraper_dict.get('fastest_laps')
            d.main_image = scraper_dict.get('main_image')
            d.flag_img_url = scraper_dict.get('flag_img_url')
            d.logo_url = scraper_dict.get('logo_url')
            d.podium_finishes = scraper_dict.get('podium_finishes')
            d.championship_titles = scraper_dict.get('championship_titles')
            d.drivers_scraped = scraper_dict.get('drivers')
            return d

        except Exception as e:
            print('Create error', e)

    def add_drivers(self, drivers_list):
        # loop over and find matching team slug
        for driver in drivers:
            print(driver)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            print('INSERT OKAY')
        except Exception as e:
            print('RollBack', e)
            db.session.rollback()

    def delete(self, team_name_slug):
        d = self.query.filter_by(team_name_slug=team_name_slug).first()
        try:
            db.session.delete(d)
            db.session.commit()
            print('DELETE OKAY')
        except Exception as e:
            print('Delete Error', e)

    def exists(self, team_name_slug):
        try:
            if self.query.filter_by(team_name_slug=team_name_slug).first():
                return True
            return False
        except Exception as e:
            print("Does not exist", e)
            return False

    def as_dict(req):
        return {c.name: getattr(req, c.name) for c in req.__table__.columns}
