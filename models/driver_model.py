from database import db
from sqlalchemy import text
from slugify import slugify, Slugify
_slugify = Slugify()
_slugify = Slugify(to_lower=True)
_slugify.separator = '_'


class Driver(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    # full name with spaces
    driver_name = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(100))
    # slug with hyphens
    name_slug = db.Column(db.String(80), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(20))
    driver_number = db.Column(db.String(10))
    place_of_birth = db.Column(db.String(50))
    flag_img_url = db.Column(db.String(150))
    main_image = db.Column(db.String(150))
    podiums = db.Column(db.String(10))
    points = db.Column(db.String(10))
    world_championships = db.Column(db.String(10))
    highest_grid_position = db.Column(db.String(10))
    points = db.Column(db.String(10))
    position = db.Column(db.String(10))
    # name of team - string with spaces
    team = db.Column(db.String(50), nullable=False)
    # url name with underscores
    team_name_slug = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'team.id'), nullable=False)

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
            print('CREATE', scraper_dict)
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
            d.highest_grid_position = scraper_dict.get('highest_grid_position')
            d.driver_name = scraper_dict.get('driver_name')
            d.date_of_birth = scraper_dict.get('date_of_birth')
            d.driver_number = scraper_dict.get('driver_number')
            d.place_of_birth = scraper_dict.get('place_of_birth')
            d.flag_img_url = scraper_dict.get('flag_img_url')
            d.main_image = scraper_dict.get('main_image')
            d.podiums = scraper_dict.get('podiums')
            d.points = scraper_dict.get('points')
            d.world_championships = scraper_dict.get('world_championships')
            d.points = scraper_dict.get('points')
            d.podiums = scraper_dict.get('podiums')
            d.position = scraper_dict.get('position')
            # print('DD', d)
            return d
        except Exception as e:
            print('New Error', e)

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
            print('SLUG', driver_slug)
            if self.query.filter_by(name_slug=driver_slug).first():
                return True
            return False
        except Exception as e:
            print("Does not exist", e)
            return False

    def as_dict(req):
        return {c.name: getattr(req, c.name) for c in req.__table__.columns}
