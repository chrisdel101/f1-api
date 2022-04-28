from database import db
import os


class Team(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    full_team_name = db.Column(db.String(100), nullable=False, unique=True)
    # underscored name
    team_name_slug = db.Column(
        db.String(100), nullable=False, unique=True)
    # shorter version of full name
    team_name_header = db.Column(db.String(100))
    team_name = db.Column(db.String(100))
    base = db.Column(db.String(100))
    team_chief = db.Column(db.String(100))
    technical_chief = db.Column(db.String(100))
    power_unit = db.Column(db.String(50))
    first_team_entry = db.Column(db.String(25))
    highest_race_finish = db.Column(db.String(25))
    pole_positions = db.Column(db.String(25))
    fastest_laps = db.Column(db.String(25))
    main_image = db.Column(db.String(500))
    main_logo_url = db.Column(db.String(500))
    small_logo_url = db.Column(db.String(500))
    chassis = db.Column(db.String(25))
    championship_titles = db.Column(db.String(25))
    drivers_scraped = db.Column(db.PickleType)
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
            db.create_all()
            d = cls()
            d.team_name_slug = scraper_dict.get('team_name_slug')
            d.team_name_header = scraper_dict.get('team_name_header')
            d.full_team_name = scraper_dict.get('full_team_name')
            d.team_name = scraper_dict.get('team_name')
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
            d.main_logo_url = scraper_dict.get('main_logo_url')
            d.small_logo_url = scraper_dict.get('small_logo_url')
            d.chassis = scraper_dict.get('chassis')
            d.championship_titles = scraper_dict.get('world_championships')
            d.drivers_scraped = scraper_dict.get('drivers')
            if os.environ['LOGS'] != 'off':
                # if os.environ['FLASK_ENV'] == 'development' or os.environ['FLASK_ENV'] == 'prod_testing' or os.environ['FLASK_ENV'] == 'dev_testing':
                print('CREATED TEAM', d)

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
