import os
from database import db
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


class Driver(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # full name with spaces
    driver_name = db.Column(db.String(80), nullable=False)
    # slug with hyphens
    name_slug = db.Column(db.String(80), unique=True, nullable=False)
    # name of team - string with spaces
    team = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(100))
    podiums = db.Column(db.String(10))
    points = db.Column(db.String(10))
    driver_number = db.Column(db.String(10))
    flag_img_url = db.Column(db.String(150))
    main_image = db.Column(db.String(150))
    points = db.Column(db.String(10))
    grands_prix_entered = db.Column(db.String(10))
    world_championships = db.Column(db.String(10))
    highest_race_finish = db.Column(db.String(10))
    highest_grid_position = db.Column(db.String(10))
    date_of_birth = db.Column(db.String(20))
    place_of_birth = db.Column(db.String(50))
    standings_position = db.Column(db.String(10))
    # url name with underscores
    team_name_slug = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'team.id',  ondelete="CASCADE"), nullable=False)
    # fix FK error in migrate
    # https://stackoverflow.com/a/52334988/5972531

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
                print('CREATE DRIVER', scraper_dict)
            db.create_all()
            d = cls()
            d.driver_name = scraper_dict.get('driver_name')
            d.name_slug = slugify(d.driver_name).lower()
            # short version with spaces
            d.team = scraper_dict.get('team')
            # url name with underscores
            d.team_name_slug = _slugify(d.team)
            # ForeignKey
            d.team_id = scraper_dict.get('team_id')
            d.country = scraper_dict.get('country')
            d.podiums = scraper_dict.get('podiums')
            d.points = scraper_dict.get('points')
            d.grands_prix_entered = scraper_dict.get('grands_prix_entered')
            d.world_championships = scraper_dict.get('world_championships')
            d.highest_race_finish = scraper_dict.get('highest_race_finish')
            d.highest_grid_position = scraper_dict.get('highest_grid_position')
            d.driver_number = scraper_dict.get('driver_number')
            d.date_of_birth = scraper_dict.get('date_of_birth')
            d.place_of_birth = scraper_dict.get('place_of_birth')
            d.flag_img_url = scraper_dict.get('flag_img_url')
            d.main_image = scraper_dict.get('main_image')
            d.standings_position = scraper_dict.get('standings_position')
            return d
        except Exception as e:
            print('Error in Driver new:', e)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            print('INSERT OKAY')
        except Exception as e:
            print('RollBack', e)
            db.session.rollback()

    def delete(self, driver_slug):
        d = self.query.filter_by(name_slug=driver_slug).first()
        try:
            db.session.delete(d)
            db.session.commit()
            print('DELETE OKAY')
        except Exception as e:
            print('Delete Error', e)

    def exists(self, driver_slug):
        try:
            print('driver_slug', driver_slug)
            if self.query.filter_by(name_slug=driver_slug).first():
                return True
            return False
        except Exception as e:
            print("Does not exist", e)
            return False

    def as_dict(req):
        return {c.name: getattr(req, c.name) for c in req.__table__.columns}
